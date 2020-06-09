##Budyko=group
##Budyko Hydrological Model=name
##ParameterFile|GEOMETRY_FILE|Geometry setup|False|False
##ParameterFile|MODEL_FILE|Model setup|False|False
##ParameterFile|OBS_REACH_FILE|Observed-discharge file|False|False
##ParameterFile|PARAMETER_FILE|Model parameter file|False|True
##ParameterNumber|REACH_NUMBER|Reach number considered|0|10000|0
##ParameterString|STARTDATE|Start date YYYYJJJ|
##ParameterSelection|MODEL_TYPE_ID|Output type|Hydrograph;Climatology;FDC|0
##OutputDirectory|OUTDIR|Output directory for plots
##ParameterSelection|TIME_RESOLUTION_ID|Time resolution|daily;monthly|0
##*ParameterNumber|N_CLASSES|Number of volume classes for FDC|0|1000|20
##*ParameterNumber|AREA_TO_M|Factor to convert area to meters|0|1000000|1.0
##*ParameterString|FIGURE_TITLE|Title for plot|||True
import sys
from contextlib import contextmanager

from budyko_model.scripts import middle_layer


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


time_resolution = ['daily', 'monthly'][TIME_RESOLUTION_ID]
model_type = ['hydrograph', 'climatology', 'fdc'][MODEL_TYPE_ID]

with redirect_stdout(progress):
    middle_layer.main(
        geometry_file=GEOMETRY_FILE,
        model_file=MODEL_FILE,
        parameter_file=(PARAMETER_FILE or None),
        obs_reach_file=OBS_REACH_FILE,
        outdir=OUTDIR,
        reach_number=REACH_NUMBER,
        startdate=STARTDATE,
        model_type=model_type,
        time_resolution=time_resolution,
        n_classes=N_CLASSES,
        area_to_m=AREA_TO_M,
        figure_title=FIGURE_TITLE,
        show_figure=True)
