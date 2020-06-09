##Budyko=group
##Budyko Hydrological Model Calibration=name
##ParameterFile|GEOMETRY_FILE|Geometry setup|False|False
##ParameterFile|MODEL_FILE|Model setup|False|False
##ParameterFile|OBS_REACH_FILE|Observed-discharge file|False|False
##ParameterFile|CONFIG_FILE|Config file (JSON) for calibration|False|False
##ParameterString|STARTDATE|Start date YYYYJJJ|
##ParameterString|ENDDATE|End date YYYYJJJ|
##ParameterSelection|CALIBRATION_TYPE_ID|Calibration type|FDC;Climatology;both|0
##*ParameterNumber|REP|Number of repetitions in optimization|1|1000000|100000
##*ParameterNumber|N_CLASSES|Number of volume classes for FDC calibration|0|1000|20
##*ParameterNumber|ACC_INT|Accepted interval for FDC objective function|0|1|0.1
##*ParameterNumber|Z_CH|Inverse of river channel side slope, z_ch (trapezoidal channel)|0|1000|2.0
##*ParameterNumber|AREA_TO_M|Factor to convert area to meters|0|1000000|1.0
import re
import sys
import json
from contextlib import contextmanager

from budyko_model.scripts import middle_layer_calibration


class ProgressLogger:

    def __init__(self, progress):
        self.progress = progress

    def write(self, msg):
        self.feedback.pushConsoleInfo(msg)


@contextmanager
def redirect_stdout(progress):
    oldout = sys.stdout
    sys.stdout = ProgressLogger(progress)
    try:
        yield
    finally:
        sys.stdout = oldout


def _key_to_int(kw):
    for k, v in kw.items():
        if isinstance(v, dict):
            _key_to_int(v)
        elif re.match('\d+', k) is not None:
            kw[int(k)] = kw.pop(k)


def _read_json_config(path):
    with open(path, 'r') as f:
        kw = json.load(f)
    _key_to_int(kw)
    return kw


config_kw = _read_json_config(CONFIG_FILE)

calibration_type = ['fdc', 'climatology', 'both'][CALIBRATION_TYPE_ID]

with redirect_stdout(progress):
    middle_layer_calibration.main(
        geometry_file=GEOMETRY_FILE,
        model_file=MODEL_FILE,
        obs_reach_file=OBS_REACH_FILE,
        startdate=STARTDATE,
        enddate=ENDDATE,
        calibration_type=calibration_type,
        N=N_CLASSES,
        acc_int=ACC_INT,
        z_ch=Z_CH,
        area_to_m=AREA_TO_M,
        rep=REP,
        **config_kw
    )
