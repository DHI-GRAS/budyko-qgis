import numpy as np

import Budyko
from RiverNetwork import RiverNetwork
import Parameter_functions
from ModelFile import ModelFile
from Visualize import Visualize


DEFAULT_PARAMETERS = {
    'a1': 0.4,
    'a2': 0.35,
    'd': 0.02,
    'Smax': 700.,
    'Xm': 0.2,
    'nm': 0.035}

DEFAULT_PARAMETER_SEQUENCE = ['a1', 'a2', 'd', 'Smax', 'Xm', 'nm']

OUTPUT_TYPES = [0, 1, 2]

TIME_STAMPS = [0, 1]


def _get_default_parameters(nsubs):
    params = [
        np.ones(nsubs, dtype=float) * DEFAULT_PARAMETERS[key]
        for key in DEFAULT_PARAMETER_SEQUENCE]
    return np.array(params)


def main(
        geometry_file, model_file,
        parameter_file, obs_reach_file,
        outdir, reach_number, startdate,
        output_type=0, time_stamp=0,
        n_classes=20, title=None):
    """Interface to Budyko model from DTU Environment

    Parameters
    ----------
    geometry_file, model_file, parameter_file : str
        paths to files
    obs_reach_file : str
        path to obs reach file
    outdir : str
        path to output directory
    reach_number : int
        Reach number
    startdate : str YYYYJJJ
        start date
    output_type, time_stamp : int
        output type and time stamp IDs
    n_classes : int
        number of classes
    title : str
        title for plot
    """
    # check inputs

    if not title:
        title = ''

    if output_type not in OUTPUT_TYPES:
        raise ValueError(
            'Invalid output type {}. Choose from {}'
            .format(output_type, OUTPUT_TYPES))

    if time_stamp not in TIME_STAMPS:
        raise ValueError(
            'Invalid time stamp {}. Choose from {}'
            .format(time_stamp, TIME_STAMPS))

    print('Initalize model')
    model = ModelFile(model_file)

    ns = int(model.desc['TotalNoSubs'])
    try:
        parameters = Parameter_functions.read_parameters_txtfile(parameter_file, ns)
    except:
        parameters = _get_default_parameters(ns)

    model_output = Budyko.setup(
        model_folder=outdir,
        Budyko_parameters=parameters,
        model_file=model_file,
        geometry_file=geometry_file)

    Visualize(
        output=model_output,
        ReachNo=reach_number,
        obs_reach_file=obs_reach_file,
        N=n_classes,
        output_type=output_type,
        time_stamp=time_stamp,
        startdate=startdate,
        folder=outdir,
        title1=title)
