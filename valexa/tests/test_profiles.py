import pytest
from unittest.mock import Mock

from valexa.core.profiles import make_profiles, Profile, Intersect, Direction
from valexa.core.models import Result, Model


@pytest.fixture()
def calib_data():
    return [
        (1, 1, 0.1, 0.012),
        (1, 2, 5.0, 0.68),
        (1, 3, 10.0, 1.34),
        (2, 1, 0.1, 0.013),
        (2, 2, 5.0, 0.70),
        (2, 3, 10.0, 1.42),

    ]


@pytest.fixture()
def valid_data():
    return [
        (1, 1, 0.1, 0.013),
        (1, 2, 5.0, 0.70),
        (1, 3, 10.0, 1.24),
        (2, 1, 0.1, 0.016),
        (2, 2, 5.0, 0.72),
        (2, 3, 10.0, 1.37),

    ]


def test_make_profiles_returns_profiles(calib_data, valid_data):
    tolerance_limit = 80
    acceptance_limit = 20

    profiles = make_profiles(calib_data, valid_data, tolerance_limit, acceptance_limit)

    assert profiles


def test_make_profiles_calls_profile_calculate_with_tolerance_limit_and_acceptance_limit(calib_data, valid_data,
                                                                                         mocker):
    tolerance_limit = 80
    acceptance_limit = 20
    calculate_mock: Mock = mocker.patch('valexa.core.profiles.Profile.calculate')

    make_profiles(calib_data, valid_data, tolerance_limit, acceptance_limit)

    calculate_mock.assert_called_with(tolerance_limit, acceptance_limit)


class TestProfile:
    results_without_repetition = [
        Result(1, 1, 0.1, 0.09),
        Result(1, 2, 5.0, 5.1),
        Result(1, 3, 10.0, 10.5),
        Result(2, 1, 0.1, 0.11),
        Result(2, 2, 5.0, 5.0),
        Result(2, 3, 10.0, 10.4),
    ]

    results_with_repetition = [
        Result(1, 1, 0.1, 0.09),
        Result(1, 1, 0.1, 0.08),
        Result(1, 2, 5.0, 5.1),
        Result(1, 2, 5.0, 5.2),
        Result(1, 3, 10.0, 10.5),
        Result(1, 3, 10.0, 10.4),
        Result(2, 1, 0.1, 0.11),
        Result(2, 1, 0.1, 0.10),
        Result(2, 2, 5.0, 5.0),
        Result(2, 2, 5.0, 5.1),
        Result(2, 3, 10.0, 10.4),
        Result(2, 3, 10.0, 10.2),
    ]

    @pytest.fixture()
    def model_without_rep(self):
        model = Model()
        model.series_calculated = self.results_without_repetition
        return model

    @pytest.fixture()
    def model_with_rep(self):
        model = Model()
        model.series_calculated = self.results_with_repetition
        return model

    def test_create_from_a_model_results_calculate_levels_from_series(self, model_without_rep):
        profile = Profile(model_without_rep)

        assert len(profile.levels) == 3
        assert len(profile.levels[0].series) == 2

    @pytest.mark.parametrize("results", [results_with_repetition, results_without_repetition],
                             ids=["without_rep", "with_rep"])
    def test_calculate_generate_values_to_make_accuracy_profile(self, results):
        model = Model()
        model.series_calculated = results
        tolerance_limit = 80
        profile = Profile(model)

        profile.calculate(tolerance_limit)

        assert profile.acceptance_interval
        for l in profile.levels:
            assert l.introduced_concentration
            assert l.calculated_concentration
            assert l.bias is not None
            assert l.relative_bias is not None
            assert l.recovery
            assert l.repeatability_var is not None
            assert l.repeatability_std is not None
            assert l.inter_series_var is not None
            assert l.inter_series_std is not None
            assert l.abs_tolerance
            assert l.rel_tolerance

    def test_calculate_limits_of_quantification_and_detection(self, model_with_rep):
        tolerance_limit = 80
        profile = Profile(model_with_rep)

        profile.calculate(tolerance_limit)

        assert profile.min_lq
        assert profile.max_lq
        assert round(profile.ld, 3) == round(profile.min_lq / 3.3, 3)

    def test_get_limits_from_intersects(self, model_with_rep):
        accept_limit = 20
        profile = Profile(model_with_rep)
        intersects_low = [
            Intersect(2, Direction.IN),
            Intersect(3, Direction.OUT),
            Intersect(6, Direction.IN)
        ]
        intersects_high = [
            Intersect(2, Direction.OUT),
            Intersect(3, Direction.IN),
            Intersect(4, Direction.OUT)
        ]

        lower_limits = profile.get_limits_from_intersects(intersects_low, accept_limit, Profile.LIMIT_LOWER)
        upper_limits = profile.get_limits_from_intersects(intersects_high, accept_limit, Profile.LIMIT_UPPER)

        assert lower_limits == (2, 3)
        assert upper_limits == (3, 4)

    def test_group_intersect_by_in_out(self, model_with_rep):
        profile = Profile(model_with_rep)
        in1 = Intersect(2, Direction.OUT)
        in2 = Intersect(3, Direction.IN)
        in3 = Intersect(4, Direction.OUT)
        intersects_high = [in1, in2, in3]

        expected = profile.group_intersects_by_in_out(intersects_high)

        assert expected == [(in2, in3)]

    def test_get_most_restrictive_limits(self, model_with_rep):
        profile = Profile(model_with_rep)
        lower_limits = (2, 4)
        upper_limits = (3, 6)

        limits = profile.get_most_restrictive_limits(lower_limits, upper_limits)

        assert limits == (3, 4)
