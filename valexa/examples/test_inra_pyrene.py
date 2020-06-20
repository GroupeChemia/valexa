from valexa.profiles import ProfileManager
from valexa.examples.dataset import sample_dataset
import numpy as np


def test_inra_pyrene():
    """
    Dataset from:
    inra_pyrene: Huyez-Levrat, M et al.,Cahier technique de l'INRA - Validation des méthodes (2010), https://www6.inrae.fr/cahier_des_techniques/Les-Cahiers-parus/Les-n-Speciaux-et-les-n-Thematiques/Validation-des-methodes

    This dataset is mainly use to check if the correction factor generated is 1.2.
    The
    :return:
    """
    data = sample_dataset.dataset("inra_pyrene")

    profiles: ProfileManager = ProfileManager(
        "Test",
        data,
        allow_correction=True
    )
    profiles.make_profiles(["Linear"])

    assert profiles.profiles["Linear"][0].correction_factor == 1.2
    assert profiles.profiles["Linear"][0].max_loq == 28.5
    assert np.abs((4.7-profiles.profiles["Linear"][0].min_loq)/4.7*100) < 10

    return True
