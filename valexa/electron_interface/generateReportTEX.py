from kaleido.scopes.plotly import PlotlyScope
import plotly.graph_objects as go
from zipfile import ZipFile
import os


###   MAIN   ###
def generate(**data):
    idProfile = data['compound_name'] + str(data['id'])
    commands = recupData(**data)

    ## Fichier Paragraphe Profile
    fIn = open("filesTex/TemplateProfileParagraph.tex", 'r')
    fOut = open(f"filesTex/profiles/Profile_{idProfile}.tex", 'w')
    for line in fIn:
        for cle, val in commands.items():
            line = line.replace(cle, val)
        fOut.write(line)
    fIn.close()
    fOut.close()

    ## Fichier listing des profiles
    f = open('filesTex/ListParagraphsProfile.tex', 'a')
    f.write("\\input{profiles/Profile_" + idProfile + "}\n")
    f.close()


def downloadZipTex():
    """
    Create a .zip file of the tex project in the "Downloads" directory of the PC user
    """
    file_paths = []
    for root, directories, files in os.walk('filesTex/'):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    file_paths.remove('filesTex/TemplateProfileParagraph.tex')
    file_paths.remove('filesTex/TemplateRegressionInfo.tex')
    dirDownloads = os.path.join(os.path.expanduser("~"), "Downloads")
    with ZipFile(dirDownloads + '/FichiersTEX.zip', 'w') as zip:
        for file in file_paths:
            zip.write(file)



###   METHODES   ###
def createTabular(isCol, listData):  #
    """
    Create lines of the {tabular} object in .tex

    :param bool isCol:      bool that specify if listData contains columns values (True) or lines values (False)
    :param list listData:   list of dicts if !isCol (dicts contain values of each lines for the tabular),
                            else list of lists (lists contain values of ech columns for the tabular)
    """
    line = ""
    if isCol:  # listdata = list of list
        lineTemp = []
        for i in range(len(listData[0])):  # n°item dans liste
            for j in range(len(listData)):  # n°liste
                lineTemp.append(listData[j][i])
            line += " & ".join(lineTemp)
            line += " \\\\\n"
            lineTemp.clear()
    else:
        for dictValues in listData:  # listData = list of dict
            dictValues = {
                str(key): str(round(val, 4)) if isinstance(val, float) else str(val)
                for key, val in dictValues.items()
            }  # convert values into str
            line += " & ".join(dictValues.values())
            line += " \\\\\n"
    return line


def createGraphs(id, data, layout):  # data=list, layout=dict
    """
    Create .png with graphs from the Profile vue

    :param str id:      str id of the specific profile
    :param list data:   list of dict of properties passed to the constructor of the specified trace type
    :param dict layout: dict of properties passed to the Layout constructor
    """
    layout['title']['x'] = 0.5
    layout['title']['y'] = 0.92
    layout['legend']['x'] = 0.9
    layout['legend']['y'] = 1
    scope = PlotlyScope()
    fig = go.Figure(data=data, layout=layout)
    with open(f"filesTex/profiles/fig{id}.png", "wb") as f:
        f.write(scope.transform(fig, format="png"))


def recupData(**data):
    """
    Create graphs .png and replace commands in the file TemplateProfileParagraph.tex by the profile data
    :param dict data
    """
    idProfile = data['compound_name'] + str(data['id'])
    modelInfo = data['model_info']

    createGraphs(id="PROFILE_" + idProfile,
                 data=data['graphs']['profile']['data'],
                 layout=data['graphs']['profile']['layout'])
    createGraphs(id="LINEARITY_" + idProfile,
                 data=data['graphs']['linearity']['data'],
                 layout=data['graphs']['linearity']['layout'])

    commands = {
        "\\COMPOUNDname": data['compound_name'],

        ### SUMMARY TABLES  ###
        "\\LODunitstype": f"""{modelInfo['lod']} {modelInfo['units']} ({
            "" if modelInfo['lod_type'] is None else modelInfo['lod_type']
        })""",
        "\\MINLOQunits": f"{modelInfo['min_loq']} {modelInfo['units']}",
        "\\MAXLOQunits": f"{modelInfo['max_loq']} {modelInfo['units']}",
        "\\CORRECTION": f"""{
            modelInfo['correction_factor'] ("", " (Forced)")[float(modelInfo['forced_correction_value'])>0]
            if modelInfo['has_correction'] else "---"
        }""",
        "\\AVERAGErecov": str(modelInfo['average_recovery']),
        "\\TOLERANCE": f"{modelInfo['tolerance']}\%",
        "\\ACCEPT": f"""{modelInfo['acceptance']}\% {"(Absolute)" if modelInfo['absolute_acceptance'] else "(Relative)"}""",

        ###  GRAPHIQUE PROFILE  ###
        "\\GRAPHprofile": "\\includegraphics[width=150mm]{profiles/figPROFILE_" + idProfile + "}",

        ###  TRUENESS TABLE  ###
        "\\DATAtrueness": createTabular(True, [
            [str(item) for item in list(range(len(data['levels_info'])))],  # nb ligne tabular
            [str(item['introduced_concentration']) for item in data['levels_info']],
            [str(item['calculated_concentration']) for item in data['levels_info']],
            [str(item['bias_abs']) for item in data['bias_info']],
            [str(item['bias_rel']) for item in data['bias_info']],
            [str(item['recovery']) for item in data['bias_info']],
            [f"{item['tolerance_abs_high']} , {item['tolerance_abs_low']}" for item in data['tolerance_info']],
            [f"{item['tolerance_rel_high']} , {item['tolerance_rel_low']}" for item in data['tolerance_info']],
        ]),

        ###  PRECISION REPEATABILITY TABLE  ###
        "\\DATAprecisionrepeat": createTabular(True, [
            [str(item) for item in list(range(len(data['levels_info'])))],  # nb ligne tabular
            [str(item['introduced_concentration']) for item in data['levels_info']],
            [str(item['intermediate_precision_std']) for item in data['intermediate_precision']],
            [str(item['intermediate_precision_cv']) for item in data['intermediate_precision']],
            [str(item['repeatability_std']) for item in data['repeatability_info']],
            [str(item['repeatability_cv']) for item in data['repeatability_info']],
            [str(item['ratio_var']) for item in data['misc_stats']]
        ]),

        ###  VALIDATION UNCERTAINTY  ###
        "\\DATAvaliduncertainty": createTabular(True, [
            [str(item) for item in list(range(len(data['levels_info'])))],  # nb ligne tabular
            [str(item['introduced_concentration']) for item in data['levels_info']],
            [str(item['calculated_concentration']) for item in data['levels_info']],
            [str(item['uncertainty_abs']) for item in data['uncertainty_info']],
            [str(item['uncertainty_pc']) for item in data['uncertainty_info']]
        ]),

        ###  GRAPHIQUE LINEARITY  ###
        "\\GRAPHlinearity": "\\includegraphics[width=150mm]{profiles/figLINEARITY_" + idProfile + "}",

        ###  VALIDATION TABLE  ###
        "\\DATAvalidation": createTabular(False, data['validation_data'])
    }

    ###  SPAN REGRESSION INFO  ###
    if len(data['validation_data']) > 0:
        commands["\\REGRESSIONinfo"] = "\\input{profiles/regr_" + idProfile + "}"
        createTexRegression(**data)
    else:
        commands["\\REGRESSIONinfo"] = ""

    return commands


def createTexRegression(**data):
    """
    Called only if there are regression information\n
    Create graphs .png and replace commands in the file TemplateRegressionInfo.tex by the profile data
    :param dict data
    """
    idProfile = data['compound_name'] + str(data['id'])

    createGraphs(id="REGRESSION_" + idProfile,
                 data=data['graphs']['regression']['data'],
                 layout=data['graphs']['regression']['layout'])
    createGraphs(id="RESIDUALS_" + idProfile,
                 data=data['graphs']['residuals']['data'],
                 layout=data['graphs']['residuals']['layout'])
    createGraphs(id="RESIDUALSstd_" + idProfile,
                 data=data['graphs']['residuals_std']['data'],
                 layout=data['graphs']['residuals_std']['layout'])

    commands = {
        "\\COMPOUNDname": data['compound_name'],

        ###  REGRESSION TABLE  ###
        "\\DATAregression": createTabular(True, [
            [str(item) for item in list(range(len(data['regression_info'])))],  # nb ligne tabular,
            [f"${item['function_string']}$" for item in data['regression_info']],
            [str(item['rsquared']) for item in data['regression_info']]
        ]),

        ###  GRAPHIQUES  ###
        "\\GRAPHregression": "\\includegraphics[width=150mm]{profiles/figREGRESSION_" + idProfile + "}",
        "\\GRAPHresidualsFIRST": "\\includegraphics[width=150mm]{profiles/figRESIDUALS_" + idProfile + "}",
        "\\GRAPHresidualsSECOND": "\\includegraphics[width=150mm]{profiles/figRESIDUALSstd_" + idProfile + "}",

        ###  CALIBRATION TABLE  ###
        "\\DATAcalibration": createTabular(False, data['calibration_data']),

    }

    ## Create file for regression info
    fIn = open("filesTex/TemplateRegressionInfo.tex", 'r')
    fOut = open(f"filesTex/profiles/regr_{idProfile}.tex", 'w')
    for line in fIn:
        for cle, val in commands.items():
            line = line.replace(cle, val)
        fOut.write(line)
    fIn.close()
    fOut.close()
