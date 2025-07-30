import dask.array as dsa
import numpy as np
import pytest
import scipy.ndimage
import xarray as xr

from skimage.measure import label as label_np
from skimage.measure import regionprops

from ocetrac import Tracker, _apply_mask


@pytest.fixture
def example_data():
    x0 = [180, 225, 360, 80, 1, 360, 1]
    y0 = [0, 20, -50, 40, -50, 40, 40]
    sigma0 = [15, 25, 30, 10, 30, 15, 10]

    lon = np.arange(0, 360) + 0.5
    lat = np.arange(-90, 90) + 0.5
    x, y = np.meshgrid(lon, lat)
    timedim = "time"
    xdim = "lon"
    ydim = "lat"

    def make_blobs(x0, y0, sigma0):
        blob = np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * sigma0**2))
        return blob

    features = {}
    for i in range(len(x0)):
        features[i] = make_blobs(x0[i], y0[i], sigma0[i])

    first_image = features[0] + features[1] + features[3] - 0.5

    da = xr.DataArray(
        first_image[np.newaxis, :, :],
        dims=[timedim, ydim, xdim],
        coords={timedim: [1], ydim: lat, xdim: lon},
    )

    da_shift_01 = da.shift(lon=0, lat=-20, fill_value=-0.5)
    da_shift_02 = da.shift(lon=0, lat=-40, fill_value=-0.5) + (
        features[2] + features[4] + features[5] + features[6]
    )
    da_shift_03 = da.shift(lon=0, lat=-40, fill_value=-0.5) + (
        features[2] + features[5] + features[6]
    )

    Anom = xr.concat(
        (
            da,
            da_shift_01,
            da_shift_02,
            da_shift_03,
        ),
        dim="time",
    )

    Anom["time"] = np.arange(1, 5)
    Anom = Anom.where(Anom > 0, drop=False, other=0)

    mask = xr.DataArray(np.ones(Anom[0, :, :].shape), coords=Anom[0, :, :].coords)
    mask[60:90, 120:190] = 0

    return Anom, mask


@pytest.mark.parametrize("radius", [8, 10])
@pytest.mark.parametrize("min_size_quartile", [0.75, 0.80])
@pytest.mark.parametrize("timedim", ["time", "t", "months"])
@pytest.mark.parametrize("xdim", ["lon", "longitude", "whoo"])
@pytest.mark.parametrize("ydim", ["lat", "latitude", "whaa"])
@pytest.mark.parametrize("positive", [True, False])
def test_track(example_data, radius, min_size_quartile, timedim, xdim, ydim, positive):
    Anom, mask = example_data
    if positive == False:
        Anom = Anom * -1
    Anom = Anom.rename({"time": timedim, "lon": xdim, "lat": ydim})
    mask = mask.rename({"time": timedim, "lon": xdim, "lat": ydim})

    tracker = Tracker(
        Anom,
        mask,
        radius,
        min_size_quartile,
        timedim=timedim,
        xdim=xdim,
        ydim=ydim,
        positive=positive,
    )
    new_labels = tracker.track()
    assert (
        new_labels.attrs["percent area reject"]
        + new_labels.attrs["percent area accept"]
    ) == 1.0

    if positive == True:
        assert Anom.sum() >= 0

    if positive == False:
        assert Anom.sum() <= 0


def test_morphological_operations(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()

    assert (timedim, ydim, xdim) != Anom.expand_dims("level").dims
    assert isinstance(binary_images.data, dsa.Array)

    ocetrac_guess = Anom.where(binary_images == True, drop=False, other=np.nan)
    best_guess = Anom.where(Anom > 0, drop=False, other=np.nan)
    part = ocetrac_guess.isin(best_guess)
    whole = best_guess.isin(best_guess)

    print(part.sum().values / whole.sum().values * 10)

    assert part.sum().values / whole.sum().values * 100 >= 80
    assert part.sum().values == 26122


def test_apply_mask(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()
    mask = mask.broadcast_like(binary_images)
    binary_images_with_mask = _apply_mask(binary_images, mask)
    assert (binary_images_with_mask.where(mask == 0, drop=True) == 0).all()


def test_filter_area(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()
    binary_images_with_mask = _apply_mask(binary_images, mask)
    area, min_area, binary_labels, N_initial = tracker._filter_area(
        binary_images_with_mask
    )

    assert min_area == 2761.5
    assert N_initial.astype(int) == 15


def test_label_either(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()
    binary_images_with_mask = _apply_mask(binary_images, mask)
    labels, num = tracker._label_either(
        binary_images_with_mask, return_num=True, connectivity=3
    )

    assert labels[2, :, :].max() == 6.0
    assert all([i in labels[2, :, :] for i in range(0, 6)])


def test_wrap(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()
    binary_images_with_mask = _apply_mask(binary_images, mask)
    area, min_area, binary_labels, N_initial = tracker._filter_area(
        binary_images_with_mask
    )
    labels, num = tracker._label_either(
        binary_images_with_mask, return_num=True, connectivity=3
    )
    labels_wrapped, N_final = tracker._wrap(labels)

    assert N_final == 6


def test_nan_timestep(
    example_data,
    radius=8,
    min_size_quartile=0.75,
    timedim="time",
    xdim="lat",
    ydim="lon",
    positive=True,
):
    Anom, mask = example_data
    Anom.loc[{"time": 2}] = Anom.sel(time=2) * 0
    tracker = Tracker(
        Anom.chunk({"time": 1}),
        mask,
        radius,
        min_size_quartile,
        timedim,
        xdim,
        ydim,
        positive,
    )
    binary_images = tracker._morphological_operations()
    binary_images_with_mask = _apply_mask(binary_images, mask)
    area, min_area, binary_labels, N_initial = tracker._filter_area(
        binary_images_with_mask
    )
    # PR 33 fixes issue where a timestep with no objects resulted in
    # no labeled objects at all future timesteps.
    labels_in_time = binary_labels.max(("lat", "lon"))
    assert labels_in_time.sel(time=2) == 0
    assert labels_in_time.sel(time=3) != 0
