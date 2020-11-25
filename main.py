from valexa.profiles import ProfileManager
from valexa.examples.dataset import sample_dataset
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import valexa.helper as vx
import numpy as np
import json


dataset = {
    "Validation": pd.DataFrame(
        [
            [2, 1, 419, 1.53451784646202],
            [3, 1, 443, 1.58609969980414],
            [2, 1, 419, 1.45862500900871],
            [3, 1, 443, 1.57630090218957],
            [2, 1, 419, 1.55035399412083],
            [3, 1, 443, 1.60626322138179],
            [1, 2, 1015, 3.91003892419292],
            [2, 2, 1047.5, 4.4144308245623],
            [3, 2, 1107.5, 4.84901802102159],
            [1, 2, 1015, 3.98691721426075],
            [2, 2, 1047.5, 4.25259486021748],
            [3, 2, 1107.5, 4.95757568303534],
            [1, 2, 1015, 3.99524580443895],
            [2, 2, 1047.5, 4.43489882448232],
            [3, 2, 1107.5, 5.03027363667067],
            [1, 4, 3045, 11.9111186706619],
            [2, 4, 3142.5, 12.4307010001949],
            [3, 4, 3322.5, 14.3365673436486],
            [1, 4, 3045, 12.0129540993486],
            [2, 4, 3142.5, 12.0058639937357],
            [3, 4, 3322.5, 14.4587582849768],
            [1, 4, 3045, 12.0860185183728],
            [2, 4, 3142.5, 12.1419565482177],
            [3, 4, 3322.5, 14.5641280564365],
            [1, 5, 4060, 14.239666251549],
            [2, 5, 4190, 17.2338229373495],
            [3, 5, 4430, 18.3592301237821],
            [1, 5, 4060, 14.382300001946],
            [2, 5, 4190, 16.6125112965469],
            [3, 5, 4430, 18.3304205458616],
            [1, 5, 4060, 14.3762852569976],
            [2, 5, 4190, 16.8719649174288],
            [3, 5, 4430, 18.6730754223547],

        ],
        columns=["Series", "Level", "x", "y"],
    ),
    "Calibration": pd.DataFrame(
        [
            [1, 1, 406, 0.998586158821292],
            [2, 1, 419, 1.10404061555999],
            [3, 1, 443, 1.33676184474706],
            [1, 1, 406, 1.10668672019367],
            [2, 1, 419, 1.10533409837239],
            [3, 1, 443, 1.3452641016464],
            [1, 1, 406, 1.11747929869418],
            [2, 1, 419, 1.11881371928904],
            [3, 1, 443, 1.33976563224466],
            [1, 2, 1015, 4.17857258377101],
            [2, 2, 1047.5, 4.46274945189253],
            [3, 2, 1107.5, 4.62794228756877],
            [1, 2, 1015, 4.50347521387168],
            [2, 2, 1047.5, 4.37069789781473],
            [3, 2, 1107.5, 4.67589704309223],
            [1, 2, 1015, 4.48445208560007],
            [2, 2, 1047.5, 4.37276385650597],
            [3, 2, 1107.5, 4.71876455317858],
            [1, 3, 2030, 6.64220182668196],
            [2, 3, 2095, 9.02599522367508],
            [3, 3, 2215, 9.86865872842256],
            [1, 3, 2030, 7.27105908029828],
            [2, 3, 2095, 9.02019877671338],
            [3, 3, 2215, 9.98849560427756],
            [1, 3, 2030, 7.48971950689836],
            [2, 3, 2095, 9.21288759522981],
            [3, 3, 2215, 10.1085590484058],
            [1, 4, 3045, 12.3754474804587],
            [2, 4, 3142.5, 11.6258656940642],
            [3, 4, 3322.5, 14.9180354705792],
            [1, 4, 3045, 12.8790473560492],
            [2, 4, 3142.5, 11.758352792905],
            [3, 4, 3322.5, 15.233986963097],
            [1, 4, 3045, 13.4446593846229],
            [2, 4, 3142.5, 11.8714051364981],
            [3, 4, 3322.5, 15.2766192141471],
            [1, 5, 4060, 14.7498947045687],
            [2, 5, 4190, 15.4064327172843],
            [3, 5, 4430, 20.176000755941],
            [1, 5, 4060, 15.8888569932834],
            [2, 5, 4190, 15.4200260630323],
            [3, 5, 4430, 20.8796730188044],
            [1, 5, 4060, 16.2515119657081],
            [2, 5, 4190, 15.1633049451082],
            [3, 5, 4430, 21.1905995597224],
        ],
        columns=["Series", "Level", "x", "y"],
    )
}

def main():
    """
    Dataset from:
    inra_pyrene: Huyez-Levrat, M et al.,Cahier technique de l'INRA - Validation des méthodes (2010), https://www6.inrae.fr/cahier_des_techniques/Les-Cahiers-parus/Les-n-Speciaux-et-les-n-Thematiques/Validation-des-methodes

    This dataset is mainly use to check if the correction factor generated is 1.2.
    The
    :return:
    """

    optimizer_parameter = {
        "has_limits": True,
        "validation_range": "max",
        "average.bias_abs": "min",
        "min_loq": "min",
        "model.rsquared": "max",
    }
    validation = dataset['Validation'].sort_values(by='x')
    calibration = dataset['Calibration'].sort_values(by='x')

    dataset['Validation'] = validation
    dataset['Calibration'] = calibration
    data = dataset


    config = {
        "compound_name": "Test",
        "rolling_data": False,
        "optimizer_parameter": optimizer_parameter,
        "correction_allow": True,
        "model_to_test": ['Linear'],
        "data": data,
        "rolling_limit": 3,
        "significant_figure": 4,
    }

    # config = json.loads('{"compound_name":"template","data":{"validation":[{"series":1,"level":1,"x":1.9,"y1":36539,"y2":36785,"$id":"72328206-0000000"},{"series":1,"level":2,"x":4.7,"y1":102066,"y2":98495,"$id":"72328206-0000001"},{"series":1,"level":3,"x":9.5,"y1":188665,"y2":191294,"$id":"72328206-0000002"},{"series":1,"level":4,"x":28.5,"y1":595999,"y2":604704,"$id":"72328206-0000003"},{"series":2,"level":1,"x":1.9,"y1":60086,"y2":35295,"$id":"72328206-0000004"},{"series":2,"level":2,"x":4.7,"y1":99897,"y2":93547,"$id":"72328206-0000005"},{"series":2,"level":3,"x":9.5,"y1":188657,"y2":198683,"$id":"72328206-0000006"},{"series":2,"level":4,"x":28.5,"y1":520857,"y2":501025,"$id":"72328206-0000007"},{"series":3,"level":1,"x":1.9,"y1":57695,"y2":59731,"$id":"72328206-0000008"},{"series":3,"level":2,"x":4.7,"y1":115298,"y2":111584,"$id":"72328206-0000009"},{"series":3,"level":3,"x":9.5,"y1":221678,"y2":194983,"$id":"72328206-0000010"},{"series":3,"level":4,"x":28.5,"y1":557258,"y2":541355,"$id":"72328206-0000011"}]},"tolerance_limit":80,"acceptance_limit":20,"acceptance_absolute":false,"quantity_units":null,"rolling_data":false,"rolling_limit":3,"model_to_test":"Linear","correction_allow":false,"correction_threshold":[0.9,1.1],"correction_forced_value":null,"correction_round_to":2,"optimizer_parameter":null,"significant_figure":4,"lod_allowed":null,"lod_force_miller":false,"status":""}')
    # config['data'] = vx.format_json_to_data(config['data'])
    # config['correction_allow'] = True
    # config['correction_forced_value'] = None
    # config['acceptance_absolute'] = True

    profiles = ProfileManager(**config)
    profiles.make_profiles()
    # profiles.optimize()


    aa = profiles.output_profiles()

    for zz in aa.values():
        print(json.dumps({"type": "PROFILE", "data": zz}, cls=PlotlyJSONEncoder))

    profiles.optimize()

    pass

if __name__ == "__main__":
    main()

