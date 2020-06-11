##Prepare Budyko model climate files=name
##Budyko=group
##ParameterFile|model_file|Model description file|False|False
##ParameterFile|pcp_folder|Precipitation folder|True|False
##ParameterFile|tmax_folder|Maximum temperature folder|True|False
##ParameterFile|tmin_folder|Minimum temperature folder|True|False
##ParameterNumber|subcatchmap_res|Resolution of subcatchment map in degrees|0.001|0.5|0.01

import os
import sys
from datetime import date, timedelta, datetime
import numpy
from qgis.core import QgsProcessingException
from budyko_model.modelfile import ModelFile
if not os.path.dirname(scriptDescriptionFile) in sys.path:
    sys.path.append(os.path.dirname(scriptDescriptionFile))
from ClimateStations import ClimateStations
from ZonalStats import ZonalStats

feedback.pushConsoleInfo("Loading model and data files...")

# Check inputs
for folder in [pcp_folder, tmax_folder, tmin_folder]:
    if not os.path.isdir(folder):
        raise QgsProcessingException('No such directory: \"' + folder + '\" ')
if not os.path.isfile(model_file):
    raise QgsProcessingException('No such file: \"' + model_file + '\" ')

# Load model
model = ModelFile(model_file)

# Create log file
with open(os.path.join(model.Path, "log.txt"), "w") as log_file:
    # Write current date to log file
    now = date.today()
    log_file.write('Generate climate files, run date: ' + now.strftime('%Y%m%d') + '\n')
    # Load stations file
    stations_temp = ClimateStations(os.path.join(model.Path, model.desc['StationsTemp']))
    stations = ClimateStations(os.path.join(model.Path, model.desc['Stations']))

    feedback.pushConsoleInfo("Reading old climate data...")
    pcp_juliandates, first_pcp_date, last_pcp_date, pcp_array = stations.readPcpFiles(log_file)
    tmp_juliandates, first_tmp_date, last_tmp_date, tmp_max_array, tmp_min_array =\
        stations_temp.readTmpFiles(log_file)

    feedback.pushConsoleInfo("Searching for new files...")
    # Getting list of new pcp data files
    new_pcp_files = []
    new_pcp_enddate = last_pcp_date
    pcp_var_GFS = 'APCP.tif'
    pcp_var_RFE = '_rain_.tif'
    pcp_var_TRMM = '_TRMM3B42.tif'
    for f in os.listdir(pcp_folder):
        if (pcp_var_GFS in f) or (pcp_var_RFE in f) or (pcp_var_TRMM in f):
            file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
            # Only get new files
            if (last_pcp_date < file_date):
                new_pcp_files.append(os.path.join(pcp_folder, f))
                # Find the last date
                if new_pcp_enddate < file_date:
                    new_pcp_enddate = file_date

    # Getting list of new tmax data files
    new_tmax_files = []
    new_tmax_enddate = last_tmp_date
    tmax_var_GFS = 'TMAX.tif'
    tmax_var_ECMWF = '_TMAX_ECMWF.tif'
    tmax_forecast_var = 'TMAX_Forecast_'
    for f in os.listdir(tmax_folder):
        if (tmax_var_GFS in f) or (tmax_var_ECMWF in f):
            file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
            # Only get new files
            if (last_tmp_date < file_date):
                new_tmax_files.append(os.path.join(tmax_folder, f))
                # Find the last date
                if new_tmax_enddate < file_date:
                    new_tmax_enddate = file_date

    # Getting list of new tmin data files
    new_tmin_files = []
    new_tmin_enddate = last_tmp_date
    tmin_var_GFS = 'TMIN.tif'
    tmin_var_ECMWF = '_TMIN_ECMWF.tif'
    tmin_forecast_var = 'TMIN_Forecast_'
    for f in os.listdir(tmin_folder):
        if (tmin_var_GFS in f) or (tmin_var_ECMWF in f):
            file_date = datetime.strptime(f[0:8], "%Y%m%d").date()
            # Only get new files
            if (last_tmp_date < file_date):
                new_tmin_files.append(os.path.join(tmin_folder, f))
                # Find the last date
                if new_tmin_enddate < file_date:
                    new_tmin_enddate = file_date

    log_file.write('APCP files: ' + str(new_pcp_files) + '\n')
    log_file.write('TMAX files: ' + str(new_tmax_files) + '\n')
    log_file.write('TMIN files: ' + str(new_tmin_files) + '\n')

    feedback.pushConsoleInfo("Extracting precipitation data...")
    # Process new APCP files
    if new_pcp_files:
        try:
            correct_factor = float(model.desc['PcpCorrFact'])
        except Exception as e:
            correct_factor = None
        # Get new array
        pcp_startdate = last_pcp_date + timedelta(days=1)
        new_pcp_juliandates, new_pcp_array = \
            ZonalStats(pcp_startdate, new_pcp_enddate,
                       os.path.join(model.Path, model.desc['Shapefile']),
                       model.desc['SubbasinColumn'], new_pcp_files, subcatchmap_res, None,
                       correct_factor, progress)
        # Combine arrays
        pcp_juliandates = numpy.concatenate((pcp_juliandates, new_pcp_juliandates), axis=0)
        pcp_array = numpy.concatenate((pcp_array, new_pcp_array), axis=0)
        feedback.pushConsoleInfo("Writing new precipitation files...")
        # Write files
        stations.writePcpFiles(first_pcp_date, pcp_array, log_file)

    feedback.pushConsoleInfo("Extracting temperature data...")
    # Process Temperature files
    if new_tmax_files and new_tmin_files:
        # TMAX
        if tmax_var_ECMWF in new_tmax_files[0]:
            correct_number = -273.15
        else:
            correct_number = None
        tmp_startdate = last_tmp_date + timedelta(days=1)
        new_tmax_juliandates, new_tmp_max_array = \
            ZonalStats(tmp_startdate, new_tmax_enddate,
                       os.path.join(model.Path, model.desc['Shapefile']),
                       model.desc['SubbasinColumn'], new_tmax_files, subcatchmap_res,
                       correct_number, None, progress)
        # TMIN
        if tmin_var_ECMWF in new_tmin_files[0]:
            correct_number = -273.15
        else:
            correct_number = None
        new_tmin_juliandates, new_tmp_min_array = \
            ZonalStats(tmp_startdate, new_tmin_enddate,
                       os.path.join(model.Path, model.desc['Shapefile']),
                       model.desc['SubbasinColumn'], new_tmin_files, subcatchmap_res,
                       correct_number, None, progress)

        # Make sure tmax and tmin have same end days
        dif = (len(new_tmax_juliandates)-len(new_tmin_juliandates))
        if dif > 0:
            new_tmp_max_array = new_tmp_max_array[:-dif, :]
            new_tmax_juliandates = new_tmax_juliandates[:-dif]
        elif dif < 0:
            new_tmp_min_array = new_tmp_min_array[:-dif, :]
            new_tmin_juliandates = new_tmin_juliandates[:-dif, :]

        feedback.pushConsoleInfo("Writing new temperature files...")
        # Combine arrays
        # TMAX
        tmp_juliandates = numpy.concatenate((tmp_juliandates, new_tmax_juliandates), axis=0)
        tmp_max_array = numpy.concatenate((tmp_max_array, new_tmp_max_array), axis=0)
        # TMIN
        tmp_min_array = numpy.concatenate((tmp_min_array, new_tmp_min_array), axis=0)
        # Write files
        stations.writeTmpFiles(first_tmp_date, tmp_max_array, tmp_min_array, log_file)
