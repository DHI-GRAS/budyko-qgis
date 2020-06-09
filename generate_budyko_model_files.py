##Budyko=group
##Generate Budyko model files=name
##ParameterFile|MODEL_FILEPATH|Storage location for model description file|True|False
##ParameterString|MODEL_NAME|Name of the model|
##ParameterString|MODEL_STARTDATE|Starting date of the model (YYYYMMDD)|20000101|
##ParameterVector|MODEL_SUBSHAPES|Model sub-basin polygon file (in lat-lon)|2|False
##ParameterVector|MODEL_NETWORK|Model river network file (in lat-lon)|1|False
##*ParameterString|MODEL_SUBCOLUMN|Name of sub-basin shapefile column holding sub IDs|ID|
##*ParameterString|MODEL_AREACOLUMN|Name of sub-basin shapefile column holding subbasin area|area
##ParameterFile|MODEL_CLIMSTATS|Storage location for model climate station file|True|False
##*ParameterNumber|MODEL_PCPFAC|Precipitation scaling factor|0.1|10.0|1.0
##ParameterVector|MODEL_CENTROIDFILE|Model sub-basin centroid point file (in lat-lon)|0|False
##*ParameterString|MODEL_LATCOLUMN|Name of centroid file column holding latitude|ycoord
##*ParameterString|MODEL_LONCOLUMN|Name of centroid file column holding longitude|xcoord
##*ParameterString|MODEL_ELEVCOLUMN|Name of centroid file column holding mean elevation|elev_mean

import os
from datetime import date

from budyko_model.modelfile import ModelFile
from processing.tools import dataobjects

import processing

model_description_file = os.path.join(MODEL_FILEPATH, MODEL_NAME+".txt")

feedback.pushConsoleInfo("Writing model description file...")
modelfile = open(model_description_file, 'w')
modelfile.writelines('Model description file\r\n')
modelfile.writelines('ModelName ' + MODEL_NAME + '\r\n')
modelfile.writelines('Type Hist\r\n')
modelfile.writelines('ModelStartDate ' + MODEL_STARTDATE + '\r\n')
modelfile.writelines('Shapefile ' + os.path.relpath(MODEL_SUBSHAPES, MODEL_FILEPATH) + '\r\n')
modelfile.writelines('RiverNetwork ' + os.path.relpath(MODEL_NETWORK, MODEL_FILEPATH) + '\r\n')
modelfile.writelines('SubbasinColumn ' + MODEL_SUBCOLUMN + '\r\n')
modelfile.writelines('Stations ' + os.path.relpath(MODEL_CLIMSTATS, MODEL_FILEPATH) + os.sep + MODEL_NAME + 'Stations.txt' + '\r\n')
modelfile.writelines('StationsTemp ' + os.path.relpath(MODEL_CLIMSTATS, MODEL_FILEPATH) + os.sep + MODEL_NAME + 'StationsTemp.txt' + '\r\n')
modelfile.writelines('PcpCorrFact ' + str(MODEL_PCPFAC) + '\r\n')
modelfile.writelines('Centroidfile ' + os.path.relpath(MODEL_CENTROIDFILE, MODEL_FILEPATH) + '\r\n')
modelfile.writelines('LatColumn ' + str(MODEL_LATCOLUMN) + '\r\n')
modelfile.writelines('LonColumn ' + str(MODEL_LONCOLUMN) + '\r\n')
modelfile.writelines('ElevColumn ' + str(MODEL_ELEVCOLUMN) + '\r\n')
modelfile.writelines('AreaColumn ' + str(MODEL_AREACOLUMN) + '\r\n')
modelfile.close()

# Generate climate station file
# Write station file
feedback.pushConsoleInfo("Reading data from catchment vector files...")
model = ModelFile(model_description_file, check_for_missing_files=False)
layer = dataobjects.getObjectFromUri(os.path.join(model.Path, model.desc['Shapefile']))
extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+\
         str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
subbasin_filename = os.path.join(model.Path, model.desc['SubbasinColumn'] + '.txt')
v_db_select_params = {"map": os.path.join(model.Path, model.desc['Shapefile']),
                      "layer": 1, "columns": model.desc['SubbasinColumn'], "-c": False,
                      "separator": ",", "where": "", "vertical_separator": "", "null_value": "",
                      "-v": False, "-r": False, "GRASS_REGION_PARAMETER": extent,
                      "GRASS_MIN_AREA_PARAMETER": 0.0001, "GRASS_SNAP_TOLERANCE_PARAMETER": -1,
                      "file": subbasin_filename}
processing.runalg("grass7:v.db.select", v_db_select_params)
area_filename = os.path.join(model.Path, model.desc['AreaColumn'] + '.txt')
v_db_select_params.update(zip(["columns", "file"], [model.desc['AreaColumn'], area_filename]))
processing.runalg("grass7:v.db.select", v_db_select_params)

layer = dataobjects.getObjectFromUri(os.path.join(model.Path, model.desc['Centroidfile']))
extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+\
         str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
lat_filename = os.path.join(model.Path, model.desc['LatColumn'] + '.txt')
v_db_select_params = {"map": os.path.join(model.Path, model.desc['Centroidfile']),
                      "layer": 1, "columns": model.desc['LatColumn'], "-c": False,
                      "separator": ",", "where": "", "vertical_separator": "", "null_value": "",
                      "-v": False, "-r": False, "GRASS_REGION_PARAMETER": extent,
                      "GRASS_MIN_AREA_PARAMETER": 0.0001, "GRASS_SNAP_TOLERANCE_PARAMETER": -1,
                      "file": lat_filename}
processing.runalg("grass7:v.db.select", v_db_select_params)
lon_filename = os.path.join(model.Path, model.desc['LonColumn'] + '.txt')
v_db_select_params.update(zip(["columns", "file"], [model.desc['LonColumn'], lon_filename]))
processing.runalg("grass7:v.db.select", v_db_select_params)
elev_filename = os.path.join(model.Path, model.desc['ElevColumn'] + '.txt')
v_db_select_params.update(zip(["columns", "file"], [model.desc['ElevColumn'], elev_filename]))
processing.runalg("grass7:v.db.select", v_db_select_params)

# Read subbasins from file
subbasins = []
with open(subbasin_filename, 'r') as fp:
    for line in fp.readlines()[1:]:
        subbasins.append(float(line))

latitudes = []
with open(lat_filename, 'r') as fp:
    for line in fp.readlines()[1:]:
        latitudes.append(float(line))

longitudes = []
with open(lon_filename, 'r') as fp:
    for line in fp.readlines()[1:]:
        longitudes.append(float(line))

elevations = []
with open(elev_filename, 'r') as fp:
    for line in fp.readlines()[1:]:
        elevations.append(float(line))

area = []
with open(area_filename, 'r') as fp:
    for line in fp.readlines()[1:]:
        area.append(float(line))

feedback.pushConsoleInfo("Writing station files..")
with open(os.path.join(model.Path, model.desc['StationsTemp']), 'w') as stp,\
     open(os.path.join(model.Path, model.desc['Stations']), 'w') as sp:
    stp.writelines('ID,NAME,LAT,LONG,ELEVATION,AREA' + '\n')
    sp.writelines('ID,NAME,LAT,LONG,ELEVATION,AREA' + '\n')
    startdate = date(int(MODEL_STARTDATE[0:4]), int(MODEL_STARTDATE[4:6]),
                     int(MODEL_STARTDATE[6:8]))
    pfirstlinenstat = startdate.strftime('%Y%m%d')
    tfirstlinenstat = startdate.strftime('%Y%m%d')
    for n in range(0, len(subbasins)):
        lat = latitudes[n]
        lon = longitudes[n]
        elev = elevations[n]
        subArea = area[n]
        towrite = "%1.0f" % subbasins[n] + ',' + "%06d" % subbasins[n] + ',' + "%.2f" % lat +\
                  ',' + "%.2f" % lon + ',' + "%.2f" % elev + ',' + "%.2f" % subArea + '\n'
        sp.writelines(towrite)
        towrite_temp = "%1.0f" % subbasins[n] + ',' + "%06d" % subbasins[n] + 'temp,' +\
                       "%.2f" % lat + ',' + "%.2f" % lon + ',' + "%.2f" % elev + ',' +\
                       "%.2f" % subArea + '\n'
        stp.writelines(towrite_temp)
        pStation_n_name = os.path.join(MODEL_CLIMSTATS, "%06d" % subbasins[n] + '.txt')
        tStation_n_name = os.path.join(MODEL_CLIMSTATS, "%06d" % subbasins[n] + 'temp.txt')
        with open(pStation_n_name, 'w') as pStation_n_file:
            pStation_n_file.writelines(pfirstlinenstat + '\n')
        with open(tStation_n_name, 'w') as tStation_n_file:
            tStation_n_file.writelines(tfirstlinenstat + '\n')

with open(model_description_file, 'a') as modelfile:
    modelfile.writelines('TotalNoSubs ' + str(len(subbasins)) + '\r\n')
