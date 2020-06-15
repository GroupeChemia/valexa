from __future__ import annotations
from typing import List, Dict, Optional, Union, Callable
import matplotlib.pyplot as plt
from warnings import warn

from scipy.stats import t
import shapely.geometry

import math
import numpy as np
import pandas as pd
import mpl_toolkits.axisartist as aa
import io

from . import models
from .dataobject import DataObject

OptimizerParams = Dict[str, Union[str, bool]]


class ProfileManager:
    def __init__(
        self,
        compound_name: str,
        data: Dict[str, pd.DataFrame],
        tolerance_limit: float = 80,
        acceptance_limit: float = 20,
        absolute_acceptance: bool = False,
        quantity_units: str = None,
        rolling_data: bool = False,
        rolling_data_limit: int = 3,
        model_to_test: Union[List[str], str] = None,
        generate_figure: bool = False,
        allow_correction: bool = False,
        correction_threshold: Optional[List[float]] = None,
        forced_correction_value: Optional[float] = None,
        optimizer_parameter: Optional[OptimizerParams] = None,
    ):
        """
        Init ProfileManager with the necessary data
        :param compound_name: This is the name of the compounds for the profile
        :param data: These are the data in the form of a Dictionnary containing a DataFrame. The format should be
        {"Validation": DataFrame, "Calibration": DataFrame}. Note that the calibration data are optional.
        :param tolerance_limit: (Optional) The tolerance limit (beta). Default = 80
        :param acceptance_limit: (Optional) The acceptance limit (lambda). Default = 20
        :param absolute_acceptance: (Optional) If True, the acceptance will be considered to be in absolute unit instead
        of percentage. Default = False
        :param quantity_units: (Optional) The units (%, mg/l, ppm, ...) of the introduced data. This is only to
        ease the reading of the output.
        :param rolling_data: (Optional) If this is set to True, the system will do multiple iteration with the data and
        generate multiple profile with each subset of data.
        :param rolling_data_limit: (Optional) In combination with rolling_data, this is the minimum lenght of the subset
        that rolling_data will go to. Default = 3.
        :param model_to_test: (Optional) A list of model to test, if not set the system will test them all.
        :param generate_figure: (Optional) Generate a plot of the profile.
        :param allow_correction: (Optional) If set to true, the model will be multiplied by a factor to bring the
        recovery close to 1.
        :param correction_threshold: (Optional) If allow_correction is set to True, these will overwrite the default
        correction threshold (0.9 - 1.1). Setting this to [1,1] will force a correction to be calculated. The
        correction_threshold is calculated by calculating the average recovery ratio.. If the ratio is outside the
        indicated range, a correction will be applied.
        :param forced_correction_value: (Optional) If allow_correction is set to True, this will set the correction
        value to the indicated value instead of calculating it. Note: the value of the average recovery ratio must still
        be outside the threshold for this to take effect.
        :param optimizer_parameter: (Optional) These are the value used to sort the profile from best to worst when
        using the optimizer.
        """
        self.compound_name: str = compound_name
        self.quantity_units: str = quantity_units
        self.stats_limits: Dict[str, float] = {
            "Tolerance": tolerance_limit,
            "Acceptance": acceptance_limit,
        }
        self.tolerance_limit: float = tolerance_limit
        self.acceptance_limit: float = acceptance_limit
        self.absolute_acceptance: bool = absolute_acceptance
        self.data: Dict[str, pd.DataFrame] = data
        self.rolling_data: bool = rolling_data
        if type(model_to_test) == str:
            model_to_test = [model_to_test]
        self.model_to_test: List[str] = model_to_test
        self.rolling_data_limit: int = rolling_data_limit
        self.generate_figure: bool = generate_figure
        self.allow_correction: bool = allow_correction
        if allow_correction:
            if correction_threshold is None:
                correction_threshold = [0.9, 1.1]
            self.correction_threshold: Optional[List[float]] = correction_threshold
            self.forced_correction_value = forced_correction_value
        else:
            self.correction_threshold: Optional[List[float]] = None
            self.forced_correction_value = None

        self.optimizer_parameters: Optional[OptimizerParams] = optimizer_parameter

        if "Calibration" in self.data:
            self.model_manager: models.ModelsManager = models.ModelsManager()
            self.model_manager.initialize_models(self.model_to_test)

        self.data_objects: List[DataObject] = self.__get_dataobject
        self.profiles: Optional[Dict[str, Profile]] = None
        self.sorted_profiles: Optional[pd.DataFrame] = None

    def optimize(self) -> None:
        if self.optimizer_parameters is None:
            warn("No Optimizer parameter set. Optimizer cannot be run.")
        elif "Calibration" not in self.data:
            warn("Optimizer cannot be run on validation using direct data.")
        else:
            self.sorted_profiles = Optimizer(
                self.profiles, self.optimizer_parameters
            ).sort_profile()

    def make_profiles(self, models_names: Optional[List[str]] = None) -> None:
        profiles: Dict[str, List[Profile]] = {}
        if "Calibration" in self.data:
            if type(models_names) == str:
                models_names = [models_names]
            list_of_models: List[str] = self.model_manager.initialized_models_list
            if models_names is None:
                if self.model_to_test is None:
                    models_names = list_of_models
                else:
                    models_names = self.model_to_test

            for model_name in models_names:
                if model_name in list_of_models:
                    print(model_name)
                    profiles[model_name] = self.__get_profiles(model_name)
                    print("Number of profile: " + str(len(profiles[model_name])))
        else:
            profiles["Direct"] = self.__get_profiles()

        self.profiles = profiles

    def __get_profiles(self, model_name: str = None) -> List[Profile]:
        profiles: List[Profile] = []
        for data_object in self.data_objects:
            if "Calibration" in self.data:
                data_to_model = self.model_manager.modelize(model_name, data_object)
            else:
                data_to_model = data_object

            current_profile: Profile = Profile(
                data_to_model,
                self.allow_correction,
                self.correction_threshold,
                self.forced_correction_value,
                self.absolute_acceptance
            )
            current_profile.calculate(self.stats_limits)

            if self.generate_figure:
                current_profile.make_plot()
            profiles.append(current_profile)

        return profiles

    @property
    def __get_dataobject(self) -> List[DataObject]:
        validation_dict: Dict[str, pd.DataFrame] = {}
        data_to_model: List[DataObject] = []
        if "Calibration" in self.data:
            calibration_dict: Dict[str, pd.DataFrame] = {}
            if self.rolling_data:
                validation_dict = self.__sliding_window_data(self.data["Validation"])
                calibration_dict = self.__sliding_window_data(self.data["Calibration"])
            else:
                validation_dict["All"] = self.data["Validation"]
                calibration_dict["All"] = self.data["Calibration"]

            for validation_key in validation_dict.keys():
                for calibration_key in calibration_dict.keys():
                    data_to_model.append(
                        DataObject(
                            validation_dict[validation_key],
                            calibration_dict[calibration_key],
                        )
                    )

        else:
            if self.rolling_data:
                validation_dict = self.__sliding_window_data(self.data["Validation"])
            else:
                validation_dict["All"] = self.data["Validation"]

            for validation_key in validation_dict.keys():
                data_to_model.append(DataObject(validation_dict[validation_key]))
                data_to_model[-1].add_calculated_value(data_to_model[-1].data_y())

        data_to_model = self.__sanitize_data_to_model(data_to_model)

        return data_to_model

    def __sliding_window_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        data_level: np.ndarray = data["Level"].unique()
        data_dict: Dict[str, pd.DataFrame] = dict()
        for window_size in range(self.rolling_data_limit - 1, len(data_level) + 1):
            for window_location in range(0, len(data_level) - window_size):
                start_level: int = data_level[window_location]
                end_level: int = data_level[window_location + window_size]
                level_name: str = str(start_level) + "->" + str(end_level)
                data_dict[level_name]: pd.DataFrame = data[
                    (data["Level"] >= start_level) & (data["Level"] <= end_level)
                ]
                data_dict[level_name].reset_index(drop=True, inplace=True)

        return data_dict

    def __sanitize_data_to_model(
        self, data_to_model: List[DataObject]
    ) -> List[DataObject]:
        data_to_keep: List[DataObject] = []
        for data_object in data_to_model:
            if data_object.calibration_data is not None:
                if (
                    (data_object.calibration_first_concentration / 2)
                    < data_object.validation_first_concentration
                    and 1.5 * data_object.calibration_last_concentration
                    >= data_object.validation_last_concentration
                ):
                    data_to_keep.append(data_object)
            else:
                data_to_keep.append(data_object)

        return data_to_keep


class ProfileLevel:
    def __init__(self, level_data: pd.DataFrame, absolute_acceptance: bool = False):
        self.data: pd.DataFrame = level_data
        self.introduced_concentration: Optional[np.float] = None
        self.calculated_concentration: Optional[np.float] = None
        self.bias: Optional[float] = None
        self.relative_bias: Optional[float] = None
        self.recovery: Optional[float] = None
        self.repeatability_var: Optional[float] = None
        self.repeatability_std: Optional[float] = None
        self.repeatability_std_pc: Optional[float] = None
        self.inter_series_var: Optional[float] = None
        self.inter_series_std: Optional[float] = None
        self.inter_series_std_pc: Optional[float] = None
        self.abs_tolerance: List[float] = []
        self.rel_tolerance: List[float] = []
        self.acceptance_interval: List[float] = []
        self.sum_square_error_intra_series: Optional[float] = None
        self.nb_series: Optional[int] = None
        self.nb_measures: Optional[int] = None
        self.nb_rep: Optional[int] = None
        self.fidelity_var: Optional[float] = None
        self.fidelity_std: Optional[float] = None
        self.fidelity_cv: Optional[float] = None
        self.ratio_var: Optional[float] = None
        self.b_coefficient: Optional[float] = None
        self.degree_of_freedom: Optional[float] = None
        self.tolerance_std: Optional[float] = None
        self.abs_uncertainty: Optional[float] = None
        self.rel_uncertainty: Optional[float] = None
        self.pc_uncertainty: Optional[float] = None
        self.cover_factor: Optional[float] = None
        self.absolute_acceptance: bool = absolute_acceptance

    def calculate(self, tolerance_limit: float, acceptance_interval: list) -> None:
        self.nb_series = self.data["Serie"].nunique()
        self.nb_measures = len(self.data.index)
        self.nb_rep = self.nb_measures / self.nb_series
        self.introduced_concentration = self.data["x"].mean()
        self.calculated_concentration = self.data["x_calc"].mean()
        self.acceptance_interval = acceptance_interval
        self.bias = self.calculated_concentration - self.introduced_concentration
        self.relative_bias = (self.bias / self.introduced_concentration) * 100
        self.recovery = (
            self.calculated_concentration / self.introduced_concentration
        ) * 100
        self.repeatability_var = self.get_repeatability_var()
        self.repeatability_std = math.sqrt(self.repeatability_var)
        self.repeatability_std_pc = (
            self.repeatability_std / self.calculated_concentration * 100
        )
        self.inter_series_var = self.get_inter_series_var()
        self.inter_series_std = math.sqrt(self.inter_series_var)
        self.inter_series_std_pc = (
            self.inter_series_std / self.calculated_concentration * 100
        )
        self.fidelity_var = np.sum([self.repeatability_var, self.inter_series_var])
        self.fidelity_std = math.sqrt(self.fidelity_var)
        self.fidelity_cv = self.fidelity_std / self.introduced_concentration * 100
        self.ratio_var = self.get_ratio_var()
        self.b_coefficient = (self.ratio_var + 1) / (self.nb_rep * self.ratio_var + 1)
        self.degree_of_freedom = (self.ratio_var + 1) ** 2 / (
            (self.ratio_var + (1 / self.nb_rep)) ** 2 / (self.nb_series - 1)
            + (1 - (1 / self.nb_rep)) / self.nb_measures
        )
        self.tolerance_std = self.fidelity_std * (
            math.sqrt(1 + (1 / (self.nb_measures * self.b_coefficient)))
        )
        self.abs_tolerance = self.get_absolute_tolerance(tolerance_limit)
        self.rel_tolerance = [
            (tol / self.introduced_concentration) * 100 for tol in self.abs_tolerance
        ]
        self.abs_uncertainty = self.tolerance_std * 2
        self.rel_uncertainty = self.abs_uncertainty / self.calculated_concentration
        self.pc_uncertainty = self.abs_uncertainty / self.introduced_concentration * 100

    def get_acceptance_interval(self, acceptance_limit: float) -> List[float]:
        if self.absolute_acceptance:
            introduced_limit: float = acceptance_limit
        else:
            introduced_limit: float = acceptance_limit / 100 * self.introduced_concentration
        return [
            self.introduced_concentration - introduced_limit,
            self.introduced_concentration + introduced_limit,
        ]

    def get_repeatability_var(self) -> float:
        repeatability_var = 0
        sum_square_errors = 0
        for series in self.data["Serie"].unique():
            series_mean_result = self.data[self.data["Serie"] == series].mean()[
                "x_calc"
            ]
            sum_square_errors += np.sum(
                (self.data[self.data["Serie"] == series]["x_calc"] - series_mean_result)
                ** 2
            )
        self.sum_square_error_intra_series = sum_square_errors

        if sum_square_errors > 0:
            repeatability_var = sum_square_errors / (self.nb_series * (self.nb_rep - 1))
        return repeatability_var

    def get_inter_series_var(self) -> float:
        sum_square_errors_total = np.sum(
            np.square(self.data["x_calc"] - self.data["x_calc"].mean())
        )
        sum_square_errors_inter_series = (
            sum_square_errors_total - self.sum_square_error_intra_series
        )

        if sum_square_errors_inter_series <= 0:
            return 0

        inter_series_var: float = (
            (sum_square_errors_inter_series / (self.nb_series - 1))
            - self.repeatability_var
        ) / self.nb_rep
        if inter_series_var < 0:
            return 0

        return inter_series_var

    def get_ratio_var(self) -> float:
        if self.inter_series_var == 0 or self.repeatability_var == 0:
            ratio_var = 0
        else:
            ratio_var = self.inter_series_var / self.repeatability_var

        return ratio_var

    def get_absolute_tolerance(self, tolerance_limit: float) -> List[float]:

        student_low = t.ppf(
            1 - ((1 - (tolerance_limit / 100)) / 2),
            int(math.floor(self.degree_of_freedom)),
        )
        student_high = t.ppf(
            1 - ((1 - (tolerance_limit / 100)) / 2),
            int(math.ceil(self.degree_of_freedom)),
        )

        self.cover_factor = student_low - (student_low - student_high) * (
            self.degree_of_freedom - math.floor(self.degree_of_freedom)
        )
        tolerance_low = (
            self.calculated_concentration - self.cover_factor * self.tolerance_std
        )
        tolerance_high = (
            self.calculated_concentration + self.cover_factor * self.tolerance_std
        )

        if self.absolute_acceptance:
            tolerance_low = tolerance_low - self.introduced_concentration
            tolerance_high = tolerance_high - self.introduced_concentration

        return [tolerance_low, tolerance_high]


class Profile:
    def __init__(
        self,
        model: Union[models.Model, DataObject],
        correction_allowed: bool = False,
        correction_threshold: List[float] = None,
        forced_correction_value: float = None,
        absolute_acceptance: bool = False
    ):
        self.model = model
        self.acceptance_interval: List[float] = []
        self.absolute_acceptance: bool = absolute_acceptance
        self.min_loq: Optional[float] = None
        self.max_loq: Optional[float] = None
        self.lod: Optional[float] = None
        self.has_limits: bool = False
        self.image_data = None
        self.fig = None
        self.correction_allowed: bool = correction_allowed
        self.correction_threshold: Optional[List[float]] = correction_threshold
        self.forced_correction_value: Optional[float] = forced_correction_value
        self.has_correction: bool = False
        self.correction_factor: Optional[float] = None
        if self.correction_allowed:
            self.generate_correction()
        self.profile_levels: Dict[ProfileLevel] = {}
        for level in self.model.list_of_levels("validation"):
            self.profile_levels[level] = ProfileLevel(self.model.get_level(level), self.absolute_acceptance)

    def summary(self) -> None:
        if type(self.model) == models.Model:
            regression_stats: Dict[int, Dict[str, float]] = {}
            if self.model.multiple_calibration:
                for key, fit_data in self.model.fit.items():
                    regression_stats[key] = fit_data.params.to_dict()
                    regression_stats[key].update({"R-Squared": fit_data.rsquared})
                    regression_stats[key].update({"P-Value": fit_data.f_pvalue})
            else:
                regression_stats[1] = self.model.fit.params.to_dict()
                regression_stats[1].update({"R-Squared": self.model.fit.rsquared})
                regression_stats[1].update({"P-Value": self.model.fit.f_pvalue})
            regression_dataframe: pd.DataFrame = pd.DataFrame(regression_stats)

        model_stats: dict = {
            "LOD": self.lod,
            "Min LOQ": self.min_loq,
            "Max LOQ": self.max_loq,
            "Correction Factor": self.correction_factor,
        }
        model_dataframe: pd.DataFrame = pd.DataFrame([model_stats]).transpose()

        level_stats: Dict[ProfileLevel, dict] = {}
        fidelity_stats: Dict[ProfileLevel, dict] = {}
        accuracy_stats: Dict[ProfileLevel, dict] = {}
        tolerance_interval_stats: Dict[ProfileLevel, dict] = {}
        accuracy_profile_stats: Dict[ProfileLevel, dict] = {}
        uncertainty_stats: Dict[ProfileLevel, dict] = {}

        for level in list(self.profile_levels.keys()):
            level_stats[level]: Dict[ProfileLevel, float] = {}
            fidelity_stats[level]: Dict[ProfileLevel, float] = {}
            accuracy_stats[level]: Dict[ProfileLevel, float] = {}
            tolerance_interval_stats[level]: Dict[ProfileLevel, float] = {}
            accuracy_profile_stats[level]: Dict[ProfileLevel, float] = {}
            uncertainty_stats[level]: Dict[ProfileLevel, float] = {}

            level_stats[level]["Introduced Concentration"] = self.profile_levels[
                level
            ].introduced_concentration
            level_stats[level]["Calculated Concentration"] = self.profile_levels[
                level
            ].calculated_concentration
            fidelity_stats[level][
                "Repeatability standard deviation (sr)"
            ] = self.profile_levels[level].repeatability_std
            fidelity_stats[level][
                "Inter-series standard deviation (sB)"
            ] = self.profile_levels[level].inter_series_std
            fidelity_stats[level][
                "Fidelity standard deviation (sFI)"
            ] = self.profile_levels[level].fidelity_std
            fidelity_stats[level][
                "Fidelity variation coefficient"
            ] = self.profile_levels[level].fidelity_cv

            accuracy_stats[level]["Absolute Bias"] = self.profile_levels[level].bias
            accuracy_stats[level]["Bias %"] = self.profile_levels[level].relative_bias

            tolerance_interval_stats[level]["Degree of freedom"] = self.profile_levels[
                level
            ].degree_of_freedom
            tolerance_interval_stats[level][
                "Coverage factor (kIT)"
            ] = self.profile_levels[level].cover_factor
            tolerance_interval_stats[level][
                "Tolerance standard deviation (sIT)"
            ] = self.profile_levels[level].tolerance_std
            tolerance_interval_stats[level]["B^2 coefficient"] = self.profile_levels[
                level
            ].b_coefficient
            tolerance_interval_stats[level][
                "Lower tolerance interval limit"
            ] = self.profile_levels[level].abs_tolerance[0]
            tolerance_interval_stats[level][
                "Upper tolerance interval limit"
            ] = self.profile_levels[level].abs_tolerance[1]
            tolerance_interval_stats[level][
                "Lower acceptability limit"
            ] = self.profile_levels[level].acceptance_interval[0]
            tolerance_interval_stats[level][
                "Upper acceptability limit"
            ] = self.profile_levels[level].acceptance_interval[1]

            if self.absolute_acceptance:
                accuracy_profile_stats[level]["Bias"] = self.profile_levels[
                    level
                ].bias
                accuracy_profile_stats[level][
                    "Lower tolerance interval limit"
                ] = self.profile_levels[level].abs_tolerance[0]
                accuracy_profile_stats[level][
                    "Upper tolerance interval limit"
                ] = self.profile_levels[level].abs_tolerance[1]
                accuracy_profile_stats[level][
                    "Lower acceptability limit"
                ] = self.acceptance_interval[0]
                accuracy_profile_stats[level][
                    "Upper acceptability limit"
                ] = self.acceptance_interval[1]

            else:
                accuracy_profile_stats[level]["Recovery"] = self.profile_levels[
                    level
                ].recovery
                accuracy_profile_stats[level][
                    "Lower tolerance interval limit in %"
                ] = self.profile_levels[level].rel_tolerance[0]
                accuracy_profile_stats[level][
                    "Upper tolerance interval limit in %"
                ] = self.profile_levels[level].rel_tolerance[1]
                accuracy_profile_stats[level][
                    "Lower acceptability limit in %"
                ] = self.acceptance_interval[0]
                accuracy_profile_stats[level][
                    "Upper acceptability limit in %"
                ] = self.acceptance_interval[1]

            uncertainty_stats[level]["Absolute uncertainty"] = self.profile_levels[
                level
            ].abs_uncertainty
            uncertainty_stats[level]["Relative uncertainty"] = self.profile_levels[
                level
            ].rel_uncertainty
            uncertainty_stats[level]["Relative uncertainty in %"] = self.profile_levels[
                level
            ].pc_uncertainty

        level_dataframe: pd.DataFrame = pd.DataFrame(level_stats)
        fidelity_dataframe: pd.DataFrame = pd.DataFrame(fidelity_stats)
        accuracy_dataframe: pd.DataFrame = pd.DataFrame(accuracy_stats)
        tolerance_interval_dataframe: pd.DataFrame = pd.DataFrame(
            tolerance_interval_stats
        )
        accuracy_profile_dataframe: pd.DataFrame = pd.DataFrame(accuracy_profile_stats)
        uncertainty_datafram: pd.DataFrame = pd.DataFrame(uncertainty_stats)

        print("\n\nModel information")
        if type(self.model) == models.Model:
            print("Model type: Regression")
            print("Model name: " + str(self.model.name))
            print("Formula: " + str(self.model.formula))
            print("Weight: " + str(self.model.weight))
        else:
            print("Model type: Direct")
        print(model_dataframe.astype(float).round(3))
        if type(self.model) == models.Model:
            print("\n\nRegression information")
            print(regression_dataframe.astype(float).round(3))
        print("\n\nProfile Level Information")
        print(level_dataframe.astype(float).round(3))
        print("\n\nFidelity statistics")
        print(fidelity_dataframe.astype(float).round(3))
        print("\n\nAccuracy statistics")
        print(accuracy_dataframe.astype(float).round(3))
        print("\n\nTolerance interval statistics")
        print(tolerance_interval_dataframe.astype(float).round(3))
        print("\n\nAccuracy profile data")
        print(accuracy_profile_dataframe.astype(float).round(3))
        print("\n\nResults uncertainty")
        print(uncertainty_datafram.astype(float).round(3))

    def average_profile_parameter(self, profile_parameter: str) -> Optional[Union[pd.DataFrame, np.ndarray]]:
        if type(profile_parameter) == str:
            profile_parameter = [profile_parameter]
        params_list: dict = {}
        for parameter in profile_parameter:
            if hasattr(list(self.profile_levels.values())[1], parameter):
                value_list: List[float] = []
                for level in self.profile_levels.values():
                    value_list.append(getattr(level, parameter))
                params_list[parameter] = value_list
            else:
                warn("The profile levels do not have attribute named " + parameter)
        if len(value_list) > 0:
            return pd.DataFrame(params_list)
        if len(value_list) == 1:
            return np.ndarray(list(params_list)[0])
        else:
            return None

    def get_profile_parameter(self, profile_parameter: Union[str, list]) -> Optional[Union[pd.DataFrame, np.ndarray]]:
        if type(profile_parameter) == str:
            profile_parameter = [profile_parameter]
        params_list: dict = {}
        for parameter in profile_parameter:
            if hasattr(list(self.profile_levels.values())[1], parameter):
                value_list: dict = {}
                for index, level in self.profile_levels.items():
                    value_list[index] = getattr(level, parameter)
                params_list[parameter] = value_list
            else:
                warn("The profile levels do not have attribute named " + parameter)
        if len(value_list) > 0:
            return pd.DataFrame(params_list)
        if len(value_list) == 1:
            return np.ndarray(list(params_list)[0])
        else:
            return None

    def calculate(self, stats_limits: Optional[Union[Dict[str, float]]] = None) -> None:
        if stats_limits is None:
            stats_limits = {"Tolerance": 80, "Acceptance": 20}
        acceptance_limit = stats_limits["Acceptance"]
        tolerance_limit = stats_limits["Tolerance"]
        if self.absolute_acceptance:
            self.acceptance_interval = [
                0 - acceptance_limit,
                0 + acceptance_limit
            ]
        else:
            self.acceptance_interval = [
                (1 - (acceptance_limit / 100)) * 100,
                (1 + (acceptance_limit / 100)) * 100
            ]
        for level in self.profile_levels.values():
            level.calculate(tolerance_limit, self.acceptance_interval)
        self.min_loq, self.max_loq = self.get_limits_of_quantification()
        if self.min_loq:
            self.lod = self.min_loq / 3.3
            self.has_limits = True
        else:
            self.lod = None

    @staticmethod
    def get_value_between(
        x_value: float, left_coord: (float, float), right_coord: (float, float)
    ) -> float:
        x1, y1 = left_coord
        x2, y2 = right_coord
        slope: float = (y2 - y1) / (x2 - x1)

        return slope * (x_value - x1) + y1

    def get_limits_of_quantification(self) -> (float, float):

        acceptance_limit_point: List[List[shapely.geometry.Point]] = [[], []]
        tolerance_limit_point: List[List[shapely.geometry.Point]] = [[], []]
        level_tolerance_list: List[Dict] = []

        for key, level in self.profile_levels.items():
            acceptance_limit_point[0].append(
                shapely.geometry.Point(
                    round(level.introduced_concentration, 3),
                    round(level.acceptance_interval[0], 3),
                )
            )
            acceptance_limit_point[1].append(
                shapely.geometry.Point(
                    round(level.introduced_concentration, 3),
                    round(level.acceptance_interval[1], 3),
                )
            )
            tolerance_limit_point[0].append(
                shapely.geometry.Point(
                    round(level.introduced_concentration, 3),
                    round(level.abs_tolerance[0], 3),
                )
            )
            tolerance_limit_point[1].append(
                shapely.geometry.Point(
                    round(level.introduced_concentration, 3),
                    round(level.abs_tolerance[1], 3),
                )
            )
            level_tolerance_list.append(
                {
                    "level_id": key,
                    "x_coord": level.introduced_concentration,
                    "lower_tol_y_coord": level.abs_tolerance[0],
                    "lower_acc_y_coord": level.acceptance_interval[0],
                    "lower_inside": level.abs_tolerance[0]
                    > level.acceptance_interval[0],
                    "upper_tol_y_coord": level.abs_tolerance[1],
                    "upper_acc_y_coord": level.acceptance_interval[1],
                    "upper_inside": level.abs_tolerance[1]
                    < level.acceptance_interval[1],
                }
            )

        level_tolerance: pd.DataFrame = pd.DataFrame(
            level_tolerance_list,
            columns=[
                "level_id",
                "x_coord",
                "lower_tol_y_coord",
                "lower_acc_y_coord",
                "lower_inside",
                "upper_tol_y_coord",
                "upper_acc_y_coord",
                "upper_inside",
            ],
        )

        acceptance_line: List[shapely.geometry.LineString] = [
            shapely.geometry.LineString(acceptance_limit_point[0]),
            shapely.geometry.LineString(acceptance_limit_point[1]),
        ]
        tolerance_line: List[shapely.geometry.LineString] = [
            shapely.geometry.LineString(tolerance_limit_point[0]),
            shapely.geometry.LineString(tolerance_limit_point[1]),
        ]

        intersects_list: List[Dict[str, float]] = []

        for type_tol in range(2):
            for type_acc in range(2):
                points = tolerance_line[type_tol].intersection(
                    acceptance_line[type_acc]
                )
                if type(points) == shapely.geometry.Point:
                    intersects_list.append(
                        {
                            "x_value": points.x,
                            "y_value": points.y,
                            "upper_intersect": type_acc,
                        }
                    )
                elif type(points) == shapely.geometry.MultiPoint:
                    for point in points:
                        intersects_list.append(
                            {
                                "x_value": point.x,
                                "y_value": point.y,
                                "upper_intersect": type_acc,
                            }
                        )

        intersects_data: pd.DataFrame = pd.DataFrame(
            intersects_list,
            columns=[
                "x_value",
                "y_value",
                "upper_intersect",
                "going_in",
                "opposite_value",
                "opposite_in",
                "valid",
            ],
        )
        level_switch: List[str] = ["lower", "upper"]
        for index in range(len(intersects_data)):
            switch: int = intersects_data.at[index, "upper_intersect"]

            point_left: pd.Series = level_tolerance[
                level_tolerance["x_coord"] < intersects_data.at[index, "x_value"]
            ].iloc[-1]
            point_right: pd.Series = level_tolerance[
                level_tolerance["x_coord"] > intersects_data.at[index, "x_value"]
            ].iloc[0]

            cur_x_coord: float = intersects_data.at[index, "x_value"]

            left_x_coord: float = point_left["x_coord"]
            right_x_coord: float = point_right["x_coord"]

            right_tol: float = point_right[level_switch[switch] + "_tol_y_coord"]

            left_acc: float = point_left[level_switch[switch] + "_acc_y_coord"]
            right_acc: float = point_right[level_switch[switch] + "_acc_y_coord"]

            left_opp_tol: float = point_left[level_switch[switch - 1] + "_tol_y_coord"]
            right_opp_tol: float = point_right[
                level_switch[switch - 1] + "_tol_y_coord"
            ]

            left_opp_acc: float = point_left[level_switch[switch - 1] + "_acc_y_coord"]
            right_opp_acc: float = point_right[
                level_switch[switch - 1] + "_acc_y_coord"
            ]

            opposite_tol: float = self.get_value_between(
                cur_x_coord,
                [left_x_coord, left_opp_tol],
                [right_x_coord, right_opp_tol],
            )
            opposite_acc: float = self.get_value_between(
                cur_x_coord,
                [left_x_coord, left_opp_acc],
                [right_x_coord, right_opp_acc],
            )
            cur_acc: float = self.get_value_between(
                cur_x_coord, [left_x_coord, left_acc], [right_x_coord, right_acc]
            )

            intersects_data.at[index, "opposite_value"] = opposite_tol

            if (
                min([right_opp_acc, right_acc])
                < right_tol
                < max([right_opp_acc, right_acc])
            ):
                intersects_data.at[index, "going_in"] = 1
            else:
                intersects_data.at[index, "going_in"] = 0

            if (
                min([cur_acc, opposite_acc])
                < opposite_tol
                < max([cur_acc, opposite_acc])
            ):
                intersects_data.at[index, "opposite_in"] = 1
            else:
                intersects_data.at[index, "opposite_in"] = 0

            if (
                intersects_data.at[index, "opposite_in"]
                and intersects_data.at[index, "going_in"]
            ):
                intersects_data.at[index, "valid"] = 1
            else:
                intersects_data.at[index, "valid"] = 0

        intersects_data.sort_values("x_value", inplace=True)

        min_loq: Optional[float] = None
        max_loq: Optional[float] = None

        if len(intersects_data):
            if intersects_data.iloc[-1]["valid"]:
                max_loq = level_tolerance.iloc[-1]["x_coord"]
            elif len(
                intersects_data.loc[
                    (intersects_data["valid"] == 0)
                    & (intersects_data["opposite_in"] == 1)
                ]
            ):
                max_loq = intersects_data.loc[
                    (intersects_data["valid"] == 0)
                    & (intersects_data["opposite_in"] == 1)
                ].iloc[-1]["x_value"]

            if len(intersects_data.loc[intersects_data["valid"] == 1]):
                min_loq = intersects_data.loc[intersects_data["valid"] == 1].iloc[-1][
                    "x_value"
                ]
        else:
            if (
                level_tolerance.iloc[0]["lower_tol_y_coord"]
                > level_tolerance.iloc[0]["lower_acc_y_coord"]
                and level_tolerance.iloc[0]["upper_tol_y_coord"]
                < level_tolerance.iloc[0]["upper_acc_y_coord"]
            ):
                max_loq = level_tolerance.iloc[-1]["x_coord"]
                min_loq = level_tolerance.iloc[0]["x_coord"]

        return [min_loq, max_loq]

    def make_plot(self):

        fig = plt.figure()
        ax = aa.Subplot(fig, 111)
        fig.add_subplot(ax)

        levels_x = np.array(
            [level.introduced_concentration for level in self.profile_levels.values()]
        )
        ax.axis["bottom", "top", "right"].set_visible(False)
        if self.absolute_acceptance:
            y_error = np.array([s.abs_uncertainty for s in self.profile_levels.values()])
            ax.axis["y=0"] = ax.new_floating_axis(nth_coord=0, value=0)
            results_y = [
                s.calculated_concentration - s.introduced_concentration
                for s in self.profile_levels.values()
            ]
            ax.set_ylabel("Accuracy (deviation from the target value)")
            min_tol_limits = [level.abs_tolerance[0] for level in self.profile_levels.values()]
            max_tol_limits = [level.abs_tolerance[1] for level in self.profile_levels.values()]
            y_recovery = np.array([level.bias for level in self.profile_levels.values()])
            ax.errorbar(
                levels_x,
                y_recovery,
                yerr=y_error,
                color="m",
                linewidth=2.0,
                marker=".",
                label="Accuracy",
            )
        else:
            y_error = np.array([s.pc_uncertainty for s in self.profile_levels.values()])
            ax.axis["y=100"] = ax.new_floating_axis(nth_coord=0, value=100)
            results_y = [
                (s.calculated_concentration / s.introduced_concentration) * 100
                for s in self.profile_levels.values()
            ]
            ax.set_ylabel("Recovery (%)")
            min_tol_limits = [level.rel_tolerance[0] for level in self.profile_levels.values()]
            max_tol_limits = [level.rel_tolerance[1] for level in self.profile_levels.values()]
            y_recovery = np.array([level.recovery for level in self.profile_levels.values()])
            ax.errorbar(
                levels_x,
                y_recovery,
                yerr=y_error,
                color="m",
                linewidth=2.0,
                marker=".",
                label="Recovery",
            )

        ax.plot(
            levels_x,
            min_tol_limits,
            linewidth=1.0,
            color="b",
            label="Min tolerance limit",
        )
        ax.plot(
            levels_x,
            max_tol_limits,
            linewidth=1.0,
            color="g",
            label="Max tolerance limit",
        )
        ax.plot(
            levels_x,
            [self.acceptance_interval[0] for _ in self.profile_levels.values()],
            "k--",
            label="Acceptance limit",
        )
        ax.plot(
            levels_x,
            [self.acceptance_interval[1] for _ in self.profile_levels.values()],
            "k--",
        )
        results_x = [s.introduced_concentration for s in self.profile_levels.values()]

        ax.scatter(results_x, results_y, alpha=0.5, s=2)

        ax.set_xlabel("Concentration")

        ax.legend(loc=1)

        self.fig = fig

        self.image_data = io.BytesIO()

    def generate_correction(self):
        ratio: float = np.mean(self.model.data_x_calc / self.model.data_x()).round(2)
        if ratio < self.correction_threshold[0] or ratio > self.correction_threshold[1]:
            if self.forced_correction_value is not None:
                ratio = 1 / self.forced_correction_value
            corrected_value: pd.DataFrame = pd.DataFrame(
                self.model.data_x_calc / ratio, columns=["x_calc"]
            )
            self.has_correction = True
            self.correction_factor = 1 / ratio
            self.model.data.add_corrected_value(corrected_value)


class Optimizer:
    def __init__(
        self,
        profiles: Dict[str, Profile],
        optimizer_parameters: Dict[str, Union[str, bool]],
    ):

        self.parameter_function: Dict[str, Callable] = {
            "has_limits": self.__get_has_limits,
            "min_loq": self.__get_min_loq,
            "model.rsquared": self.__get_model_rsquared,
            "max_loq": self.__get_max_loq,
            "lod": self.__get_lod,
            "model.data.calibration_levels": self.__get_model_data_calibration_levels,
            "validation_range": self.__get_validation_range,
            "average.bias": self.__get_average_bias,
        }

        self.profiles = profiles
        self.parameters = optimizer_parameters

        self.profile_value = self.get_profile_value()

    def sort_profile(self) -> pd.DataFrame:
        boolean_parameter: Dict[str, bool] = {}
        ascending_parameter: Dict[str, bool] = {}
        final_dataframe: pd.DataFrame = self.profile_value
        for key, value in self.parameters.items():
            if type(value) == bool:
                boolean_parameter[key] = value

        for key, value in self.parameters.items():
            if value == "max":
                ascending_parameter[key] = False
            elif value == "min":
                ascending_parameter[key] = True

        for parameter in boolean_parameter:
            final_dataframe = final_dataframe[
                final_dataframe[parameter] == self.parameters[parameter]
            ]

        final_dataframe = final_dataframe.sort_values(
            by=list(ascending_parameter.keys()), ascending=ascending_parameter.values()
        )

        return final_dataframe

    def get_profile_value(self) -> pd.DataFrame:
        results: pd.DataFrame = pd.DataFrame()
        for parameter in self.parameters.keys():
            if len(results) == 0:
                results = self.parameter_function[parameter]()
            else:
                results = pd.merge(
                    results, self.parameter_function[parameter](), on=["Model", "Index"]
                )

        return results

    def __get_validation_range(self) -> pd.DataFrame:
        valid_range: pd.DataFrame = pd.merge(
            self.__get_max_loq(), self.__get_min_loq(), on=["Model", "Index"]
        )
        valid_range["validation_range"] = (
            valid_range["max_loq"] - valid_range["min_loq"]
        )
        valid_range = valid_range.drop(["min_loq", "max_loq"], axis=1)
        return valid_range

    def __get_model_rsquared(self) -> pd.DataFrame:
        return self.__get_profile_model("rsquared")

    def __get_average_bias(self) -> pd.DataFrame:
        return self.__get_profiel_average("bias")

    def __get_model_data_calibration_levels(self) -> pd.DataFrame:
        return self.__get_profile_model_data("calibration_levels")

    def __get_min_loq(self) -> pd.DataFrame:
        return self.__get_profile_value("min_loq")

    def __get_max_loq(self) -> pd.DataFrame:
        return self.__get_profile_value("max_loq")

    def __get_lod(self) -> pd.DataFrame:
        return self.__get_profile_value("lod")

    def __get_has_limits(self) -> pd.DataFrame:
        return self.__get_profile_value("has_limits")

    def __get_profile_value(self, parameter) -> pd.DataFrame:
        return_value: pd.DataFrame = pd.DataFrame()
        for profile_type in self.profiles.keys():
            for key, profile in enumerate(self.profiles[profile_type]):
                temp_dataframe = pd.DataFrame(
                    [[profile_type, key, getattr(profile, parameter)]],
                    columns=["Model", "Index", parameter],
                )
                return_value = return_value.append(temp_dataframe, ignore_index=True)
        return return_value

    def __get_profile_model(self, parameter) -> pd.DataFrame:
        return_value: pd.DataFrame = pd.DataFrame()
        for profile_type in self.profiles.keys():
            for key, profile in enumerate(self.profiles[profile_type]):
                temp_dataframe = pd.DataFrame(
                    [[profile_type, key, getattr(profile.model, parameter)]],
                    columns=["Model", "Index", "model." + parameter],
                )
                return_value = return_value.append(temp_dataframe, ignore_index=True)
        return return_value

    def __get_profile_model_data(self, parameter) -> pd.DataFrame:
        return_value: pd.DataFrame = pd.DataFrame()
        for profile_type in self.profiles.keys():
            for key, profile in enumerate(self.profiles[profile_type]):
                temp_dataframe = pd.DataFrame(
                    [[profile_type, key, getattr(profile.model.data, parameter)]],
                    columns=["Model", "Index", "model.data." + parameter],
                )
                return_value = return_value.append(temp_dataframe, ignore_index=True)
        return return_value

    def __get_profiel_average(self, parameter) -> pd.DataFrame:
        return_value: pd.DataFrame = pd.DataFrame()
        for profile_type in self.profiles.keys():
            for key, profile in enumerate(self.profiles[profile_type]):
                temp_dataframe = pd.DataFrame(
                    [[profile_type, key, profile.average_profile_parameter(parameter)]],
                    columns=["Model", "Index", "average." + parameter],
                )
                return_value = return_value.append(temp_dataframe, ignore_index=True)
        return return_value

    @property
    def available_parameters(self):
        return self.parameter_function.keys()
