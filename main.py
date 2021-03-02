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


    # config = {
    #     "compound_name": "Test",
    #     "rolling_data": False,
    #     "optimizer_parameter": optimizer_parameter,
    #     "correction_allow": True,
    #     "model_to_test": ['Linear'],
    #     "data": data,
    #     "rolling_limit": 3,
    #     "significant_figure": 4,
    # }

    config = json.loads('{"compound_name":"Validation 8-THC","data":{"validation":[{"series":1,"level":1,"x1":0,"y1":0,"y2":0,"y3":0},{"series":1,"level":2,"x1":0.02,"y1":4.80753735059871,"y2":6.47930071904036,"y3":0},{"series":1,"level":3,"x1":0.07,"y1":12.5547409057603,"y2":12.2986632705014,"y3":19.528248938895},{"series":1,"level":4,"x1":0.31,"y1":75.8204460143959,"y2":77.3027871784325,"y3":78.4984486840891},{"series":2,"level":1,"x1":0,"y1":0,"y2":0,"y3":0},{"series":2,"level":2,"x1":0.02,"y1":9.02298838399814,"y2":9.09072935921548,"y3":8.41021463019245},{"series":2,"level":3,"x1":0.07,"y1":24.0594863891575,"y2":23.9938735961888,"y3":23.4537124633763},{"series":2,"level":4,"x1":0.31,"y1":134.710026330937,"y2":134.308801860803,"y3":129.891295020735},{"series":3,"level":1,"x1":0,"y1":0,"y2":0,"y3":0},{"series":3,"level":2,"x1":0.02,"y1":8.33072805237797,"y2":13.4003293238159,"y3":8.05812654304487},{"series":3,"level":3,"x1":0.07,"y1":25.6507622509369,"y2":30.2629631414579,"y3":23.6714863569795},{"series":3,"level":4,"x1":0.31,"y1":126.446546916968,"y2":130.014134564315,"y3":123.074153020988}],"calibration":[{"series":1,"level":1,"x1":0.019531,"y1":0,"y2":0,"y3":0},{"series":1,"level":2,"x1":0.078125,"y1":17,"y2":15,"y3":19},{"series":1,"level":3,"x1":0.3125,"y1":73,"y2":64,"y3":71},{"series":1,"level":4,"x1":1.25,"y1":371,"y2":375,"y3":368},{"series":1,"level":5,"x1":5,"y1":1199,"y2":1222,"y3":1222},{"series":2,"level":1,"x1":0.019531,"y1":7.3134422302238,"y2":7.8779220581046,"y3":6.14490509033141},{"series":2,"level":2,"x1":0.078125,"y1":30.2732467651333,"y2":30.5685043334927,"y3":33.0387115478479},{"series":2,"level":3,"x1":0.3125,"y1":143.43757629393,"y2":132.082271575913,"y3":138.692855834946},{"series":2,"level":4,"x1":1.25,"y1":698.757749938888,"y2":644.550898742605,"y3":621.293260192803},{"series":2,"level":5,"x1":5,"y1":2045.63196105935,"y2":2038.29667968728,"y3":1989.91182861306},{"series":3,"level":1,"x1":0.019531,"y1":9.14697647094664,"y2":10.2504730224598,"y3":733.325886436509},{"series":3,"level":2,"x1":0.078125,"y1":32.4423789977991,"y2":29.4147491455046,"y3":29.8345565795866},{"series":3,"level":3,"x1":0.3125,"y1":122.380638122545,"y2":124.029922485338,"y3":120.820236206042},{"series":3,"level":4,"x1":1.25,"y1":489.615534210151,"y2":483.353230285591,"y3":488.412567901557},{"series":3,"level":5,"x1":5,"y1":1935.79681625345,"y2":1905.20286560038,"y3":1908.72211456278}]},"tolerance_limit":80,"acceptance_limit":20,"acceptance_absolute":false,"quantity_units":"%","rolling_data":false,"rolling_limit":3,"model_to_test":"Linear","correction_allow":false,"correction_threshold":[0.9,1.1],"correction_forced_value":null,"correction_type":"slope","correction_round_to":2,"optimizer_parameter":null,"significant_figure":4,"lod_allowed":null,"lod_force_miller":false,"data_transformation":null,"use_median":false,"status":""}')
    config['data'] = vx.format_json_to_data(config['data'])
    config['correction_type'] = 'average'
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

