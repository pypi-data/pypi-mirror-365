# pylint: disable=protected-access,missing-function-docstring,missing-module-docstring
# pylint: disable=use-implicit-booleaness-not-comparison
import json
import math

import pytest
from odc.geo.geobox import GeoBox

from .types import (
    AuxBandMetadata,
    AuxDataSource,
    FixedCoord,
    RasterBandMetadata,
    RasterGroupMetadata,
    RasterLoadParams,
    RasterSource,
    norm_nodata,
    with_default,
)

gbox_4326 = GeoBox.from_bbox((103, -44, 169, -11), 4326, shape=200)
gbox_3857 = gbox_4326.to_crs(3857)


@pytest.mark.parametrize(
    "xx",
    [
        RasterLoadParams(),
        RasterSource("file:///tmp/x.tif"),
        RasterSource("file:///tmp/x.nc", subdataset="x"),
        RasterSource("x", meta=RasterBandMetadata("float32", -9999)),
        RasterSource("x", geobox=gbox_4326, meta=RasterBandMetadata("float32", -9999)),
        RasterSource("x", geobox=gbox_3857, meta=RasterBandMetadata("float32", -9999)),
        RasterGroupMetadata({}),
        RasterGroupMetadata(
            bands={("x", 1): RasterBandMetadata("float32", -9999)},
            aliases={"X": [("x", 1)]},
            extra_dims={"b": 3},
            extra_coords=[
                FixedCoord("b", ["a", "b", "c"]),
                FixedCoord("B", [1, 2, 3], dtype="int32", dim="b"),
            ],
        ),
    ],
)
def test_repr_json_smoke(xx) -> None:
    dd = xx._repr_json_()
    assert isinstance(dd, dict)
    assert json.dumps(dd)

    gbox = getattr(xx, "geobox", None)
    if gbox is not None:
        assert "crs" in dd
        assert "transform" in dd
        assert "shape" in dd
        assert dd["shape"] == list(gbox.shape.yx)
        assert dd["crs"] == str(gbox.crs)
        assert dd["transform"] == list(gbox.transform)[:6]

    meta = getattr(xx, "meta", None)
    if meta is not None:
        assert "data_type" in dd
        assert "nodata" in dd
        assert dd["data_type"] == meta.data_type
        assert dd["nodata"] == meta.nodata


def test_with_default() -> None:
    A = object()
    B = "B"
    assert with_default(None, A) is A
    assert with_default(A, B) is A
    assert with_default(A, B, A) is B
    assert with_default((), B, (), {}) is B


def test_raster_band() -> None:
    assert RasterBandMetadata("float32", -9999).nodata == -9999
    assert RasterBandMetadata().units == "1"
    assert RasterBandMetadata().unit == "1"
    assert RasterBandMetadata().ndim == 2
    assert RasterBandMetadata("float32").data_type == "float32"
    assert RasterBandMetadata("float32").dtype == "float32"
    assert RasterBandMetadata(dims=("y", "x", "B")).ydim == 0
    assert RasterBandMetadata(dims=("B", "y", "x")).ydim == 1
    assert RasterBandMetadata(dims=("B", "y", "x")).extra_dims == ("B",)
    assert RasterBandMetadata(dims=("B", "y", "x")).ndim == 3

    assert RasterBandMetadata().patch(nodata=-1).nodata == -1
    assert RasterBandMetadata(nodata=10).patch(nodata=-1).nodata == -1

    assert RasterBandMetadata(nodata=-9999).with_defaults(
        RasterBandMetadata(
            "float64",
            dims=("y", "x", "B"),
        ),
    ) == RasterBandMetadata(
        "float64",
        -9999,
        dims=("y", "x", "B"),
    )


def test_basics() -> None:
    assert RasterLoadParams().fill_value is None
    assert RasterLoadParams().dtype is None
    assert RasterLoadParams().resampling == "nearest"
    assert RasterLoadParams().patch(resampling="cubic").resampling == "cubic"

    assert RasterSource("").band == 1
    assert RasterSource("").patch(band=0).band == 0

    assert RasterGroupMetadata({}).extra_dims == {}
    assert RasterGroupMetadata({}).patch(extra_dims={"b": 3}).extra_dims == {"b": 3}


def test_norm_nodata() -> None:
    assert norm_nodata(None) is None
    assert norm_nodata(0) == 0
    assert isinstance(norm_nodata(0), (float, int))
    nan = norm_nodata("nan")
    assert nan is not None
    assert math.isnan(nan)


def test_raster_band_metadata_driver_data() -> None:
    """Test driver_data field in RasterBandMetadata."""
    # Test default value
    meta = RasterBandMetadata()
    assert meta.driver_data is None

    # Test with custom driver_data
    custom_data = {"key": "value", "nested": {"data": 123}}
    meta_with_data = RasterBandMetadata(driver_data=custom_data)
    assert meta_with_data.driver_data == custom_data

    # Test with different types of driver_data
    meta_int = RasterBandMetadata(driver_data=42)
    assert meta_int.driver_data == 42

    meta_str = RasterBandMetadata(driver_data="driver_specific_info")
    assert meta_str.driver_data == "driver_specific_info"

    meta_list = RasterBandMetadata(driver_data=[1, 2, 3])
    assert meta_list.driver_data == [1, 2, 3]

    # Test with_defaults method includes driver_data
    defaults = RasterBandMetadata(driver_data={"default": "data"})
    result = meta.with_defaults(defaults)
    assert result.driver_data == {"default": "data"}

    # Test that existing driver_data takes precedence
    existing_data = {"existing": "data"}
    meta_existing = RasterBandMetadata(driver_data=existing_data)
    result = meta_existing.with_defaults(defaults)
    assert result.driver_data == existing_data

    # Test JSON serialization
    json_repr = meta_with_data._repr_json_()
    assert "driver_data" in json_repr
    assert json_repr["driver_data"] == custom_data

    # Test JSON serialization with non-serializable data
    non_serializable = object()  # object is not JSON serializable
    meta_non_serializable = RasterBandMetadata(driver_data=non_serializable)
    json_repr = meta_non_serializable._repr_json_()
    assert "driver_data" in json_repr
    assert json_repr["driver_data"] == "SET, NOT JSON SERIALIZABLE"


def test_aux_band_metadata_driver_data() -> None:
    """Test driver_data field in AuxBandMetadata."""
    # Test default value
    meta = AuxBandMetadata()
    assert meta.driver_data is None

    # Test with custom driver_data
    custom_data = {"aux_key": "aux_value", "nested": {"aux_data": 456}}
    meta_with_data = AuxBandMetadata(driver_data=custom_data)
    assert meta_with_data.driver_data == custom_data

    # Test with different types of driver_data
    meta_int = AuxBandMetadata(driver_data=99)
    assert meta_int.driver_data == 99

    meta_str = AuxBandMetadata(driver_data="auxiliary_driver_info")
    assert meta_str.driver_data == "auxiliary_driver_info"

    meta_tuple = AuxBandMetadata(driver_data=(1, 2, 3))
    assert meta_tuple.driver_data == (1, 2, 3)

    # Test JSON serialization
    json_repr = meta_with_data._repr_json_()
    assert "driver_data" in json_repr
    assert json_repr["driver_data"] == custom_data

    # Test JSON serialization with non-serializable data
    non_serializable = object()  # object is not JSON serializable
    meta_non_serializable = AuxBandMetadata(driver_data=non_serializable)
    json_repr = meta_non_serializable._repr_json_()
    assert "driver_data" in json_repr
    assert json_repr["driver_data"] == "SET, NOT JSON SERIALIZABLE"


def test_driver_data_consistency() -> None:
    """Test that driver_data behaves consistently across different metadata types."""
    test_data = {"test": "data", "number": 42}

    # Test RasterBandMetadata
    raster_meta = RasterBandMetadata(driver_data=test_data)
    assert raster_meta.driver_data == test_data

    # Test AuxBandMetadata
    aux_meta = AuxBandMetadata(driver_data=test_data)
    assert aux_meta.driver_data == test_data

    # Test that they can be used in RasterSource and AuxDataSource
    raster_source = RasterSource("test.tif", driver_data=test_data)
    assert raster_source.driver_data == test_data

    aux_source = AuxDataSource("test.nc", driver_data=test_data)
    assert aux_source.driver_data == test_data


def test_driver_data_integration() -> None:
    """Test driver_data integration with existing functionality."""
    # Test with RasterGroupMetadata
    driver_data = {"compression": "lzw", "tilesize": 512}
    band_meta = RasterBandMetadata("float32", -9999, driver_data=driver_data)

    group_meta = RasterGroupMetadata({("test", 1): band_meta})

    # Verify the driver_data is preserved in the group
    stored_band_meta = group_meta.bands[("test", 1)]
    assert stored_band_meta.driver_data == driver_data

    # Test JSON serialization of the group
    json_repr = group_meta._repr_json_()
    band_json = json_repr["bands"]["test.1"]
    assert "driver_data" in band_json
    assert band_json["driver_data"] == driver_data


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (RasterGroupMetadata({}), RasterGroupMetadata({}), RasterGroupMetadata({})),
        (
            # a
            RasterGroupMetadata(
                bands={("a", 1): RasterBandMetadata("float32")},
                aliases={"A": [("a", 1)]},
            ),
            # b
            RasterGroupMetadata(
                bands={
                    ("b", 1): RasterBandMetadata("int16", -9999, dims=("y", "x", "w")),
                    ("b", 2): RasterBandMetadata("int16", -9999),
                },
                aliases={
                    "A": [("b", 2)],
                    "B": [("b", 1)],
                },
                extra_dims={"w": 3},
                extra_coords=(FixedCoord("w", ["a", "b", "c"]),),
            ),
            # expected
            RasterGroupMetadata(
                bands={
                    ("a", 1): RasterBandMetadata("float32"),
                    ("b", 1): RasterBandMetadata("int16", -9999, dims=("y", "x", "w")),
                    ("b", 2): RasterBandMetadata("int16", -9999),
                },
                aliases={"A": [("a", 1), ("b", 2)], "B": [("b", 1)]},
                extra_dims={"w": 3},
                extra_coords=(FixedCoord("w", ["a", "b", "c"]),),
            ),
        ),
    ],
)
def test_merge_metadata(a, b, expected) -> None:
    assert a.merge(b) == expected
    assert a.merge(a) == a
    assert b.merge(b) == b

    assert a.merge(a) is a
    assert b.merge(b) is b
