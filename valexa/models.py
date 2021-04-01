from __future__ import annotations

import pandas as pd
import numpy as np
import copy
import statsmodels.formula.api as smf
import statsmodels.regression.linear_model as sm
from math import sqrt
from sympy import lambdify, solveset, S, simplify
from sympy.abc import x
from sympy.sets.sets import EmptySet
from patsy.highlevel import dmatrix

from warnings import warn
from typing import List, Dict, Union, Callable, Optional

from valexa.models_list import model_list
from valexa.dataobject import DataObject
from valexa.helper import roundsf

ModelInfo = Dict[str, Optional[str]]
FitInfo = Union[sm.RegressionResultsWrapper, Dict[int, sm.RegressionResultsWrapper]]


class ModelsManager:
    def __init__(self, models_source: str = "hardcoded"):
        self.available_models: Dict[str, Dict[str, str]] = self.get_available_models(
            models_source
        )
        self.models: Dict[str, ModelGenerator] = {}

    def initialize_models(self, models_name: Union[List, str] = None) -> ModelsManager:
        if models_name is not None:

            if type(models_name) == str:
                models_name = [models_name]

            for model in models_name:
                if self.get_model_info(model) is not None:
                    self.models[model] = ModelGenerator(
                        model, self.get_model_info(model)
                    )
        else:
            for model in self.available_models:
                self.models[model] = ModelGenerator(model, self.get_model_info(model))

        if len(self.models) == 0:
            warn("No model initialized")

        return self

    def modelize(self, model_name: str, model_data: DataObject, sigfig: int) -> Model:
        return self.models[model_name].calculate_model(model_data, sigfig)

    @staticmethod
    def get_available_models(
        models_source: str = "hardcoded",
    ) -> Dict[str, Dict[str, str]]:
        # TODO: Handle model through SQL or other database
        list_of_models: Union[Model, Dict[str, ModelInfo]] = {}

        if models_source == "hardcoded":
            list_of_models = model_list()

        return list_of_models

    def get_model_weight(self, model_name: str) -> Optional[str]:
        if model_name in self.available_models:
            return self.available_models[model_name]["weight"]
        else:
            warn(
                "Model name not found, try get_available_models() for a list of available models"
            )
            return None

    def get_model_formula(self, model_name: str) -> Optional[str]:
        if model_name in self.available_models:
            return self.available_models[model_name]["formula"]
        else:
            warn(
                "Model name not found, try get_available_models() for a list of available models"
            )
            return None

    def get_model_info(self, model_name: str) -> Optional[Dict[str, str]]:
        if model_name in self.available_models:
            return self.available_models[model_name]
        else:
            warn(
                "Model name not found, try get_available_models() for a list of available models"
            )
            return None

    def get_model_min_point(self, model_name: str) -> Optional[str]:
        if model_name in self.available_models:
            return self.available_models[model_name]["min_points"]
        else:
            warn(
                "Model name not found, try get_available_models() for a list of available models"
            )
            return None

    @property
    def number_of_models(self) -> int:
        return len(list(self.available_models.keys()))

    @property
    def initialized_models_list(self) -> List[str]:
        return list(self.models.keys())


class Model:
    def __init__(
        self,
        data: DataObject,
        model_formula: str,
        model_weight: str,
        model_name: str,
        sigfig: int,
    ):

        self.data: DataObject = copy.deepcopy(data)
        self.name = model_name
        self.formula: str = model_formula
        self.weight: str = model_weight
        self.root_function: Optional[Union[Callable, Dict[int, Callable]]] = None
        self.fit: Optional[FitInfo] = None
        self.sigfig: int = sigfig
        self.miller_lod = None
        if len(self.list_of_series("validation")) == len(
            self.list_of_series("calibration")
        ):
            self.multiple_calibration: bool = True
            self.fit = {}
            self.root_function = {}
            self.function_string = {}
            self.miller_lod = {}
            for series in self.list_of_series("calibration"):
                self.fit[series] = self.__get_model_fit(series)
                self.function_string[series] = self.__build_function_from_params(
                    self.fit[series]
                )
                self.root_function[series] = lambdify(x, self.function_string[series])
                self.miller_lod[series] = self.__get_miller_lod(
                    self.fit[series], self.root_function[series]
                )
        else:
            self.multiple_calibration: bool = False
            self.fit = self.__get_model_fit()
            self.function_string = self.__build_function_from_params(self.fit)
            self.root_function = lambdify(x, self.function_string)
            self.miller_lod = self.__get_miller_lod(self.fit, self.root_function)

        self.data.add_value(self.__get_model_roots(), "x_calc")
        self.rsquared: Optional[float] = None
        if self.multiple_calibration:
            self.rsquared = np.mean([s.rsquared for s in self.fit.values()])
        else:
            self.rsquared = self.fit.rsquared

    def __get_miller_lod(self, fit: FitInfo, function: callable) -> Optional[float]:
        if "Intercept" in fit.params:
            regression_intercept = (
                0 if fit.params["Intercept"] < 0 else fit.params["Intercept"]
            )
        else:
            regression_intercept = 0
        miller_lod_y = regression_intercept + 3 * sqrt(fit.mse_resid)
        miller_lod = solveset(function(x) - miller_lod_y, x, S.Reals)
        if type(miller_lod) != EmptySet:
            return list(miller_lod)[0]
        else:
            return None

    def __get_model_fit(
        self, series: Optional[int] = None
    ) -> sm.RegressionResultsWrapper:
        if series is None:
            calibration_data: pd.DataFrame = self.data.calibration_data
        else:
            calibration_data: pd.DataFrame = self.data.get_series(series, "calibration")
        return smf.wls(
            formula=self.formula,
            weights=dmatrix(self.weight, calibration_data),
            data=calibration_data,
        ).fit()

    def __sanitize_roots(self, root_set):
        if type(root_set) != EmptySet:
            return pd.DataFrame(root_set.evalf())
        else:
            return pd.DataFrame()

    def __get_model_roots(self, signal_data: str = "y") -> pd.Series:
        list_of_roots: List[Union[float, None]] = []
        for validation_value in self.data.validation_data.iterrows():
            root_value: pd.DataFrame = pd.DataFrame()
            if self.multiple_calibration:
                root_value = self.__sanitize_roots(
                    solveset(
                        self.root_function[validation_value[1]["Series"]](x)
                        - validation_value[1][signal_data],
                        x,
                        S.Reals,
                    )
                )
            else:
                root_value = self.__sanitize_roots(
                    solveset(
                        self.root_function(x) - validation_value[1][signal_data], x, S.Reals
                    )
                )
            if len(root_value) > 0:
                list_of_roots.append(roundsf(float(root_value[0][0]), self.sigfig))
            else:
                list_of_roots.append(None)
        return pd.Series(list_of_roots)

    def __build_function_from_params(self, fitted_function: FitInfo) -> str:
        function_string: str = ""
        params_items = fitted_function.params.items()
        for param, value in params_items:
            if param == "Intercept":
                function_string += "+" + str(roundsf(value, self.sigfig))
            elif param.startswith("I("):
                function_string += "+" + str(roundsf(value, self.sigfig)) + "*" + param[2:-1]
            else:
                function_string += "+" + str(roundsf(value, self.sigfig)) + "*" + param
        return str(simplify(function_string))

    def get_level(
        self, level: int, series_type: str = "validation"
    ) -> Optional[pd.DataFrame]:
        return self.data.get_level(level, series_type)

    def get_series(
        self, series: int, series_type: str = "validation"
    ) -> Optional[pd.DataFrame]:
        return self.data.get_series(series, series_type)

    @property
    def data_x_calc(self) -> Optional[pd.Series]:
        return self.data.data_x_calc

    def data_x(self, series_type: str = "validation") -> Optional[pd.Series]:
        return self.data.data_x(series_type)

    def data_y(self, series_type: str = "validation") -> Optional[pd.Series]:
        return self.data.data_y(series_type)

    def list_of_series(self, series_type: str = "validation") -> Optional[np.ndarray]:
        return self.data.list_of_series(series_type)

    def list_of_levels(self, series_type: str = "validation") -> Optional[np.ndarray]:
        return self.data.list_of_levels(series_type)

    def add_value(self, value: pd.Series, name: str) -> None:
        return self.data.add_value(value, name)

    def add_corrected_value_y(self, corrected_value: pd.Series) -> None:
        self.add_value(corrected_value, "y_corr")
        corrected_value = self.__get_model_roots("y_corr")
        return self.data.add_corrected_value(corrected_value)

    def add_corrected_value(self, corrected_value: pd.Series) -> None:
        return self.data.add_corrected_value(corrected_value)

    @property
    def validation_data(self) -> pd.DataFrame:
        return self.data.validation_data

    @property
    def calibration_data(self) -> pd.DataFrame:
        return self.data.calibration_data


class ModelGenerator:
    def __init__(self, model_name: str, model_info: Dict[str, Union[str, int]]):

        self.name: str = model_name
        self.formula: str = model_info["formula"]
        if model_info["weight"] is None:
            self.weight: str = "I(x/x) - 1"
        else:
            self.weight: str = "I(" + model_info["weight"] + ") - 1"
        self.min_points: int = model_info["min_points"]

    def calculate_model(self, data: DataObject, sigfig: int) -> Model:
        return Model(data, self.formula, self.weight, self.name, sigfig)
