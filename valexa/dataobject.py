import pandas as pd
import numpy as np

from typing import Optional


class DataObject:
    def __init__(
        self, validation_data: pd.DataFrame, calibration_data: pd.DataFrame = None
    ):
        self.validation_data: pd.DataFrame = validation_data
        self.validation_first_level: int = min(self.validation_data["Level"].unique())
        self.validation_last_level: int = max(self.validation_data["Level"].unique())
        self.validation_levels: int = self.validation_data["Level"].nunique()
        self.validation_first_concentration: float = min(self.validation_data["x"])
        self.validation_last_concentration: float = max(self.validation_data["x"])

        self.calibration_data: Optional[pd.DataFrame] = calibration_data
        if self.calibration_data is not None:
            self.calibration_first_level: int = min(
                self.calibration_data["Level"].unique()
            )
            self.calibration_last_level: int = max(
                self.calibration_data["Level"].unique()
            )
            self.calibration_levels: int = self.calibration_data["Level"].nunique()
            self.calibration_first_concentration: float = min(
                self.calibration_data["x"]
            )
            self.calibration_last_concentration: float = max(self.calibration_data["x"])

    def add_calculated_value(self, calculated_value: pd.Series) -> None:
        calculated_value = calculated_value.to_frame("x_calc")
        self.validation_data = pd.concat(
            [self.validation_data, calculated_value], axis=1
        )

    def add_corrected_value(self, corrected_value: pd.Series) -> None:
        corrected_value = corrected_value.to_frame("x_calc")
        self.validation_data.rename(columns={"x_calc": "x_raw"}, inplace=True)
        self.validation_data = pd.concat(
            [self.validation_data, corrected_value], axis=1
        )

    def get_level(
        self, level: int, data_type: str = "validation"
    ) -> Optional[pd.DataFrame]:
        if data_type == "validation":
            return self.validation_data[self.validation_data["Level"] == level]
        elif data_type == "calibration":
            return self.calibration_data[self.calibration_data["Level"] == level]
        else:
            return None

    def get_serie(
        self, serie: int, serie_type: str = "validation"
    ) -> Optional[pd.DataFrame]:
        if serie_type == "validation":
            return self.validation_data[self.validation_data["Serie"] == serie]
        elif serie_type == "calibration":
            return self.calibration_data[self.calibration_data["Serie"] == serie]
        else:
            return None

    @property
    def data_x_calc(self) -> Optional[pd.Series]:
        if "x_calc" in self.validation_data:
            return self.validation_data["x_calc"]
        else:
            return self.validation_data["y"]

    def data_x(self, serie_type: str = "validation") -> Optional[pd.Series]:
        if serie_type == "validation":
            return self.validation_data["x"]
        elif serie_type == "calibration":
            return self.calibration_data["x"]
        else:
            return None

    def data_y(self, serie_type: str = "validation") -> Optional[pd.Series]:
        if serie_type == "validation":
            return self.validation_data["y"]
        elif serie_type == "calibration":
            return self.calibration_data["y"]
        else:
            return None

    def list_of_series(self, serie_type: str = "validation") -> Optional[np.ndarray]:
        if serie_type == "validation":
            return self.validation_data["Serie"].unique()
        elif serie_type == "calibration":
            return self.calibration_data["Serie"].unique()
        else:
            return None

    def list_of_levels(self, serie_type: str = "validation") -> Optional[np.ndarray]:
        if serie_type == "validation":
            return self.validation_data["Level"].unique()
        elif serie_type == "calibration":
            return self.calibration_data["Level"].unique()
        else:
            return None
