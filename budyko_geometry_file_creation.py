##Budyko=group
##Prepare subreaches' geometry file=name
##ParameterFile|MODEL_FILE|Model setup file|False|False
##OutputFile|GEOMETRY_FILE|Output file with model subreaches' geometry|txt

import pandas as pd
import sys
from contextlib import contextmanager

from processing.tools.system import getTempFilename

from budyko_model import geometry_file_creation
from budyko_model.river_network import RiverNetwork
from budyko_model.modelfile import ModelFile


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


with redirect_stdout(progress):

    routing = RiverNetwork(MODEL_FILE)
    model = ModelFile(MODEL_FILE)

    # Get drainage network
    drains_to = routing.drains_to

    temp_file = getTempFilename("csv")
    geometry_file_creation.read_network_file(model, routing, temp_file)
    subreaches = pd.read_csv(temp_file, index_col='Subbasin')
    geometry_file_creation.write_geometry_file(subreaches=subreaches,
                                               model=model,
                                               drains_to=drains_to,
                                               geometry_file=GEOMETRY_FILE)
