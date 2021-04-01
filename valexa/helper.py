import sigfig as sf
import pandas as pd
import math


def get_value_between(
    x_value: float, left_coord: (float, float), right_coord: (float, float)
) -> float:
    x1, y1 = left_coord
    x2, y2 = right_coord
    slope: float = (y2 - y1) / (x2 - x1)

    return slope * (x_value - x1) + y1


def format_json_to_data(data):
    validation = pd.DataFrame(data["validation"])
    ys = [col for col in validation.columns if col[0] == "y"]
    xs = [col for col in validation.columns if col[0] == "x"]
    validation_dataframe = pd.DataFrame()
    if len(ys) > len(xs):
        for y in ys:
            columns_name = {"series": "Series", "level": "Level", "x1": "x", y: "y"}
            temp_dataframe = validation[["series", "level", "x1", y]].rename(
                columns=columns_name
            )
            validation_dataframe = pd.concat(
                [validation_dataframe, temp_dataframe], ignore_index=True
            )
    else:
        for x in range(1, len(xs)+1):
            columns_name = {"series": "Series", "level": "Level", "x" + str(x): "x", "y" + str(x): "y"}
            temp_dataframe = validation[["series", "level", "x" + str(x), "y" + str(x)]].rename(
                columns=columns_name
            )
            validation_dataframe = pd.concat(
                [validation_dataframe, temp_dataframe], ignore_index=True
            )


    if "calibration" in data:
        calibration = pd.DataFrame(data["calibration"])
        ys = [col for col in calibration.columns if col[0] == "y"]
        xs = [col for col in calibration.columns if col[0] == "x"]
        calibration_dataframe = pd.DataFrame()
        if len(ys) > len(xs):
            for y in ys:
                columns_name = {"series": "Series", "level": "Level", "x1": "x", y: "y"}
                temp_dataframe = calibration[["series", "level", "x1", y]].rename(
                    columns=columns_name
                )
                calibration_dataframe = pd.concat(
                    [calibration_dataframe, temp_dataframe], ignore_index=True
                )

        else:
            for x in range(1, len(xs)+1):
                columns_name = {"series": "Series", "level": "Level", "x" + str(x): "x", "y" + str(x): "y"}
                temp_dataframe = calibration[["series", "level", "x" + str(x), "y" + str(x)]].rename(
                    columns=columns_name
                )
                calibration_dataframe = pd.concat(
                    [calibration_dataframe, temp_dataframe], ignore_index=True
                )

        validation_dataframe = pd.DataFrame(validation_dataframe[(validation_dataframe.Series > 3)]).reset_index(drop=True)
        calibration_dataframe = pd.DataFrame(calibration_dataframe[(calibration_dataframe.Series > 3)]).reset_index(drop=True)


        return {
            # Quick test
            "Validation": validation_dataframe,
            "Calibration": calibration_dataframe
        }

    else:
        return {
            "Validation": validation_dataframe
        }


def roundsf(data, sigfig):

    if data == None or data == '':
        return data
    if type(data) == str:
        return data
    if math.isnan(data):
        return data
    if math.isinf(data):
        return data
    if sigfig > 0:
        if type(data).__module__ == "numpy":
            return sf.round(data.item(), sigfig)
        else:
            return sf.round(data, sigfig)
    else:
        return data


def get_intersection_from_points(point1, point2, point3, point4):
    x1, y1 = point1
    x2, y2 = point2
    x3, y3 = point3
    x4, y4 = point4

    x = ((x1 * y2 - x2 * y1) * (x3 - x4) - (x3 * y4 - x4 * y3) * (x1 - x2)) / (
        (x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2)
    )
    y = ((x1 * y2 - x2 * y1) * (y3 - y4) - (x3 * y4 - x4 * y3) * (y1 - y2)) / (
        (x1 - x2) * (y3 - y4) - (x3 - x4) * (y1 - y2)
    )

    return [x, y]
