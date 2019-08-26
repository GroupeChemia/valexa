import os

import pytest

from valexa.core.xlsx import XlsxHandler


class TestXlsxHandler:
    @pytest.fixture(scope="class")
    def filename(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, "data/test.xlsx")

    @pytest.fixture(scope="class")
    def filename_empty(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, "data/empty.xlsx")

    def test_handle_xlsx_on_init(self, filename):
        xs = XlsxHandler(filename)

        assert xs.workbook

    def test_valid_xlsx_sheets(self, filename_empty):
        with pytest.raises(ValueError) as exception:
            xs = XlsxHandler(filename_empty)

        assert "Bad format " in str(exception.value)

    def test_get_calibration_data(self, filename):
        xs = XlsxHandler(filename)

        data = xs.get_calibration_data()

        assert data

    def test_get_validation_data(self, filename):
        xs = XlsxHandler(filename)

        data = xs.get_validation_data()

        assert data
