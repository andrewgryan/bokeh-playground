"""Example Python I/O library"""
import datetime as dt


def data_times(dataset):
    """Datetime information related to dataset"""
    x = [dt.datetime.now()]
    return {
        "x": [1000 * t.timestamp() for t in x]
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
