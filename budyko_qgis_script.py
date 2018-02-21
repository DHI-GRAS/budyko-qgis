##Budyko=group
##Budyko Hydrological Model=name
##ParameterFile|GEOMETRY_FILE|Geometry setup|False|False
##ParameterFile|MODEL_FILE|Model setup|False|False
##ParameterFile|OBS_REACH_FILE|Observed-discharge file|False|False
##ParameterFile|PARAMETER_FILE|Model parameter file|False|True
##ParameterNumber|REACH_NUMBER|Reach number considered|0|10000|0
##ParameterString|STARTDATE|Start date YYYYJJJ|
##ParameterSelection|OUTPUT_TYPE|Output type|Hydrograph;Climatology;FDC|0
##OutputDirectory|OUTDIR|Output directory for plots
##ParameterSelection|TIME_STAMP|Time resolution|daily;monthly|0
##*ParameterNumber|N_CLASSES|Number of volume classes for FDC|0|1000|20
##*ParameterString|TITLE|Title for plot|||True
import sys
from contextlib import contextmanager

from budyko_model.scripts import middle_layer


class ProgressLogger:

    def __init__(self, progress):
        self.progress = progress

    def write(self, msg):
        self.progress.setConsoleInfo(msg)


@contextmanager
def redirect_stdout(progress):
    oldout = sys.stdout
    sys.stdout = ProgressLogger(progress)
    try:
        yield
    finally:
        sys.stdout = oldout


with redirect_stdout(progress):
    middle_layer.main(
        geometry_file=GEOMETRY_FILE,
        model_file=MODEL_FILE,
        parameter_file=PARAMETER_FILE,
        obs_reach_file=OBS_REACH_FILE,
        outdir=OUTDIR,
        reach_number=REACH_NUMBER,
        startdate=STARTDATE,
        output_type=OUTPUT_TYPE,
        time_stamp=TIME_STAMP,
        n_classes=N_CLASSES,
        title=TITLE)
