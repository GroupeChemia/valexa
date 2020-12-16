from valexa.profiles import ProfileManager
from valexa.examples.dataset import sample_dataset
import numpy as np
import pandas as pd


def test_feinberg_coli():
    """
    Dataset from Feinberg, M. et al., Validation of Alternative Methods for the Analysis of Drinking Water and Their
    Application to Escherichia coli (2011), https://dx.doi.org/10.1128/AEM.00020-11

    This is an example of validation with absolute unit, in this case a bacterial count.
    Here the raw data are manipulated before being passed to the algorithm. They are transformed in their log10
    equivalent and the target level are using the median instead of the mean. Please refer to the article for more
    information.

    The reference DataFrame is as follow:

         | repeatability_std | inter_series_std | tolerance_std | bias  | abs_tolerance_low | abs_tolerance_high
    -----+-------------------+------------------+---------------+-------+-------------------+--------------------
      1  | 0.141             | 0.092            | 0.173         | 0.024 | -0.206            | 0.254
    -----+-------------------+------------------+---------------+-------+-------------------+--------------------
      2  | 0.093             | 0.081            | 0.127         | 0.055 | -0.115            | 0.225
    -----+-------------------+------------------+---------------+-------+-------------------+--------------------
      3  | 0.099             | 0.141            | 0.178         | 0.093 | -0.147            | 0.333

    Note: the kM value given in the article is equivalent to kIT * sqrt(1 + (1/(nb_measures * b_coefficient)), the
    tolerance interval obtained stays the same since Valexa add this factor in the calculation of the tolerance standard
    deviation instead of the calculation of the coverage factor as found in the article. In the same way, the sFI needs
    to be divided by the same equation.
    """
    data = sample_dataset.dataset("feinberg_coli")

    profiles: ProfileManager = ProfileManager(
        "Test", data, acceptance_absolute=True, acceptance_limit=0.3, data_transformation="log10", use_median=True
    )
    profiles.make_profiles()

    data = sample_dataset.dataset("feinberg_coli")

    profiles_with_more_acceptance: ProfileManager = ProfileManager(
        "Test", data, acceptance_absolute=True, acceptance_limit=0.4, data_transformation="log10", use_median=True
    )
    profiles_with_more_acceptance.make_profiles()

    data = sample_dataset.dataset("feinberg_coli")

    profiles_with_correction: ProfileManager = ProfileManager(
        "Test",
        data,
        acceptance_absolute=True,
        correction_allow=True,
        correction_threshold=[1, 1],
        data_transformation="log10",
        use_median=True
    )
    profiles_with_correction.make_profiles()

    litterature_dataframe: pd.DataFrame = pd.DataFrame(
        {
            "repeatability_std": {1: 0.141, 2: 0.093, 3: 0.099},
            "inter_series_std": {1: 0.092, 2: 0.081, 3: 0.141},
            "tolerance_std": {1: 0.173, 2: 0.127, 3: 0.178},
            "intermediate_precision_std": {1: 0.168, 2: 0.123, 3: 0.172},
            "bias_abs": {1: 0.024, 2: 0.055, 3: 0.093},
            "tolerance_rel_low": {1: -0.206, 2: -0.115, 3: -0.147},
            "tolerance_rel_high": {1: 0.254, 2: 0.225, 3: 0.333},
            "tolerance_abs_low": {1: 0.794, 2: 1.601, 3: 1.902},
            "tolerance_abs_high": {1: 1.254, 2: 1.941, 3: 2.382},
        }
    )

    results_dataframe: pd.DataFrame = profiles.best().get_profile_parameter(
        [
            "repeatability_std",
            "inter_series_std",
            "intermediate_precision_std",
            "tolerance_std",
            "bias_abs",
            "tolerance_rel",
            "tolerance_abs",
        ]
    ).round(3)

    assertion_dataframe = np.abs(
        litterature_dataframe.sub(results_dataframe).divide(litterature_dataframe) * 100
    )

    # We allow 0.9% since most number have only 3 significants figures. Two the data has a 0.001 absolute deviation
    # which translate to a > 0.5% error:
    # - Serie 3 Tolerance Std : Literature: 0.178, Valexa: 0.177
    # - Serie 2 Intermediate Precision Std: Literature: 0.123, Valexa: 0.124
    # This is probably due to rounding. We take them into account during the assert.
    assert len(assertion_dataframe[assertion_dataframe.ge(0.9).any(axis=1)]) == 0

    # Check if the detected max limit of quantification is the right one (max 1% deviation)
    assert np.abs((1.96 - profiles.best().max_loq) / 1.96 * 100) < 1

    # Check if the detected max limit of quantification with increased acceptance is the right one (max 1% deviation)
    assert (
        np.abs((2.05 - profiles_with_more_acceptance.best().max_loq) / 2.05 * 100) <= 1
    )

    # Check if the detected max limit of quantification with correction is the right one (max 1% deviation)
    assert np.abs((2.05 - profiles_with_correction.best().max_loq) / 2.05 * 100) <= 1

    # Check if the calculated correction is the right one (max 5% deviation).
    # Valexa now calculate the correction factor using the slope of the Reference X vs Caclulated X, however in the
    # article it is unclear which data was taken for their plot. In the case of Valexa, the Reference X is the median of
    # the logarithm of the reference method value. The difference seems to be small (slope of 1.06 vs 1.02).
    assert (
        np.abs(
            round(((1 / 1.02) - profiles_with_correction.best().correction_factor), 2)
        )
        <= 0.05
    )

    return True
