from typing import List, Tuple

import numpy as np
from collections import namedtuple

from valexa.core.standard import Standard, Entry

Result = namedtuple('Result', ['series', 'level', 'concentration', 'result'])


class Model:
    NAME_BY_DEGREE = {
        1: "Linear",
        2: "Quadratic"
    }

    def __init__(self):
        self.degree: int = None
        self.series_params = {}
        self.series_calculated: List[Result] = []
        self.has_correction: bool = False
        self.correction_factor: float = 1.0

    @property
    def name(self) -> str:
        try:
            return self.NAME_BY_DEGREE[self.degree]
        except KeyError:
            return "Unknown model"

    def handle_correction(self):
        recoveries = [(s.result / s.concentration) * 100 for s in self.series_calculated]
        recovery_avg: float = np.mean(recoveries)

        if abs(100 - recovery_avg) >= 15:
            self.has_correction = True
            self.correction_factor = round(1 / (recovery_avg / 100), 1)
            self.__apply_correction()

    def __apply_correction(self):
        corrected_results = []
        for s in self.series_calculated:
            value_corrected = s.result * self.correction_factor
            corrected_results.append(s._replace(result=value_corrected))

        self.series_calculated = corrected_results


class ModelHandler:
    DEFAULT_MAX_DEGREE = 2

    def __init__(self, calib_std: Standard, valid_std: Standard):
        self.calib_std = calib_std
        self.valid_std = valid_std

    def get_models(self, max_degree: int = DEFAULT_MAX_DEGREE) -> List[Model]:
        models = []
        for degree in range(1, max_degree + 1):
            model = Model()
            model.degree = degree
            for (key, entries) in self.calib_std.series.items():
                parameters = self.__get_model_params(degree, entries)
                model.series_params[key] = parameters
                model.series_calculated.extend(self.__apply_params_to_series(key, parameters))
            model.handle_correction()
            models.append(model)
        return models

    def __get_model_params(self, degree: int, entries: List[Entry]) -> Tuple:
        x_value = [e.concentration for e in entries]
        y_value = [e.response for e in entries]
        parameters = np.polyfit(x_value, y_value, degree)

        return parameters

    def __apply_params_to_series(self, index: int, parameters) -> List[Result]:
        results = []
        for entry in self.valid_std.series[index]:
            p_func = np.poly1d(parameters)
            result_value = (p_func - entry.response).roots[-1]
            result = Result(entry.series, entry.level, entry.concentration, result_value)
            results.append(result)

        return results
