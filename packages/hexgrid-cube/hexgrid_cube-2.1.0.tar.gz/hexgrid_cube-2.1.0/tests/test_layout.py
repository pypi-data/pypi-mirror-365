import pytest
from hexgrid_cube.layout import Layout
from hexgrid_cube.orientation import FLAT_TOP_ORIENTATION
from hexgrid_cube.point import Point
from hexgrid_cube.hex import Hex


@pytest.fixture
def flat_top_layout():
    return Layout(FLAT_TOP_ORIENTATION, Point(1, 1), Point(50, 50))


@pytest.fixture
def layout_origin():
    return Point(50, 50)


class TestLayout:

    def test_layout_instanced_from_tuples_fails(self, layout_origin):
        with pytest.raises(ValueError):
            Layout(FLAT_TOP_ORIENTATION, (1, 1), (0, 0))
        with pytest.raises(ValueError):
            Layout(FLAT_TOP_ORIENTATION, (1, 1), Point(0, 0))
        with pytest.raises(ValueError):
            Layout(FLAT_TOP_ORIENTATION, Point(1, 1), (0, 0))

    def test_to_pixel_hex_origin_equals_layout_origin(self, flat_top_layout, layout_origin):
        assert flat_top_layout.to_pixel(Hex(0, 0, 0)) == layout_origin

    def test_to_hex_layout_origin_equals_hex_origin(self, flat_top_layout, layout_origin):
        assert flat_top_layout.to_hex(layout_origin) == Hex(0, 0, 0)
