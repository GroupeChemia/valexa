from __future__ import annotations

import json
import math
from typing import List, Dict, Optional, Union, Callable
from warnings import warn, resetwarnings, filterwarnings

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import shapely.geometry
import statsmodels.formula.api as smf
import statsmodels.regression.linear_model as sm
import statsmodels.stats.outliers_influence as smout
from scipy.stats import t

import valexa.helper as vx
from valexa import models
from valexa.dataobject import DataObject
from valexa.helper import roundsf

OptimizerParams = Dict[str, Union[str, bool]]


class ProfileManager:
    def __init__(
            self,
            compound_name: str,
            data: Dict[str, pd.DataFrame],
            tolerance_limit: float = 80,
            acceptance_limit: float = 20,
            acceptance_absolute: bool = False,
            quantity_units: str = None,
            rolling_data: bool = False,
            rolling_limit: Union[list, int] = 3,
            model_to_test: Union[List[str], str] = None,
            correction_allow: bool = False,
            correction_threshold: Optional[List[float]] = None,
            correction_forced_value: Optional[float] = None,
            correction_round_to: int = 2,
            correction_type: Optional[str] = "slope",
            optimizer_parameter: Optional[OptimizerParams] = None,
            significant_figure: int = 4,
            lod_allowed: Optional[list] = None,
            lod_force_miller: bool = False,
            data_transformation: Optional[str] = None,
            use_median: bool = False,
            **_
    ):
        """
        Init ProfileManager with the necessary dataset
        :param str compound_name: This is the name of the compounds for the profile
        :param dict data: These are the dataset in the form of a Dictionnary containing a DataFrame. The format should
        be {"Validation": DataFrame, "Calibration": DataFrame}. Note that the calibration dataset are optional.
        :param int? tolerance_limit: The tolerance limit (beta), defaults to 80
        :param float? acceptance_limit: The acceptance limit (lambda), defaults to 20
        :param bool? acceptance_absolute: If True, the acceptance will be considered to be in absolute unit instead
        of percentage, defaults to False
        :param str? quantity_units: The units (%, mg/l, ppm, ...) of the introduced dataset. This is only to
        ease the reading of the output, default to None.
        :param bool? rolling_data: If this is set to True, the system will do multiple iteration with the dataset
        and generate multiple profile with each subset of dataset, defaults to False.
        :param list? rolling_limit: In combination with rolling_data, this is the minimum length of the subset
        that rolling_data will go to. This can also be a list if the number of minimum is different for the validation
        and the calibration data, in which case the order is [Validation, Calibration], defaults to 3.
        :param list? model_to_test: A list of model to test, if not set the system will test them all, defaults to
        None.
        :param bool? correction_allow: If set to true, the model will be multiplied by a factor to bring the
        recovery close to 1, defaults to False
        :param list? correction_threshold: If allow_correction is set to True, these will overwrite the default
        correction threshold (0.9 - 1.1). Setting this to [1,1] will force a correction to be calculated. The
        correction_threshold is calculated by calculating the average recovery ratio. If the ratio is outside the
        indicated range, a correction will be applied, defaults to [0.9, 1.1]
        :param float? correction_forced_value: If allow_correction is set to True, this will set the correction
        value to the indicated value instead of calculating it. Note: the value of the average recovery ratio must still
        be outside the threshold for this to take effect, defaults to None
        :param str? correction_type: Set the type of correction to apply, if allowed, "slope" use the inverse of the
        slope of the expected vs calculated plot, "average" will use use the average bias, defaults to "slope"
        :param int? correction_round_to: If allow_correction is set to True, the generated correction will be
        rounded to this number of significant figures, defaults to 2.
        :param dict? optimizer_parameter: These are the value used to sort the profile from best to worst when
        using the optimizer, default to None
        :param int? significant_figure: Set the number of significant figure to take into account during the
        analysis. Setting this to 0 will remove any rounding, defaults to 4
        :param list? lod_allowed: List the allowed type of LOD calculation, LOQ/3.3 is self-describing, Miller use the
        regression standard deviation (Miller & Miller, 2010), if set to None, it will try both, defaults to None
        :param bool? lod_force_miller: Force the use of Miller & Miller calculation method for the LOD determination,
        defaults to False
        :param str? data_transformation: Apply transformation to data, currently the option are None or "log10",
        defaults to None
        :param bool? use_median: Use median instead of mean for level target, defaults to False

        """
        self.compound_name: str = compound_name
        self.quantity_units: str = quantity_units if quantity_units is not None else 'No Units'
        self.stats_limits: Dict[str, float] = {
            "Tolerance": tolerance_limit,
            "Acceptance": acceptance_limit,
        }
        self.tolerance_limit: float = tolerance_limit
        self.acceptance_limit: float = acceptance_limit
        self.absolute_acceptance: bool = acceptance_absolute
        self.data: Dict[str, pd.DataFrame] = data
        self.sigfig: int = significant_figure
        if lod_allowed is None:
            self.lod_allowed: list = ['LOQ/3.3', 'Miller']
        else:
            self.lod_allowed: list = lod_allowed
        self.lod_force_miller: bool = lod_force_miller

        if type(model_to_test) == str:
            model_to_test = [model_to_test]
        self.model_to_test: List[str] = model_to_test
        self.rolling_data: bool = rolling_data

        self.__set_rolling_data_limit(rolling_limit)

        self.allow_correction: bool = correction_allow
        self.correction_round_to: int = correction_round_to
        self.forced_correction_value = None
        if correction_allow:
            if correction_threshold is None:
                correction_threshold = [0.9, 1.1]
            self.correction_threshold: Optional[List[float]] = correction_threshold
            if correction_forced_value is not None:
                self.forced_correction_value = float(correction_forced_value)
        else:
            self.correction_threshold: Optional[List[float]] = None

        self.correction_type: str = correction_type
        self.optimizer_parameters: Optional[OptimizerParams] = optimizer_parameter

        if "Calibration" in self.data:
            self.model_manager: models.ModelsManager = models.ModelsManager()
            self.model_manager.initialize_models(self.model_to_test)

        self.data_transformation: Optional[str] = data_transformation
        self.use_median: Optional[bool] = use_median

        self.data_objects: List[DataObject] = self.__get_dataobject
        self.profiles: Optional[Dict[str, Profile]] = None
        self.sorted_profiles: Optional[pd.DataFrame] = None

    def __set_rolling_data_limit(self, rolling_data_limit: Union[list, int]) -> None:
        if type(rolling_data_limit) == list:
            self.rolling_data_limit_validation = rolling_data_limit[0]
            self.rolling_data_limit_calibration = rolling_data_limit[1]
        else:
            self.rolling_data_limit_validation = rolling_data_limit
            self.rolling_data_limit_calibration = rolling_data_limit

        if (
                self.rolling_data_limit_validation
                > self.data["Validation"]["Level"].nunique()
        ):
            warn(
                "Minimum amount of data for Validation is "
                + str(self.data["Validation"]["Level"].nunique())
                + ". Limit set at this value."
            )
            self.rolling_data_limit_validation = self.data["Validation"][
                "Level"
            ].nunique()

        if "Calibration" in self.data:
            if (
                    self.rolling_data_limit_calibration
                    > self.data["Calibration"]["Level"].nunique()
            ):
                warn(
                    "Minimum amount of data for Validation is "
                    + str(self.data["Validation"]["Level"].nunique())
                    + ". Limit set at this value."
                )
                self.rolling_data_limit_calibration = self.data["Calibration"][
                    "Level"
                ].nunique()

    def best(
            self, type_of_model: Optional[str] = None, number: Optional[int] = None
    ) -> Optional[Profile]:

        if self.sorted_profiles is not None:
            profiles_list = self.sorted_profiles
        else:
            profile_dict = {"Model": [], "Index": []}
            for key, value in self.profiles.items():
                for index in range(len(value)):
                    profile_dict["Model"].append(key)
                    profile_dict["Index"].append(index)
            profiles_list = pd.DataFrame(profile_dict)

        if type_of_model in self.profiles and type_of_model is not None:
            profiles_list = profiles_list[profiles_list["Model"] == type_of_model]
        elif type_of_model not in self.profiles and type_of_model is not None:
            warn("No profile of model " + type_of_model + " found.")
            return None

        if number is None:
            model, index = profiles_list[["Model", "Index"]].iloc[0]
            return self.profiles[model][index]

        elif number < len(profiles_list):
            model, index = profiles_list[["Model", "Index"]].iloc[number]
            return self.profiles[model][number]
        else:
            warn(
                "The profile number must be less or equal to "
                + str(len(profiles_list) - 1)
            )
            return None

    def output_profiles(self, format: str = "dict"):
        output_dict = {}
        profile_number = 0

        if self.sorted_profiles is not None:
            for index, profile in self.sorted_profiles.iterrows():
                temp_profile_data = self.profiles[profile["Model"]][
                    profile["Index"]
                ].output_profile()
                temp_profile_data["id"] = profile_number
                temp_profile_data["compound_name"] = self.compound_name
                temp_profile_data["quantity_units"] = self.quantity_units
                output_dict[profile_number] = temp_profile_data
                profile_number += 1

        else:
            for profile_list in self.profiles.values():
                for profile in profile_list:
                    temp_profile_data = profile.output_profile()
                    temp_profile_data["id"] = profile_number
                    temp_profile_data["compound_name"] = self.compound_name
                    temp_profile_data["quantity_units"] = self.quantity_units
                    output_dict[profile_number] = temp_profile_data
                    profile_number += 1

        if format == "dict":
            return output_dict
        elif format == "json":
            return json.dumps(output_dict)
        else:
            warn("Available format are: dict, json")
            return None

    def optimize(self) -> None:
        if self.optimizer_parameters is None:
            warn("No Optimizer parameter set. Optimizer cannot be run.")
        elif "Calibration" not in self.data:
            warn("Optimizer cannot be run on validation using direct dataset.")
        elif len(self.profiles) == 0:
            warn(
                "No profiles found. Have you calculated them by using .make_profile()?"
            )
        else:
            self.sorted_profiles = Optimizer(
                self.profiles, self.optimizer_parameters
            ).sort_profile()

    def make_profiles(self, models_names: Optional[Union[list, str]] = None) -> None:
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
                    profiles[model_name] = self.__get_profiles(model_name)
        else:
            profiles["Direct"] = self.__get_profiles()

        self.profiles = profiles

    def __get_profiles(self, model_name: str = None) -> List[Profile]:
        profiles: List[Profile] = []
        for data_object in self.data_objects:
            if "Calibration" in self.data:
                if (
                        data_object.calibration_levels
                        >= self.model_manager.get_model_min_point(model_name)
                ):
                    data_to_model = self.model_manager.modelize(
                        model_name, data_object, self.sigfig
                    )
                else:
                    warn(
                        model_name
                        + " require at least "
                        + str(self.model_manager.get_model_min_point(model_name))
                        + " level to generate. Skipped possibility with only "
                        + str(data_object.calibration_levels)
                        + " point(s)"
                    )
                    data_to_model = None
            else:
                data_to_model = data_object

            if data_to_model is not None:
                current_profile: Profile = Profile(
                    model=data_to_model,
                    correction_allowed=self.allow_correction,
                    correction_type=self.correction_type,
                    correction_threshold=self.correction_threshold,
                    forced_correction_value=self.forced_correction_value,
                    absolute_acceptance=self.absolute_acceptance,
                    correction_round_to=self.correction_round_to,
                    sigfig=self.sigfig,
                    lod_allowed=self.lod_allowed,
                    lod_force_miller=self.lod_force_miller,
                    compound=self.compound_name,
                    units=self.quantity_units,
                    use_median=self.use_median
                )
                current_profile.calculate(self.stats_limits)

                profiles.append(current_profile)

        return profiles

    @property
    def __get_dataobject(self) -> List[DataObject]:
        validation_dict: Dict[str, pd.DataFrame] = {}
        data_to_model: List[DataObject] = []
        if "Calibration" in self.data:
            calibration_dict: Dict[str, pd.DataFrame] = {}
            if self.rolling_data:
                validation_dict = self.__sliding_window_data(
                    self.data["Validation"], self.rolling_data_limit_validation
                )
                calibration_dict = self.__sliding_window_data(
                    self.data["Calibration"], self.rolling_data_limit_calibration
                )
            else:
                validation_dict["All"] = self.data["Validation"]
                calibration_dict["All"] = self.data["Calibration"]

            for validation_key in validation_dict.keys():
                for calibration_key in calibration_dict.keys():
                    data_to_model.append(
                        DataObject(
                            validation_dict[validation_key],
                            calibration_dict[calibration_key],
                            self.data_transformation
                        )
                    )

        else:
            if self.rolling_data:
                validation_dict = self.__sliding_window_data(
                    self.data["Validation"], self.rolling_data_limit_validation
                )
            else:
                validation_dict["All"] = self.data["Validation"]

            for validation_key in validation_dict.keys():
                data_to_model.append(
                    DataObject(
                        validation_dict[validation_key],
                        data_transformation=self.data_transformation
                    )
                )
                data_to_model[-1].add_value(data_to_model[-1].data_y(), "x_calc")

        # data_to_model = self.__sanitize_data_to_model(data_to_model)

        return data_to_model

    def __sliding_window_data(
            self, data: pd.DataFrame, size_limit: int
    ) -> Dict[str, pd.DataFrame]:
        data_level: np.ndarray = data["Level"].unique()
        data_dict: Dict[str, pd.DataFrame] = dict()
        for window_size in range(size_limit - 1, len(data_level) + 1):
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
                        and data_object.calibration_last_concentration
                        <= 1.5 * data_object.validation_last_concentration
                ):
                    data_to_keep.append(data_object)
            else:
                data_to_keep.append(data_object)

        return data_to_keep

    def get_number_of_dataset(self) -> int:
        return len(self.data_objects)


class Profile:
    def __init__(
            self,
            model: Union[models.Model, DataObject],
            correction_allowed: bool = False,
            correction_type: str = "slope",
            correction_threshold: List[float] = None,
            forced_correction_value: float = None,
            absolute_acceptance: bool = False,
            correction_round_to: int = 2,
            sigfig: int = 4,
            lod_allowed: list = None,
            lod_force_miller: bool = False,
            compound: str = None,
            units: str = None,
            use_median: bool = False,
    ):
        if lod_allowed is None:
            lod_allowed = ["LOQ/3.3", "Miller"]
        self.model = model
        self.compound = compound
        self.units = units
        self.acceptance_interval: List[float] = []
        self.absolute_acceptance: bool = absolute_acceptance
        self.acceptance_limit: Optional[float] = None
        self.tolerance_limit: Optional[float] = None
        self.min_loq: Optional[float] = None
        self.max_loq: Optional[float] = None
        self.lod: Optional[float] = None
        self.has_limits: bool = False
        self.image_data = None
        self.fig = None
        self.sigfig: int = sigfig
        self.correction_allowed: bool = correction_allowed
        self.correction_type: str = correction_type
        self.correction_threshold: Optional[List[float]] = correction_threshold
        self.forced_correction_value: Optional[float] = forced_correction_value
        self.correction_round_to: int = correction_round_to
        self.has_correction: Optional[str] = None
        self.correction_parameter: Optional[dict] = None
        self.correction_factor: Optional[float] = None
        self.lod_allowed = lod_allowed
        self.lod_force_miller = lod_force_miller
        self.lod_type: Optional[str] = None
        self.use_median: bool = use_median
        if self.correction_allowed:
            self.generate_correction()
        self.calculate_bias()
        self.profile_levels: Dict[ProfileLevel] = {}
        for level in self.model.list_of_levels("validation"):
            self.profile_levels[level] = ProfileLevel(
                self.model.get_level(level), self.absolute_acceptance, self.sigfig, self.use_median
            )
        self.graphs: dict = {}
        self.linearity: dict = {}

    def summary(self) -> None:

        filterwarnings("ignore")

        print("Model Info\n")
        print(pd.Series(self.profile_data("model_info")))

        if self.profile_data("regression_info").size > 0:
            print("\nRegression Info\n")
            print(self.profile_data("regression_info").transpose())

        print("\nLinearity Info\n")
        print(self.profile_data("linearity_info").transpose())

        if self.has_correction:
            print("\nCorrection Info\n")
            print(self.profile_data("correction_info").transpose())

        print("\nLevels Info\n")
        print(self.profile_data("levels_info").transpose())

        print("\nBias Info\n")
        print(self.profile_data("bias_info").transpose())

        print("\nRepeatability Info\n")
        print(self.profile_data("repeatability_info").transpose())

        print("\nIntermediate Precision\n")
        print(self.profile_data("intermediate_precision").transpose())

        print("\nTotal Error\n")
        print(self.profile_data("total_error").transpose())

        print("\nMiscellaneous Stats\n")
        print(self.profile_data("misc_stats").transpose())

        print("\nTolerance Info\n")
        print(self.profile_data("tolerance_info").transpose())

        print("\nUncertainty Info\n")
        print(self.profile_data("uncertainty_info").transpose())

        print("\nValidation Data\n")
        print(self.model.validation_data)

        if self.profile_data("regression_info").size > 0:
            print("\nCalibration Data\n")
            print(self.model.calibration_data)

        resetwarnings()

    def calculate_bias(self) -> None:
        bias_abs: pd.Series = self.model.validation_data[
                                  "x_calc"
                              ] - self.model.validation_data["x"]
        bias_rel = bias_abs / self.model.validation_data["x"] * 100
        self.model.add_value(
            bias_abs.map(lambda val: roundsf(val, self.sigfig)), "bias_abs"
        )
        self.model.add_value(
            bias_rel.map(lambda val: roundsf(val, self.sigfig)), "bias_rel"
        )

    def average_profile_parameter(
            self, profile_parameter: str
    ) -> Optional[Union[pd.DataFrame, np.ndarray]]:
        if type(profile_parameter) == str:
            profile_parameter = [profile_parameter]
        params_list: pd.DataFrame = pd.DataFrame()
        for parameter in profile_parameter:
            if hasattr(list(self.profile_levels.values())[1], parameter):
                value_list: List[float] = []
                for level in self.profile_levels.values():
                    value_list.append(getattr(level, parameter))
                params_list = pd.concat(
                    [
                        params_list,
                        pd.DataFrame([np.mean(value_list)], index=[parameter]),
                    ]
                )
            else:
                warn("The profile levels do not have attribute named " + parameter)
        if len(params_list) > 0:
            return params_list.transpose()
        else:
            return None

    def get_profile_parameter(
            self, profile_parameter: Union[str, list]
    ) -> Optional[pd.DataFrame]:
        if type(profile_parameter) == str:
            profile_parameter = [profile_parameter]
        params_list: pd.DataFrame = pd.DataFrame()
        for parameter in profile_parameter:
            if hasattr(list(self.profile_levels.values())[1], parameter):
                value_dict: dict = {}
                for index, level in self.profile_levels.items():
                    value_dict[index] = getattr(level, parameter)
                if type(list(value_dict.values())[0]) == pd.Series:
                    params_list = pd.concat([params_list, pd.DataFrame(value_dict)])
                else:
                    params_list = pd.concat(
                        [params_list, pd.DataFrame(value_dict, index=[parameter])]
                    )
            else:
                warn("The profile levels do not have attribute named " + parameter)
        if len(params_list) > 0:
            return params_list.transpose()
        else:
            return None

    def get_model_parameter(
            self, model_parameter: Union[str, list]
    ) -> Optional[pd.DataFrame]:
        if type(model_parameter) == str:
            model_parameter = [model_parameter]
        params_list = pd.DataFrame()
        if hasattr(self, "model"):
            for parameter in model_parameter:
                if type(self.model.fit) == dict:
                    if hasattr(list(self.model.fit.values())[1], parameter):
                        value_dict: dict = {}
                        for index, fit in self.model.fit.items():
                            value_dict[index] = getattr(fit, parameter)
                        if type(list(value_dict.values())[0]) == pd.Series:
                            params_list = pd.concat(
                                [params_list, pd.DataFrame(value_dict)]
                            )
                        else:
                            params_list = pd.concat(
                                [
                                    params_list,
                                    pd.DataFrame(value_dict, index=[parameter])
                                ]
                            )
                    elif hasattr(self.model, parameter):
                        value_dict: dict = {}
                        for index, param in getattr(self.model, parameter).items():
                            value_dict[index] = param
                        if type(list(value_dict.values())[0]) == pd.Series:
                            params_list = pd.concat(
                                [params_list, pd.DataFrame(value_dict)]
                            )
                        else:
                            params_list = pd.concat(
                                [
                                    params_list,
                                    pd.DataFrame(value_dict, index=[parameter])
                                ]
                            )
                    else:
                        warn(
                            "The model fits do not have an attribute named " + parameter
                        )
                else:
                    if hasattr(self.model.fit, parameter):
                        value = getattr(self.model.fit, parameter)
                        if type(value) == pd.Series:
                            params_list = pd.concat([params_list, pd.DataFrame(value)])
                        else:
                            params_list = pd.concat(
                                [params_list, pd.DataFrame([value], index=[parameter])]
                            )
                    elif hasattr(self.model, parameter):
                        value = getattr(self.model, parameter)
                        if type(value) == pd.Series:
                            params_list = pd.concat([params_list, pd.DataFrame(value)])
                        else:
                            params_list = pd.concat(
                                [params_list, pd.DataFrame([value], index=[parameter])]
                            )
                    else:
                        warn(
                            "The model fit do not have an attribute named " + parameter
                        )

            if len(params_list) > 0:
                return params_list.transpose()
            else:
                return None
        else:
            warn("This profile has no model")
            return None

    def calculate(self, stats_limits: Optional[Union[Dict[str, float]]] = None) -> None:
        if stats_limits is None:
            stats_limits = {"Tolerance": 80, "Acceptance": 20}
        self.acceptance_limit = stats_limits["Acceptance"]
        self.tolerance_limit = stats_limits["Tolerance"]

        for level in self.profile_levels.values():
            level.calculate(self.tolerance_limit, self.acceptance_limit)

        self.min_loq, self.max_loq = self.get_limits_of_quantification()
        if self.min_loq:
            self.lod = self.get_lod()
            self.has_limits = True
        else:
            self.lod = None
        self.linearity = self.get_linearity
        self.generate_graphs()

    def get_lod(self) -> float:
        base_lod = self.min_loq / 3.3
        miller_lod = None
        if "Miller" in self.lod_allowed:
            if self.model.calibration_data is not None:
                miller_lod = pd.Series(self.model.miller_lod).mean()
        if self.lod_force_miller:
            self.lod_type = "Miller"
            return miller_lod
        else:
            if miller_lod is not None:
                if miller_lod < base_lod:
                    self.lod_type = "Miller"
                    return miller_lod
                else:
                    self.lod_type = "LOQ/3.3"
                    return base_lod
            else:
                self.lod_type = "LOQ/3.3"
                return base_lod

    @property
    def get_linearity(self) -> (dict):
        x_plot: sm.RegressionResults = smf.ols(
            formula="x_calc~x", data=self.model.validation_data
        ).fit()

        intercept: float = x_plot.params["Intercept"]
        slope: float = x_plot.params["x"]

        return {
            "slope": {"value": slope, "p_value": x_plot.pvalues["x"], "std_error": x_plot.bse["x"]},
            "intercept": {"value": intercept, "p_value": x_plot.pvalues["Intercept"],
                          "std_error": x_plot.bse["Intercept"]},
            "rsquared": {"value": x_plot.rsquared, "p_value": x_plot.f_pvalue, "std_error": ""}
        }

    def get_limits_of_quantification(self) -> (float, float):

        acceptance_limit_point: List[List[shapely.geometry.Point]] = [[], []]
        tolerance_limit_point: List[List[shapely.geometry.Point]] = [[], []]
        level_tolerance_list: List[Dict] = []

        for key, level in self.profile_levels.items():
            acceptance_limit_point[0].append(
                shapely.geometry.Point(
                    roundsf(level.introduced_concentration, self.sigfig),
                    roundsf(
                        level.acceptance_limits_abs["acceptance_limits_abs_low"],
                        self.sigfig,
                    ),
                )
            )
            acceptance_limit_point[1].append(
                shapely.geometry.Point(
                    roundsf(level.introduced_concentration, self.sigfig),
                    roundsf(
                        level.acceptance_limits_abs["acceptance_limits_abs_high"],
                        self.sigfig,
                    ),
                )
            )
            tolerance_limit_point[0].append(
                shapely.geometry.Point(
                    roundsf(level.introduced_concentration, self.sigfig),
                    roundsf(level.tolerance_abs["tolerance_abs_low"], self.sigfig),
                )
            )
            tolerance_limit_point[1].append(
                shapely.geometry.Point(
                    roundsf(level.introduced_concentration, self.sigfig),
                    roundsf(level.tolerance_abs["tolerance_abs_high"], self.sigfig),
                )
            )
            level_tolerance_list.append(
                {
                    "level_id": key,
                    "x_coord": level.introduced_concentration,
                    "lower_tol_y_coord": level.tolerance_abs["tolerance_abs_low"],
                    "lower_acc_y_coord": level.acceptance_limits_abs[
                        "acceptance_limits_abs_low"
                    ],
                    "lower_inside": level.tolerance_abs["tolerance_abs_low"]
                                    > level.acceptance_limits_abs["acceptance_limits_abs_low"],
                    "upper_tol_y_coord": level.tolerance_abs["tolerance_abs_high"],
                    "upper_acc_y_coord": level.acceptance_limits_abs[
                        "acceptance_limits_abs_high"
                    ],
                    "upper_inside": level.tolerance_abs["tolerance_abs_high"]
                                    < level.acceptance_limits_abs["acceptance_limits_abs_high"],
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
                level_tolerance["x_coord"] <= intersects_data.at[index, "x_value"]
                ].iloc[-1]
            point_right: pd.Series = level_tolerance[
                level_tolerance["x_coord"] >= intersects_data.at[index, "x_value"]
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

            opposite_tol: float = vx.get_value_between(
                cur_x_coord,
                [left_x_coord, left_opp_tol],
                [right_x_coord, right_opp_tol],
            )
            opposite_acc: float = vx.get_value_between(
                cur_x_coord,
                [left_x_coord, left_opp_acc],
                [right_x_coord, right_opp_acc],
            )
            cur_acc: float = vx.get_value_between(
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

        if len(intersects_data):  # if there are intersect
            # pick the last one going in that is valid
            if len(
                    intersects_data[
                        (intersects_data["valid"] == 1) & (intersects_data["going_in"] == 1)
                    ]
            ):
                min_loq = intersects_data["x_value"][
                    (intersects_data["valid"] == 1) & (intersects_data["going_in"] == 1)
                    ].iloc[-1]
            elif (
                    level_tolerance.iloc[0]["lower_inside"]
                    and level_tolerance.iloc[0]["upper_inside"]
            ):  # check if first point is in bounds
                min_loq = level_tolerance.iloc[0]["x_coord"]

            # pick the last one going out that has an opposite in
            if len(
                    intersects_data[
                        (intersects_data["opposite_in"] == 1)
                        & (intersects_data["going_in"] == 0)
                    ]
            ):
                max_loq = intersects_data["x_value"][
                    (intersects_data["opposite_in"] == 1)
                    & (intersects_data["going_in"] == 0)
                    ].iloc[-1]
            elif (  # check if the last point is in bounds
                    level_tolerance.iloc[-1]["lower_inside"]
                    and level_tolerance.iloc[-1]["upper_inside"]
            ):
                max_loq = level_tolerance.iloc[-1]["x_coord"]
            if intersects_data.iloc[-1]["valid"]:
                max_loq = level_tolerance.iloc[-1]["x_coord"]

        else:  # no intersect

            if (
                    level_tolerance.iloc[0]["lower_inside"]
                    and level_tolerance.iloc[0]["upper_inside"]
            ):
                # check if first point is between bound, if there are no intersect, the last point should be in bounds
                max_loq = level_tolerance.iloc[-1]["x_coord"]
                min_loq = level_tolerance.iloc[0]["x_coord"]

        # debug check
        if min_loq is not None and max_loq is not None:
            if min_loq > max_loq:  # ensure that the min_loq is smaller than the max_loq
                # temp = min_loq
                # min_loq = max_loq
                # max_loq = temp
                #print("Error here")
                pass

        return [min_loq, max_loq]

    def profile_data(
            self, data_type: str = "", sigfig: int = 4
    ) -> Optional[Union[dict, pd.DataFrame]]:

        if hasattr(self.model, "fit"):
            regression_info = self.get_model_parameter(
                ["params", "rsquared", "f_pvalue"]
            ).applymap(lambda x: roundsf(x, sigfig))
            regression_info['function_string'] = self.get_model_parameter('function_string')
        else:
            regression_info = pd.DataFrame(None)

        model_info = {}

        if hasattr(self.model, "fit"):
            model_info["model_name"] = self.model.name
            model_info["model_formula"] = self.model.formula
            model_info["model_weight"] = self.model.weight
            model_info["number_of_series_calibration"] = len(
                self.model.list_of_series("calibration")
            )
            model_info["number_of_levels_calibration"] = len(
                self.model.list_of_levels("calibration")
            )
            model_info["list_of_series_calibration"] = self.model.list_of_series(
                "calibration"
            ).tolist()
            model_info["list_of_levels_calibration"] = self.model.list_of_levels(
                "calibration"
            ).tolist()
        else:
            model_info["model_name"] = ("Direct",)
            model_info["model_formula"] = ("",)
            model_info["model_weight"] = ""

        model_info.update(
            {
                "lod": roundsf(self.lod, sigfig),
                "lod_type": self.lod_type,
                "min_loq": roundsf(self.min_loq, sigfig),
                "max_loq": roundsf(self.max_loq, sigfig),
                "correction_factor": roundsf(self.correction_factor, sigfig),
                "forced_correction_value": roundsf(
                    self.forced_correction_value, sigfig
                ),
                "has_correction": self.has_correction,
                "has_limits": self.has_limits,
                "number_of_series_validation": len(self.model.list_of_series()),
                "number_of_levels_validation": len(self.model.list_of_levels()),
                "list_of_series_validation": self.model.list_of_series().tolist(),
                "list_of_levels_validation": self.model.list_of_levels().tolist(),
                "absolute_acceptance": self.absolute_acceptance,
                "average_recovery": roundsf(
                    self.average_profile_parameter('recovery').recovery[0], sigfig
                ),
                "units": self.units,
                "compound": self.compound,
                "tolerance": self.tolerance_limit,
                "acceptance": self.acceptance_limit
            }
        )

        linearity_info = pd.DataFrame(self.linearity).applymap(
            lambda x: roundsf(x, sigfig)
        )

        correction_info = pd.DataFrame(self.correction_parameter).applymap(
            lambda x: roundsf(x, sigfig)
        )

        levels_info = self.get_profile_parameter(
            [
                "introduced_concentration",
                "calculated_concentration",
                "acceptance_limits_abs",
                "acceptance_limits_rel",
            ]
        ).applymap(lambda x: roundsf(x, sigfig))

        bias_info = self.get_profile_parameter(
            ["bias_abs", "bias_rel", "recovery"]
        ).applymap(lambda x: roundsf(x, sigfig))

        repeatability_info = self.get_profile_parameter(
            [
                "repeatability_var",
                "repeatability_std",
                "repeatability_cv",
                "intra_series_var",
                "intra_series_std",
                "intra_series_cv",
                "inter_series_var",
                "inter_series_std",
                "inter_series_cv",
            ]
        ).applymap(lambda x: roundsf(x, sigfig))

        intermediate_precision = self.get_profile_parameter(
            [
                "intermediate_precision_var",
                "intermediate_precision_std",
                "intermediate_precision_cv",
            ]
        ).applymap(lambda x: roundsf(x, sigfig))

        total_error = self.get_profile_parameter(
            ["total_error_abs", "total_error_rel"]
        ).applymap(lambda x: roundsf(x, sigfig))

        misc_stats = self.get_profile_parameter(
            ["ratio_var", "b_coefficient", "degree_of_freedom"]
        ).applymap(lambda x: roundsf(x, sigfig))

        tolerance_info = self.get_profile_parameter(
            ["tolerance_std", "tolerance_abs", "tolerance_rel"]
        ).applymap(lambda x: roundsf(x, sigfig))

        uncertainty_info = self.get_profile_parameter(
            ["uncertainty_abs", "uncertainty_rel", "uncertainty_pc"]
        ).applymap(lambda x: roundsf(x, sigfig))

        profile_graphs = {}

        for key, value in self.graphs.items():
            profile_graphs[key] = value.to_dict()

        return_dict = {
            "model_info": model_info,
            "regression_info": regression_info,
            "levels_info": levels_info,
            "bias_info": bias_info,
            "repeatability_info": repeatability_info,
            "intermediate_precision": intermediate_precision,
            "total_error": total_error,
            "misc_stats": misc_stats,
            "tolerance_info": tolerance_info,
            "uncertainty_info": uncertainty_info,
            "correction_info": correction_info,
            "linearity_info": linearity_info,
            "profile_graphs": profile_graphs
        }

        if data_type == "":
            return return_dict
        elif data_type in return_dict:
            return return_dict[data_type]
        else:
            warn(
                "No data of type: "
                + data_type
                + ". The available data types are: "
                + ", ".join(return_dict.keys())
            )
            return None

    def generate_correction(self):
        x_plot: sm.RegressionResults = smf.ols(
            formula="x_calc~x", data=self.model.validation_data
        ).fit()

        intercept: float = x_plot.params["Intercept"]
        slope: float = x_plot.params["x"]

        if self.correction_type == "average":
            self.generate_correction_average()
        else:
            self.generate_correction_slope(slope)

        if self.correction_factor:
            self.correction_parameter = {
                "slope": {"value": slope, "p_value": x_plot.pvalues["x"], "std_error": x_plot.bse["x"]},
                "intercept": {
                    "value": intercept,
                    "p_value": x_plot.pvalues["Intercept"],
                    "std_error": x_plot.bse["Intercept"]
                },
                "rsquared": {"value": x_plot.rsquared, "p_value": x_plot.f_pvalue, "std_error": ""}
            }
            if self.correction_type == "slope" and not self.absolute_acceptance:
                corrected_value: pd.Series = pd.Series(
                    self.model.data_y() * self.correction_factor
                )
                self.model.add_corrected_value_y(
                    corrected_value.map(lambda x: roundsf(x, self.sigfig))
                )
            else:
                corrected_value: pd.Series = pd.Series(
                    self.model.data_x_calc * self.correction_factor
                )
                self.model.add_corrected_value(
                    corrected_value.map(lambda x: roundsf(x, self.sigfig))
                )


    def generate_correction_average(self):
        ratio: float = roundsf(
            np.mean(self.model.data_x_calc / self.model.data_x()), self.sigfig
        )
        if ratio < self.correction_threshold[0] or ratio > self.correction_threshold[1]:
            if self.forced_correction_value is not None:
                self.correction_factor = roundsf(
                    self.forced_correction_value, self.correction_round_to
                )
            else:
                self.correction_factor = roundsf(1 / ratio, self.correction_round_to)
            self.has_correction = 'average'

    def generate_correction_slope(self, slope):
        if slope < self.correction_threshold[0] or slope > self.correction_threshold[1]:
            if self.forced_correction_value is not None:
                self.correction_factor = roundsf(
                    self.forced_correction_value, self.correction_round_to
                )
            else:
                self.correction_factor = roundsf(1 / slope, self.correction_round_to)
            self.has_correction = 'slope'

    def output_profile(
            self, data_type: str = "", format: str = "dict", sigfig: int = 4
    ) -> Optional[str]:

        return_dict = {
            "model_info": self.profile_data("model_info", sigfig),
            "linearity_info": self.profile_data("linearity_info", sigfig).to_dict(),
            "correction_info": self.profile_data("correction_info", sigfig).to_dict(),
            "regression_info": self.profile_data("regression_info", sigfig).to_dict(
                orient="row"
            ),
            "levels_info": self.profile_data("levels_info", sigfig).to_dict(
                orient="row"
            ),
            "bias_info": self.profile_data("bias_info", sigfig).to_dict(orient="row"),
            "repeatability_info": self.profile_data(
                "repeatability_info", sigfig
            ).to_dict(orient="row"),
            "intermediate_precision": self.profile_data(
                "intermediate_precision", sigfig
            ).to_dict(orient="row"),
            "total_error": self.profile_data("total_error", sigfig).to_dict(
                orient="row"
            ),
            "misc_stats": self.profile_data("misc_stats", sigfig).to_dict(orient="row"),
            "tolerance_info": self.profile_data("tolerance_info", sigfig).to_dict(
                orient="row"
            ),
            "uncertainty_info": self.profile_data("uncertainty_info", sigfig).to_dict(
                orient="row"
            ),
            "validation_data": self.model.validation_data.to_dict(orient="row"),
            "graphs": self.profile_data('profile_graphs')
        }

        if self.model.calibration_data is not None:
            return_dict["calibration_data"] = self.model.calibration_data.to_dict(
                orient="row"
            )

        if format == "dict":
            if data_type == "":
                return return_dict
            elif data_type in return_dict:
                return return_dict[data_type]
            else:
                warn(
                    "No data of type: "
                    + data_type
                    + ". The available data types are: "
                    + ", ".join(return_dict.keys())
                )
                return None
        elif format == "json":
            if data_type == "":
                return json.dumps(return_dict)
            elif data_type in return_dict:
                return json.dumps(return_dict[data_type])
            else:
                warn(
                    "No data of type: "
                    + data_type
                    + ". The available data types are: "
                    + ", ".join(return_dict.keys())
                )
                return None
        else:
            warn("Available format are: dict, json")
            return None

    def generate_graphs(self):
        # Linearity graph
        linearity_fig = go.Figure()
        x_data = self.model.validation_data["x"].unique()
        linearity_y = (
                x_data * self.linearity["slope"]["value"]
                + self.linearity["intercept"]["value"]
        )
        linearity_fig.add_trace(
            go.Scatter(x=x_data, y=linearity_y, mode="lines", name="Linearity", )
        )
        for series in self.model.list_of_series():
            linearity_fig.add_trace(
                go.Scatter(
                    x=self.model.get_series(series)["x"],
                    y=self.model.get_series(series)["x_calc"],
                    name="Series " + str(series),
                    mode="markers",
                    marker={"size": 10, "line": {"color": "DarkSlateGrey", "width": 2}},
                )
            )

        linearity_fig.update_layout(
            title={
                'text': 'Linearity Plot',
                'xanchor': 'center',
                'yanchor': 'bottom',
                'y': 0.9,
                'x': 0.5,
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            },
            xaxis_title='Expected (' + self.units + ')',
            yaxis_title='Calculated (' + self.units + ')',
        )
        self.graphs["linearity"] = linearity_fig

        # Correction Graph
        if self.has_correction:
            correction_fig = go.Figure()
            correction_y = (
                    x_data * self.correction_parameter["slope"]["value"]
                    + self.correction_parameter["intercept"]["value"]
            )
            correction_fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=correction_y,
                    mode="lines",
                    name="Linearity",
                )
            )
            for series in self.model.list_of_series():
                correction_fig.add_trace(
                    go.Scatter(
                        x=self.model.get_series(series)["x"],
                        y=self.model.get_series(series)["x_raw"],
                        name="Series " + str(series),
                        mode="markers",
                        marker={
                            "size": 10,
                            "line": {"color": "DarkSlateGrey", "width": 2},
                        },
                    )
                )

            correction_fig.update_layout(
                title={
                    'text': 'Linearity Plot with no correction',
                    'xanchor': 'center',
                    'yanchor': 'bottom',
                    'y': 0.9,
                    'x': 0.5,
                },
                legend={
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1
                },
                xaxis_title='Expected (' + self.units + ')',
                yaxis_title='Calculated (' + self.units + ')',
            )
            self.graphs["correction"] = correction_fig

        # Regression and Residual Graph
        if self.profile_data("regression_info").size > 0:
            regression_fig = go.Figure()
            residual_fig = go.Figure()
            residual_std_fig = go.Figure()
            residual_fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=0,
                x1=1,
                y1=0,
                line={"color": "Green"},
            )
            residual_std_fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=0,
                x1=1,
                y1=0,
                line={"color": "Green"},
            )
            cal_x_data = self.model.calibration_data["x"].unique()
            x_data_spread = np.linspace(cal_x_data.min(), cal_x_data.max(), 100)
            if type(self.model.root_function) == dict:
                for index, regression in self.model.root_function.items():
                    regression_fig.add_trace(
                        go.Scatter(
                            x=x_data_spread,
                            y=list(map(regression, x_data_spread)),
                            mode="lines",
                            name="Series " + str(index),
                        )
                    )
                    residual_fig.add_trace(
                        go.Scatter(
                            x=self.model.fit[index].fittedvalues,
                            y=self.model.fit[index].resid,
                            mode="markers",
                            name="Series " + str(index),
                            marker={
                                "size": 10,
                                "line": {"color": "DarkSlateGrey", "width": 2},
                            },
                        )
                    )
                    residual_std_fig.add_trace(
                        go.Scatter(
                            x=self.model.fit[index].fittedvalues,
                            y=smout.OLSInfluence(self.model.fit[index]).resid_std,
                            mode="markers",
                            name="Series " + str(index),
                            marker={
                                "size": 10,
                                "line": {"color": "DarkSlateGrey", "width": 2},
                            },
                        )
                    )

            else:
                regression_fig.add_trace(
                    go.Scatter(
                        x=x_data_spread,
                        y=list(map(self.model.root_function, x_data_spread)),
                        mode="lines",
                        name="All Series",
                    )
                )
                residual_fig.add_trace(
                    go.Scatter(
                        x=self.model.fit.fittedvalues,
                        y=self.model.fit.resid,
                        mode="markers",
                        name="All Series",
                        marker={
                            "size": 10,
                            "line": {"color": "DarkSlateGrey", "width": 2},
                        },
                    )
                )
                residual_std_fig.add_trace(
                    go.Scatter(
                        x=self.model.fit.fittedvalues,
                        y=smout.OLSInfluence(self.model.fit).resid_std,
                        mode="markers",
                        name="All Series",
                        marker={
                            "size": 10,
                            "line": {"color": "DarkSlateGrey", "width": 2},
                        },
                    )
                )

            for index in self.model.list_of_series('calibration'):
                regression_fig.add_trace(
                    go.Scatter(
                        x=self.model.get_series(index, 'calibration')["x"],
                        y=self.model.get_series(index, 'calibration')["y"],
                        mode="markers",
                        name="Series " + str(index) if self.model.list_of_series(
                            'calibration').size > 1 else "All Series",
                        marker={
                            "size": 10,
                            "line": {"color": "DarkSlateGrey", "width": 2},
                        },
                    )
                )

            regression_fig.update_layout(
                title={
                    'text': 'Regression Plot',
                    'xanchor': 'center',
                    'yanchor': 'bottom',
                    'y': 0.9,
                    'x': 0.5,
                },
                legend={
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1
                },
                xaxis_title='Expected (' + self.units + ')',
                yaxis_title='Signal',
            )
            residual_fig.update_layout(
                title={
                    'text': 'Residual Plot',
                    'xanchor': 'center',
                    'yanchor': 'bottom',
                    'y': 0.9,
                    'x': 0.5,
                },
                legend={
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1
                },
                xaxis_title='Fitted (' + self.units + ')',
                yaxis_title='Residuals',
            )
            residual_std_fig.update_layout(
                title={
                    'text': 'Internally Studentized Residual Plot',
                    'xanchor': 'center',
                    'yanchor': 'bottom',
                    'y': 0.9,
                    'x': 0.5,
                },
                legend={
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': 1.02,
                    'xanchor': 'right',
                    'x': 1
                },
                xaxis_title='Fitted (' + self.units + ')',
                yaxis_title='Internally Studentized Residuals',
            )
            self.graphs["regression"] = regression_fig
            self.graphs["residuals"] = residual_fig
            self.graphs["residuals_std"] = residual_std_fig

        # Profile Graph
        profile_fig = go.Figure()
        profile_data = self.get_profile_parameter(
            [
                "introduced_concentration",
                "recovery",
                "tolerance_rel",
                "acceptance_limits_rel",
            ]
        )
        if self.absolute_acceptance:
            uncertainty = self.get_profile_parameter(["uncertainty_abs"])
        else:
            uncertainty = self.get_profile_parameter(["uncertainty_pc"])

        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=profile_data["recovery"],
                name="Recovery",
                mode="lines",
                error_y={"type": "data", "array": uncertainty, "visible": True},
                line={"color": "green", },
            )
        )
        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=profile_data["tolerance_rel_high"],
                legendgroup="Tolerance",
                name="Tolerance",
                mode="lines",
                line={"color": "blue", },
            )
        )
        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=profile_data["tolerance_rel_low"],
                legendgroup="Tolerance",
                name="Tolerance",
                mode="lines",
                showlegend=False,
                line={"color": "blue", },
            )
        )
        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=profile_data["acceptance_limits_rel_high"],
                legendgroup="Acceptance",
                name="Acceptance limits",
                mode="lines",
                line={"color": "red", "dash": "dash"},
            )
        )
        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=profile_data["acceptance_limits_rel_low"],
                legendgroup="Acceptance",
                name="Acceptance",
                mode="lines",
                showlegend=False,
                line={"color": "red", "dash": "dash"},
            )
        )

        if self.absolute_acceptance:
            y_middle = 0
            bias_type = "bias_abs"
        else:
            y_middle = 100
            bias_type = "bias_rel"

        profile_fig.add_trace(
            go.Scatter(
                x=profile_data["introduced_concentration"],
                y=[y_middle] * profile_data["introduced_concentration"].size,
                legendgroup="Bias",
                name="Bias",
                mode="lines",
                showlegend=False,
                line={"color": "black", "dash": "dash"},
            )
        )

        for series in self.model.list_of_series():
            y_data = y_middle + self.model.get_series(series)[bias_type]
            profile_fig.add_trace(
                go.Scatter(
                    x=self.model.get_series(series)["x"],
                    y=y_data,
                    name="Series " + str(series),
                    mode="markers",
                    marker={"size": 10, "line": {"color": "DarkSlateGrey", "width": 2}},
                )
            )

        profile_fig.update_layout(
            title={
                'text': 'Accuracy Profile',
                'xanchor': 'center',
                'yanchor': 'bottom',
                'y': 0.9,
                'x': 0.5,
            },
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            },
            xaxis_title='Level (' + self.units + ')',
            yaxis_title='Bias',
        )
        self.graphs["profile"] = profile_fig


class ProfileLevel:
    def __init__(
            self,
            level_data: pd.DataFrame,
            absolute_acceptance: bool = False,
            sigfig: int = 4,
            use_median: bool = False
    ):
        self.data: pd.DataFrame = level_data
        self.use_median: bool = use_median
        self.sigfig: int = sigfig
        self.introduced_concentration: Optional[np.float] = None
        self.calculated_concentration: Optional[np.float] = None
        self.bias_abs: Optional[float] = None
        self.bias_rel: Optional[float] = None
        self.recovery: Optional[float] = None
        self.repeatability_var: Optional[float] = None
        self.repeatability_std: Optional[float] = None
        self.repeatability_cv: Optional[float] = None
        self.inter_series_var: Optional[float] = None
        self.inter_series_std: Optional[float] = None
        self.inter_series_cv: Optional[float] = None
        self.total_error_abs: Optional[float] = None
        self.total_error_rel: Optional[float] = None
        self.tolerance_abs: dict = {}
        self.tolerance_rel: dict = {}
        self.acceptance_limits_abs: dict = {}
        self.sum_square_error_intra_series: Optional[float] = None
        self.nb_series: Optional[int] = None
        self.nb_measures: Optional[int] = None
        self.nb_rep: Optional[int] = None
        self.intermediate_precision_var: Optional[float] = None
        self.intermediate_precision_std: Optional[float] = None
        self.intermediate_precision_cv: Optional[float] = None
        self.ratio_var: Optional[float] = None
        self.b_coefficient: Optional[float] = None
        self.degree_of_freedom: Optional[float] = None
        self.tolerance_std: Optional[float] = None
        self.uncertainty_abs: Optional[float] = None
        self.uncertainty_rel: Optional[float] = None
        self.uncertainty_pc: Optional[float] = None
        self.cover_factor: Optional[float] = None
        self.absolute_acceptance: bool = absolute_acceptance
        self.intra_series_var: Optional[float] = None
        self.intra_series_std: Optional[float] = None
        self.intra_series_cv: Optional[float] = None

    def calculate(self, tolerance_limit: float, acceptance_limit: float) -> None:
        self.nb_series = self.data["Series"].nunique()
        self.nb_measures = len(self.data.index)
        self.nb_rep = self.nb_measures / self.nb_series

        if self.use_median:
            self.introduced_concentration = roundsf(self.data["x"].median(), self.sigfig)
        else:
            self.introduced_concentration = roundsf(self.data["x"].mean(), self.sigfig)

        self.calculated_concentration = roundsf(self.data["x_calc"].mean(), self.sigfig)
        self.acceptance_limits_abs = self.get_acceptance_limits_abs(
            acceptance_limit
        ).map(lambda x: roundsf(x, self.sigfig))
        self.acceptance_limits_rel = self.get_acceptance_limits_rel(
            acceptance_limit
        ).map(lambda x: roundsf(x, self.sigfig))

        self.bias_abs = roundsf(
            self.calculated_concentration - self.introduced_concentration, self.sigfig
        )
        try:
            self.bias_rel = roundsf(
                (self.bias_abs / self.introduced_concentration) * 100, self.sigfig
            )
        except ZeroDivisionError:
            self.bias_rel = "N/A"
        self.bias_abs_n = roundsf(self.data["bias_abs"].mean(), self.sigfig)
        self.bias_rel_n = roundsf(self.data["bias_rel"].mean(), self.sigfig)
        self.recovery = roundsf(self.get_recovery(), self.sigfig)

        self.repeatability_var = roundsf(self.get_repeatability_var, self.sigfig)
        self.repeatability_std = roundsf(math.sqrt(self.repeatability_var), self.sigfig)
        try:
            self.repeatability_cv = roundsf(
                self.repeatability_std / self.introduced_concentration * 100, self.sigfig
            )
        except ZeroDivisionError:
            self.repeatability_cv = "N/A"

        self.intra_series_var = roundsf(self.repeatability_var, self.sigfig)
        self.intra_series_std = roundsf(self.repeatability_std, self.sigfig)
        self.intra_series_cv = roundsf(self.repeatability_cv, self.sigfig)

        self.inter_series_var = roundsf(self.get_inter_series_var, self.sigfig)
        self.inter_series_std = roundsf(math.sqrt(self.inter_series_var), self.sigfig)
        self.inter_series_cv = roundsf(
            self.inter_series_std / self.calculated_concentration * 100, self.sigfig
        )
        self.intermediate_precision_var = roundsf(
            self.repeatability_var + self.inter_series_var, self.sigfig
        )
        self.intermediate_precision_std = roundsf(
            math.sqrt(self.intermediate_precision_var), self.sigfig
        )
        try:
            self.intermediate_precision_cv = roundsf(
                self.intermediate_precision_std / self.introduced_concentration * 100,
                self.sigfig,
            )
        except ZeroDivisionError:
            self.intermediate_precision_cv = "N/A"

        self.total_error_abs = roundsf(
            abs(self.bias_abs) + abs(self.intermediate_precision_std), self.sigfig
        )
        try:
            self.total_error_rel = roundsf(
                self.total_error_abs / self.introduced_concentration * 100, self.sigfig
            )
        except ZeroDivisionError:
            self.total_error_rel = "N/A"

        self.ratio_var = roundsf(self.get_ratio_var, self.sigfig)

        self.b_coefficient = roundsf(
            math.sqrt((self.ratio_var + 1) / (self.nb_rep * self.ratio_var + 1)),
            self.sigfig,
        )
        self.degree_of_freedom = roundsf(
            (self.ratio_var + 1) ** 2
            / (
                    (self.ratio_var + (1 / self.nb_rep)) ** 2 / (self.nb_series - 1)
                    + (1 - (1 / self.nb_rep)) / self.nb_measures
            ),
            self.sigfig,
        )
        self.tolerance_std = roundsf(
            self.intermediate_precision_std
            * (math.sqrt(1 + (1 / (self.nb_measures * self.b_coefficient)))),
            self.sigfig,
        )
        self.tolerance_abs = self.get_absolute_tolerance(tolerance_limit).map(
            lambda x: roundsf(x, self.sigfig)
        )
        self.tolerance_rel = self.get_tolerance_rel().map(
            lambda x: roundsf(x, self.sigfig)
        )

        self.uncertainty_abs = roundsf(self.tolerance_std * 2, self.sigfig)
        self.uncertainty_rel = roundsf(
            self.uncertainty_abs / self.calculated_concentration, self.sigfig
        )

        try:
            self.uncertainty_pc = roundsf(
                self.uncertainty_abs / self.introduced_concentration * 100, self.sigfig
            )
        except ZeroDivisionError:
            self.uncertainty_pc = "N/A"

    def get_recovery(self) -> float:
        if self.absolute_acceptance:
            return self.bias_abs
        else:
            try:
                return (self.calculated_concentration / self.introduced_concentration) * 100
            except ZeroDivisionError:
                return 0

    def get_tolerance_rel(self) -> pd.Series:
        if self.absolute_acceptance:
            return pd.Series(
                {
                    "tolerance_rel_low": self.tolerance_abs["tolerance_abs_low"]
                                         - self.introduced_concentration,
                    "tolerance_rel_high": self.tolerance_abs["tolerance_abs_high"]
                                          - self.introduced_concentration,
                }
            )
        else:
            return pd.Series(
                {
                    "tolerance_rel_low": self.tolerance_abs["tolerance_abs_low"]
                                         / self.introduced_concentration
                                         * 100,
                    "tolerance_rel_high": self.tolerance_abs["tolerance_abs_high"]
                                          / self.introduced_concentration
                                          * 100,
                }
            )

    def get_acceptance_limits_abs(self, acceptance_limit: float) -> pd.Series:
        if self.absolute_acceptance:
            introduced_limit: float = acceptance_limit
        else:
            introduced_limit: float = acceptance_limit / 100 * self.introduced_concentration
        return pd.Series(
            {
                "acceptance_limits_abs_low": self.introduced_concentration
                                             - introduced_limit,
                "acceptance_limits_abs_high": self.introduced_concentration
                                              + introduced_limit,
            }
        )

    def get_acceptance_limits_rel(self, acceptance_limit: float) -> pd.Series:
        if self.absolute_acceptance:
            return pd.Series(
                {
                    "acceptance_limits_rel_low": 0 - acceptance_limit,
                    "acceptance_limits_rel_high": 0 + acceptance_limit,
                }
            )
        else:
            return pd.Series(
                {
                    "acceptance_limits_rel_low": 100 - acceptance_limit,
                    "acceptance_limits_rel_high": 100 + acceptance_limit,
                }
            )

    def get_absolute_tolerance(self, tolerance_limit: float) -> pd.Series:

        student = t.ppf(
            (1 + (tolerance_limit / 100)) / 2, np.float32(self.degree_of_freedom)
        )

        self.cover_factor = student * math.sqrt(
            1 + (1 / (self.nb_measures * np.power(self.b_coefficient, 2)))
        )

        tolerance_low = (
                self.calculated_concentration
                - self.cover_factor * self.intermediate_precision_std
        )

        tolerance_high = (
                self.calculated_concentration
                + self.cover_factor * self.intermediate_precision_std
        )

        if self.absolute_acceptance:
            tolerance_low = tolerance_low
            tolerance_high = tolerance_high

        return pd.Series(
            {"tolerance_abs_low": tolerance_low, "tolerance_abs_high": tolerance_high}
        )

    @property
    def mean_square_model(self) -> float:
        mean_x_level = self.data["x_calc"].mean()
        mean_x_level_series = [
            self.data[self.data["Series"] == series]["x_calc"].mean()
            for series in self.data["Series"].unique()
        ]
        number_item_in_series = [
            len(self.data[self.data["Series"] == series])
            for series in self.data["Series"].unique()
        ]
        number_of_series = self.data["Series"].nunique()

        return (1 / (number_of_series - 1)) * np.sum(
            np.multiply(
                number_item_in_series,
                np.power(np.subtract(mean_x_level_series, mean_x_level), 2),
            )
        )

    @property
    def mean_square_error(self) -> float:
        mean_x_level_series = [
            self.data[self.data["Series"] == series]["x_calc"].mean()
            for series in self.data["Series"].unique()
        ]
        number_item_in_series = [
            len(self.data[self.data["Series"] == series])
            for series in self.data["Series"].unique()
        ]
        number_of_series = self.data["Series"].nunique()
        x_calc = [
            self.data[self.data["Series"] == series]["x_calc"]
            for series in self.data["Series"].unique()
        ]

        return (1 / (np.sum(number_item_in_series) - number_of_series)) * np.sum(
            [
                np.sum(
                    np.power(
                        np.subtract(
                            x_calc[mean_x_level_series.index(mean_series)], mean_series
                        ),
                        2,
                    )
                )
                for mean_series in mean_x_level_series
            ]
        )

    @property
    def get_inter_series_var(self) -> float:
        number_item_in_series = [
            len(self.data[self.data["Series"] == series])
            for series in self.data["Series"].unique()
        ]
        if self.mean_square_error < self.mean_square_model:
            inter_series_var = (
                                       self.mean_square_model - self.mean_square_error
                               ) / number_item_in_series[0]
        else:
            inter_series_var = 0

        return inter_series_var

    @property
    def sum_of_square_residual(self) -> np.ndarray:
        mean_x_level_series = [
            self.data[self.data["Series"] == series]["x_calc"].mean()
            for series in self.data["Series"].unique()
        ]
        x_calc = [
            self.data[self.data["Series"] == series]["x_calc"]
            for series in self.data["Series"].unique()
        ]

        return np.sum(
            [
                np.sum(
                    np.power(
                        np.subtract(
                            x_calc[mean_x_level_series.index(mean_series)], mean_series
                        ),
                        2,
                    )
                )
                for mean_series in mean_x_level_series
            ]
        )

    @property
    def sum_of_square_total(self) -> np.ndarray:
        mean_x_level = self.data["x_calc"].mean()
        mean_x_level_series = [
            self.data[self.data["Series"] == series]["x_calc"].mean()
            for series in self.data["Series"].unique()
        ]
        number_item_in_series = [
            len(self.data[self.data["Series"] == series])
            for series in self.data["Series"].unique()
        ]

        return np.sum(
            np.multiply(
                number_item_in_series,
                np.power(np.subtract(mean_x_level_series, mean_x_level), 2),
            )
        )

    @property
    def get_repeatability_var(self) -> float:
        if self.mean_square_error < self.mean_square_model:
            repeatability_var = self.mean_square_error
        else:
            mean_x_level = self.data["x_calc"].mean()
            number_item_in_series = [
                len(self.data[self.data["Series"] == series])
                for series in self.data["Series"].unique()
            ]
            number_of_series = self.data["Series"].nunique()
            x_calc = self.data["x_calc"]

            repeatability_var = (
                                        1 / (number_item_in_series[0] * number_of_series - 1)
                                ) * np.sum(np.power(np.subtract(x_calc, mean_x_level), 2))

        return repeatability_var

    @property
    def get_ratio_var(self) -> float:
        if self.inter_series_var == 0 or self.repeatability_var == 0:
            ratio_var = 0
        else:
            ratio_var = self.inter_series_var / self.repeatability_var

        return ratio_var


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
            "average.bias_abs": self.__get_average_bias_abs,
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

    def __get_average_bias_abs(self) -> pd.DataFrame:
        return self.__get_profile_average("bias_abs")

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

    def __get_profile_average(self, parameter) -> pd.DataFrame:
        return_value: pd.DataFrame = pd.DataFrame()
        for profile_type in self.profiles.keys():
            for key, profile in enumerate(self.profiles[profile_type]):
                temp_dataframe = pd.DataFrame(
                    [
                        [
                            profile_type,
                            key,
                            profile.average_profile_parameter(parameter)[parameter][0],
                        ]
                    ],
                    columns=["Model", "Index", "average." + parameter],
                )
                return_value = return_value.append(temp_dataframe, ignore_index=True)
        return return_value

    @property
    def available_parameters(self):
        return self.parameter_function.keys()
