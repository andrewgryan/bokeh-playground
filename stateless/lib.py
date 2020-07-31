"""Example Python I/O library"""
import datetime as dt


def data_times(dataset):
    """Datetime information related to dataset"""
    return {
        "x": [dt.datetime.now()]
    }


def xy_data(dataset, variable):
    """X-Y line/circle data related to a dataset"""
    # import time
    # time.sleep(5)  # Simulate expensive I/O or slow server
    if dataset == "takm4p4":
        return {
            "x": [0, 1e5, 2e5],
            "y": [0, 1e5, 2e5]
        }
    else:
        return {
            "x": [0, 1e5, 2e5],
            "y": [0, 3e5, 1e5]
        }


def image_data(dataset, variable):
    return {
        "x": [],
        "y": [],
        "dw": [],
        "dh": [],
        "image": [
        ]
    }