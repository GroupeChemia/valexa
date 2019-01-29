from collections import defaultdict
from enum import Enum
from operator import attrgetter
from typing import List, Dict

from scipy.stats import t

import math
import numpy as np

import io

from valexa.core.standard import Standard
from valexa.core.models import Result, ModelHandler, Model

DEFAULT_TOLERANCE = 80
DEFAULT_ACCEPTANCE = 50


def make_profiles(calib_data: List[tuple], valid_data: List[tuple], tolerance_limit: int,
                  acceptance_limit: int, file_name: str) -> List:
    std_calib = Standard(calib_data)
    std_valid = Standard(valid_data)
    model_handler = ModelHandler(std_calib, std_valid)

    models = model_handler.get_models()

    profiles = []
    for model in models:
        profile = Profile(model)
        profile.name_of_file = file_name
        profile.tolerance_limit = tolerance_limit
        profile.acceptance_limit = acceptance_limit
        profile.calculate(tolerance_limit, acceptance_limit)
        profiles.append(profile)

    return profiles


class ProfileLevel:
    def __init__(self, index):
        self.index = index
        self.series: List[Result] = []
        self.introduced_concentration: float = None
        self.calculated_concentration: float = None
        self.bias: float = None
        self.relative_bias: float = None
        self.recovery: float = None
        self.repeatability_var: float = None
        self.repeatability_std: float = None
        self.repeatability_std_pc: float = None
        self.inter_series_var: float = None
        self.inter_series_std: float = None
        self.inter_series_std_pc: float = None
        self.intermediate_precision_std: float = None
        self.abs_tolerance: List[float] = []
        self.rel_tolerance: List[float] = []
        self.acceptance_interval: List[float] = []
        self.sum_square_error_intra_series: float = None
        self.series_by_group: Dict = {}
        self.nb_series: int = None
        self.nb_measures: int = None
        self.nb_rep: int = None

    def __series_by_group(self) -> Dict:
        series_group = defaultdict(list)
        for s in self.series:
            series_group[s.series].append(s)

        return series_group

    def add_result(self, result):
        self.series.append(result)

    def calculate(self, tolerance_limit: int = DEFAULT_TOLERANCE):
        self.series_by_group = self.__series_by_group()
        self.nb_series = len(self.series_by_group.keys())
        self.nb_measures = len(self.series)
        self.nb_rep = self.nb_measures / self.nb_series
        self.introduced_concentration = np.mean([s.concentration for s in self.series])
        self.calculated_concentration = np.mean([s.result for s in self.series])
        self.bias = self.calculated_concentration - self.introduced_concentration
        self.relative_bias = (self.bias / self.introduced_concentration) * 100
        self.recovery = (self.calculated_concentration / self.introduced_concentration) * 100
        self.repeatability_var = self.get_repeatability_var()
        self.repeatability_std = np.sqrt(self.repeatability_var)
        self.repeatability_std_pc = self.repeatability_std/self.calculated_concentration * 100
        self.inter_series_var = self.get_inter_series_var()
        self.inter_series_std = np.sqrt(self.inter_series_var)
        self.inter_series_std_pc = self.inter_series_std / self.calculated_concentration * 100
        self.abs_tolerance = self.get_absolute_tolerance(tolerance_limit)
        self.rel_tolerance = [(tol / self.introduced_concentration) * 100 for tol in self.abs_tolerance]

    def get_repeatability_var(self) -> float:
        repeatability_var = 0
        sum_square_errors = 0
        for (k, series) in self.series_by_group.items():
            series_mean_result = np.mean([s.result for s in series])
            sum_square_errors += np.sum([(rep.result - series_mean_result) ** 2 for rep in series])
        self.sum_square_error_intra_series = sum_square_errors

        if sum_square_errors > 0:
            repeatability_var = sum_square_errors / (self.nb_series * (self.nb_rep - 1))
        return repeatability_var

    def get_inter_series_var(self) -> float:
        sum_square_errors_total = np.sum([(s.result - self.calculated_concentration) ** 2 for s in self.series])
        sum_square_errors_inter_series = sum_square_errors_total - self.sum_square_error_intra_series

        if sum_square_errors_inter_series <= 0:
            return 0

        inter_series_var: float = ((sum_square_errors_inter_series / (
                self.nb_series - 1)) - self.repeatability_var) / self.nb_rep
        if inter_series_var < 0:
            return 0

        return inter_series_var

    def get_absolute_tolerance(self, tolerance_limit: int) -> List[float]:
        fidelity_var = np.sum([self.repeatability_var, self.inter_series_var])
        fidelity_std = np.sqrt(fidelity_var)
        if self.inter_series_var == 0 or self.repeatability_var == 0:
            ratio_var = 0
        else:
            ratio_var = self.inter_series_var / self.repeatability_var

        b_coefficient = (ratio_var + 1) / (self.nb_rep * ratio_var + 1)
        degree_of_freedom = (ratio_var + 1) ** 2 / ((ratio_var + (1 / self.nb_rep)) ** 2 / (self.nb_series - 1) + (
                1 - (1 / self.nb_rep)) / self.nb_measures)
        student_low = t.ppf(1 - ((1 - (tolerance_limit / 100)) / 2), math.floor(degree_of_freedom))
        student_high = t.ppf(1 - ((1 - (tolerance_limit / 100)) / 2), math.ceil(degree_of_freedom))

        cover_factor = student_low - (student_low - student_high) * (degree_of_freedom - math.floor(degree_of_freedom))
        tolerance_std = fidelity_std * (np.sqrt(1 + (1 / (self.nb_measures * b_coefficient))))
        tolerance_low = self.calculated_concentration - cover_factor * tolerance_std
        tolerance_high = self.calculated_concentration + cover_factor * tolerance_std

        return [tolerance_low, tolerance_high]


class Direction(Enum):
    IN = 1
    OUT = 2


class Intersect:

    def __init__(self, value: float, direction: Direction):
        self.value = value
        self.direction = direction


class Profile:
    LIMIT_LOWER = 0
    LIMIT_UPPER = 1

    def __init__(self, model: Model):
        self.model = model
        self.series = model.series_calculated
        self.levels: List[ProfileLevel] = []
        self.acceptance_interval: List[float] = []
        self.min_lq: float = None
        self.max_lq: float = None
        self.ld: float = None
        self.has_limits = False
        self.name_of_file: str = None
        self.acceptance_limit: int = None
        self.tolerance_limit: int = None
        self.image_data = None

        self.__split_series_by_levels()
        self.levels.sort(key=attrgetter('index'))

    def __split_series_by_levels(self):
        for s in self.series:
            try:
                level = [level for level in self.levels if level.index == s.level][0]
                level.add_result(s)
            except IndexError:
                level = ProfileLevel(index=s.level)
                level.add_result(s)
                self.levels.append(level)

    def calculate(self, tolerance_limit: int = DEFAULT_TOLERANCE, acceptance_limit: int = DEFAULT_ACCEPTANCE):
        self.acceptance_interval = [(1 - (acceptance_limit / 100)) * 100, (1 + (acceptance_limit / 100)) * 100]
        for level in self.levels:
            level.calculate(tolerance_limit)
        try:
            self.min_lq, self.max_lq = self.get_limits_of_quantification(acceptance_limit)
            self.ld = self.min_lq / 3.3
            self.has_limits = True
        except ValueError as e:
            print(e)
            self.min_lq = None
            self.max_lq = None
            self.ld = None

    def get_limits_of_quantification(self, acceptance_limit: int) -> (float, float):
        print('LOQ START')
        intersects_low = []
        intersects_high = []

        for l in range(len(self.levels) - 1):
            level_a = self.levels[l]
            level_b = self.levels[l + 1]
            lower_intersect = self.get_intersect_between_levels(level_a, level_b, acceptance_limit, self.LIMIT_LOWER)
            upper_intersect = self.get_intersect_between_levels(level_a, level_b, acceptance_limit, self.LIMIT_UPPER)
            if lower_intersect:
                intersects_low.append(lower_intersect)
            if upper_intersect:
                intersects_high.append(upper_intersect)

        lower_limits = self.get_limits_from_intersects(intersects_low, acceptance_limit, self.LIMIT_LOWER)
        print('LINTER MID')
        upper_limits = self.get_limits_from_intersects(intersects_high, acceptance_limit, self.LIMIT_UPPER)

        print('LINTER END')
        limits = self.get_most_restrictive_limits(lower_limits, upper_limits)

        print('LIMIT PASS')
        print('LOQ')
        return limits

    def get_intersect_between_levels(self, level_a, level_b, accept_limit: int, limit_type) -> Intersect:
        level_a_tol = level_a.abs_tolerance[limit_type]
        level_b_tol = level_b.abs_tolerance[limit_type]
        if limit_type == self.LIMIT_LOWER:
            lambda_accept = 1 - (accept_limit / 100)
        elif limit_type == self.LIMIT_UPPER:
            lambda_accept = 1 + (accept_limit / 100)
        else:
            raise ValueError("Limit type not valid. Valid options are: Profile.LOWER_LIMIT or Profile.UPPER_LIMIT")

        level_a_accept_limit = level_a.introduced_concentration * lambda_accept
        level_b_accept_limit = level_b.introduced_concentration * lambda_accept

        tol_slope = (level_b_tol - level_a_tol) / (
                level_b.introduced_concentration - level_a.introduced_concentration)
        tol_origin = level_a_tol - tol_slope * level_a.introduced_concentration

        accept_slope = (level_b_accept_limit - level_a_accept_limit) / (
                level_b.introduced_concentration - level_a.introduced_concentration)
        accept_origin = level_a_accept_limit - accept_slope * level_a.introduced_concentration

        value = (accept_origin - tol_origin) / (tol_slope - accept_slope)
        if value > level_b.introduced_concentration or value < level_a.introduced_concentration:
            return None

        if level_a_tol >= level_a_accept_limit and level_b_tol < level_b_accept_limit:
            if limit_type == self.LIMIT_LOWER:
                direction = Direction.OUT
            else:
                direction = Direction.IN
        elif level_a_tol < level_a_accept_limit and level_b_tol >= level_b_accept_limit:
            if limit_type == self.LIMIT_LOWER:
                direction = Direction.IN
            else:
                direction = Direction.OUT
        else:
            raise ValueError("Cannot identify intersect's direction")

        return Intersect(value, direction)

    def get_limits_from_intersects(self, intersects: List[Intersect], accept_limit: int, limit_type: int) -> (
            float, float):

        print('LINTER START')
        if len(intersects) == 0:
            low_accept_limit_rel = (1 - (accept_limit / 100)) * 100
            high_accept_limit_rel = (1 + (accept_limit / 100)) * 100
            mean_tolerance = np.mean([l.rel_tolerance[limit_type] for l in self.levels])
            if low_accept_limit_rel <= mean_tolerance <= high_accept_limit_rel:
                limits = (self.levels[0].introduced_concentration, self.levels[-1].introduced_concentration)
            else:
                raise ValueError("Not valid limit of quantification detected")
        elif len(intersects) == 1 and intersects[0].direction == Direction.IN:
            limits = (intersects[0].value, self.levels[-1].introduced_concentration)
        elif len(intersects) == 1 and intersects[0].direction == Direction.OUT:
            limits = (self.levels[0].introduced_concentration, intersects[0].value)
        elif len(intersects) == 2:
            if intersects[0].direction == Direction.IN and intersects[1].direction == Direction.OUT:
                limits = (intersects[0].value, intersects[1].value)
            elif intersects[0].direction == Direction.OUT and intersects[1].direction == Direction.IN:
                limits = (intersects[1].value, self.levels[-1].introduced_concentration)
            else:
                raise ValueError("Intersects pair not valid: possible values (IN, OUT) or (OUT, IN)")
        elif len(intersects) > 2:
            in_out_pairs = self.group_intersects_by_in_out(intersects)
            if len(in_out_pairs) == 1:
                min_limit = in_out_pairs[0][0].value
                max_limit = in_out_pairs[0][1].value
                limits = (min_limit, max_limit)
            elif len(in_out_pairs) > 1:
                min_limit = in_out_pairs[-1][0].value
                max_limit = in_out_pairs[-1][1].value
                limits = (min_limit, max_limit)
        else:
            raise ValueError("Cannot define limits from intersects")

        print('LINTER')
        return limits

    def group_intersects_by_in_out(self, intersects: List[Intersect]) -> List:
        in_out_pairs = []
        current_in_intersect = None
        for i in intersects:
            if i.direction == Direction.IN:
                current_in_intersect = i
            elif current_in_intersect and i.direction == Direction.OUT:
                in_out_pairs.append((current_in_intersect, i))
                current_in_intersect = None
        return in_out_pairs

    def get_most_restrictive_limits(self, lower_limits, upper_limits) -> (float, float):
        min_limit = max(lower_limits[0], upper_limits[0])
        max_limit = min(lower_limits[1], upper_limits[1])

        return min_limit, max_limit

    def make_plot(self, ax):
        levels_x = [l.calculated_concentration for l in self.levels]
        ax.axis["bottom", "top", "right"].set_visible(False)
        ax.axis["y=100"] = ax.new_floating_axis(nth_coord=0, value=100)
        ax.plot(levels_x, [l.recovery for l in self.levels], color="m", linewidth=2.0, marker=".", label="Recovery")
        ax.plot(levels_x, [l.rel_tolerance[0] for l in self.levels], linewidth=1.0, color="b",
                label="Min tolerance limit")
        ax.plot(levels_x, [l.rel_tolerance[1] for l in self.levels], linewidth=1.0, color="g",
                label="Max tolerance limit")
        ax.plot(levels_x, [self.acceptance_interval[0] for _ in self.levels], "k--", label="Acceptance limit")
        ax.plot(levels_x, [self.acceptance_interval[1] for _ in self.levels], "k--")
        results_x = [s.concentration for s in self.series]
        results_y = [(s.result / s.concentration) * 100 for s in self.series]
        ax.scatter(results_x, results_y, alpha=0.5, s=2)
        ax.set_xlabel("Concentration")
        ax.set_ylabel("Recovery (%)")
        ax.legend(loc=1)

