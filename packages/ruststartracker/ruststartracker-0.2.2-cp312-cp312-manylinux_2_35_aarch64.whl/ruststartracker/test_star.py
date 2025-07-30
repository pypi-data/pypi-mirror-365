import time

import numpy as np
import pytest
import scipy.spatial

import ruststartracker
import ruststartracker.star


def test_extract_observations():
    size_x, size_y = (40, 50)
    img = np.zeros((size_y, size_x), np.uint8)
    points = np.array([(3, 5), (23, 13)])
    for x, y in points:
        img[y - 1 : y + 3, x - 1 : x + 3] = 50
    centers, intensities = ruststartracker.star._extract_observations(img, threshold=30)
    np.testing.assert_almost_equal(centers, points + 0.5)
    np.testing.assert_almost_equal(intensities, 50 * 16)


@pytest.fixture
def setup():
    rng = np.random.default_rng(42)

    n_cat_stars = 2617

    vec = rng.normal(size=[n_cat_stars, 3]).astype(np.float32)
    vec /= np.linalg.norm(vec, axis=-1, keepdims=True)

    angle_threshold = np.radians(10)
    dotp = np.sum([0, 0, 1] * vec, axis=-1)
    threshold = np.cos(angle_threshold).item()
    obs = vec[dotp >= threshold]

    camera_params = ruststartracker.CameraParameters(
        np.array(
            (
                (4000, 0, 900),
                (0, 4000, 500),
                (0, 0, 1),
            ),
            dtype=np.float32,
        ),
        (1800, 1000),
        None,
    )

    pixel_in_frame = (camera_params.camera_matrix @ obs.T).T
    pixel_in_frame = pixel_in_frame[..., :2] / pixel_in_frame[..., 2:]

    size_x, size_y = camera_params.cam_resolution
    img = np.zeros((size_y, size_x), np.uint8)
    for x, y in pixel_in_frame.astype(int):
        image_patch = img[y - 1 : y + 2, x - 1 : x + 2]
        image_patch[:] = 50

    return img, vec, camera_params


def test_star_matcher_success(setup):
    img, vec, camera_params = setup

    rot = scipy.spatial.transform.Rotation.from_rotvec([1, 1, 1])
    vec = rot.inv().apply(vec)

    st = ruststartracker.StarTracker(
        vec,
        camera_params,
        inter_star_angle_tolerance=np.radians(0.1).item(),
        n_minimum_matches=6,
    )
    res = st.process_image(img)

    assert res is not None
    np.testing.assert_allclose(res.quat, rot.inv().as_quat(), rtol=0.001, atol=0.001)
    assert res.n_matches >= 4


def test_star_matcher_exhaust(setup):
    img, vec, camera_params = setup
    st = ruststartracker.StarTracker(
        vec,
        camera_params,
        inter_star_angle_tolerance=np.radians(0.001).item(),
        n_minimum_matches=500,
        timeout_secs=999.0,
    )
    with pytest.raises(ruststartracker.StarTrackerError, match="exhaust"):
        st.process_image(img)


def test_star_matcher_timout(setup):
    img, vec, camera_params = setup
    timeout = 0.2
    st = ruststartracker.StarTracker(
        vec,
        camera_params,
        inter_star_angle_tolerance=np.radians(0.1).item(),
        n_minimum_matches=500,
        timeout_secs=timeout,
    )
    t = time.monotonic()
    with pytest.raises(ruststartracker.StarTrackerError, match="Timeout reached"):
        st.process_image(img)
    passed_time = time.monotonic() - t
    assert passed_time > timeout


if __name__ == "__main__":
    pytest.main([__file__])
