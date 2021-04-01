from valexa.profiles import ProfileManager
from valexa.examples.dataset import sample_dataset
import numpy as np


def test_inra_pyrene():
    """
    Dataset from:
    inra_pyrene: Huyez-Levrat, M et al.,Cahier technique de l'INRA - Validation des méthodes (2010), https://www6.inrae.fr/cahier_des_techniques/Les-Cahiers-parus/Les-n-Speciaux-et-les-n-Thematiques/Validation-des-methodes

    This dataset is mainly use to check if the correction factor generated is 1.2.

    This example is from a student paper and has some particularity, among other, the correction factor is calculated
    through the slope, however it is applied to the final results and not to the raw measurement. This is equivalent to
    an "average" calculation of the correction factor.
    :return:
    """
    data = sample_dataset.dataset("inra_pyrene")

    profiles: ProfileManager = ProfileManager("Test", data, correction_allow=True, correction_type='average')
    profiles.make_profiles(["Linear"])

    assert profiles.best().correction_factor == 1.2
    assert profiles.best().max_loq == 28.5
    assert np.abs((4.7 - profiles.best().min_loq) / 4.7 * 100) < 10

    return True
