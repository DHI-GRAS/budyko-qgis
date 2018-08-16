import os
from datetime import date, timedelta
import math
import processing
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.tools import dataobjects
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly


def ZonalStats(start_date, end_date, model_folder, model_name, vec_name, sb_column,
               subcatchmap_res, file_list, log_file, corr_by_num=None, corr_by_fact=None):

    if not os.path.isfile(vec_name):
        raise GeoAlgorithmExecutionException('No shapefile: \"' + vec_name + '\" ')
    if not file_list:
        raise GeoAlgorithmExecutionException('List of files is empty')

    first = True

    # Get Subbasins from shapefile and save to txt file
    layer = dataobjects.getObjectFromUri(vec_name)
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+\
             str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
    subbasin_filename = os.path.join(model_folder, sb_column + '.txt')
    v_db_select_params = {"map": vec_name, "layer": 1, "columns": sb_column, "-c": False,
                          "separator": ",", "where": "", "vertical_separator": "", "null_value": "",
                          "-v": False, "-r": False, "GRASS_REGION_PARAMETER": extent,
                          "GRASS_MIN_AREA_PARAMETER": 0.0001, "GRASS_SNAP_TOLERANCE_PARAMETER": -1,
                          "file": subbasin_filename}
    processing.runalg("grass:v.db.select", v_db_select_params)

    # Read subbasins from file
    subbasins = []
    with open(subbasin_filename, 'r') as fp:
        for line in fp.readlines[1:]:
            subbasins.append(int(line))
    log_file.write("Subbasins: %s \n" % subbasins)

    # Creating a list of dates (year + julian day)
    dates = []
    for n in range((end_date-start_date).days + 1):
        d = start_date + timedelta(days=n)
        year = d.year
        day = (d - date(year, 1, 1)).days + 1
        dates.append(str(year) + str(day).zfill(3))

    # Initialising array for results
    result_ts = np.ones([len(dates),len(subbasins)]) * -99.0

    R_Xres_old = -9999
    R_Yres_old = -9999
    R_Xleft_old = -9999
    R_Ytop_old = -9999
    R_Xsize_old = -9999
    R_Ysize_old = -9999
    # Extracting data and saving in array
    for file_name in file_list:
        if (file_name.endswith('.tif')) or (file_name.endswith('.tiff')):
            f = os.path.split(file_name)[1]
            file_date = date(int(f[0:4]), int(f[4:6]), int(f[6:8]))
            year = file_date.year
            day = (file_date - date(year, 1, 1)).days + 1
            ind = dates.index(str(year) + str(day).zfill(3))  # index in dates list

            # Get info from raster
            dataset = gdal.Open(file_name, GA_ReadOnly)
            if dataset is None:
                    raise GeoAlgorithmExecutionException('Cannot open file ' + file_name)
            R_Xsize = dataset.RasterXSize
            R_Ysize = dataset.RasterYSize
            geotransform = dataset.GetGeoTransform()
            R_Xres = float('%.3f' % geotransform[1])
            R_Yres = float('%.3f' % geotransform[5])
            R_Xleft = float('%.3f' % geotransform[0])
            R_Ytop = float('%.3f' % geotransform[3])
            R_map_array = dataset.ReadAsArray()
            b = dataset.GetRasterBand(1)
            NoDataValue = b.GetNoDataValue()
            if not dataset.GetProjection().split('DATUM["')[1][0:8] == 'WGS_1984':
                raise GeoAlgorithmExecutionException('Datafiles must be in WGS_1984 datum')
            dataset = None  # Closing dataset
            b = None

            # Check is raster have same size and resolution as last processed raster, if no new
            # coefficient maps will be created
            if (first) or (R_Xres_old != R_Xres) or (R_Yres_old != R_Yres) or\
               (R_Xleft_old != R_Xleft) or (R_Ytop_old != R_Ytop) or (R_Xsize_old != R_Xsize) or\
               (R_Ysize_old != R_Ysize):

                log_file.write("Creating maps \n")
                # Rasterize model shapefile
                layer = dataobjects.getObjectFromUri(vec_name)
                V_Xmin = math.floor(layer.extent().xMinimum()) - (R_Xres/2)
                V_Xmax = math.ceil(layer.extent().xMaximum()) + (R_Xres/2)
                V_Ymin = math.floor(layer.extent().yMinimum()) + (R_Yres/2)
                if layer.extent().yMinimum() < V_Ymin:
                    V_Ymin = math.floor(layer.extent().yMinimum()) - (R_Yres/2)
                V_Ymax = math.ceil(layer.extent().yMaximum()) - (R_Yres/2)
                if layer.extent().yMaximum() > V_Ymax:
                    V_Ymax = math.ceil(layer.extent().yMaximum()) + (R_Yres/2)
                extent = str(V_Xmin)+","+str(V_Xmax)+","+str(V_Ymin)+","+str(V_Ymax)
                OutRName = os.path.join(model_folder, + model_name + '_Raster.tif')
                params = {"INPUT": vec_name, "FIELD": sb_column, "DIMENSIONS": 1,
                          "WIDTH": subcatchmap_res, "HEIGHT": subcatchmap_res, "RAST_EXT": extent,
                          "RTYPE": 5, "NO_DATA": "", "COMPRESS": 4, "JPEGCOMPRESSION": 75,
                          "ZLEVEL": 6, "PREDICTOR": 1, "TILED": False, "BIGTIFF": 0, "TFW": False,
                          "EXTRA": "", "OUTPUT": OutRName}
                processing.runalg("gdalogr:rasterize", params)
                # Get info from new raster
                dataset = gdal.Open(OutRName, GA_ReadOnly)
                if dataset is None:
                    raise GeoAlgorithmExecutionException('Cannot open file ' + OutRName)
                sc = dataset.ReadAsArray()
                geotransform = dataset.GetGeoTransform()
                sc_Xres = geotransform[1]
                sc_Yres = geotransform[5]
                sc_Xleft = geotransform[0]
                sc_Ytop = geotransform[3]
                if not dataset.GetProjection().split('DATUM["')[1][0:8] == 'WGS_1984':
                    raise GeoAlgorithmExecutionException('Shapefile must be in WGS_1984 datum')
                dataset = None  # Closing dataset

                # Check resolution
                if (abs(sc_Xres) > abs(R_Xres)) or (abs(sc_Yres) > abs(R_Ysize)):
                    raise GeoAlgorithmExecutionException('Resolution of subcatchment map must be' +
                                                         ' less that raster data maps, try using' +
                                                         ' a smaller subcatchment map resolution' +
                                                         ' as input.')

                # Check for all subcatchments
                if not len(np.unique(sc))-1 == len(subbasins):
                    raise GeoAlgorithmExecutionException('Not all subcatchment are found in' +
                                                         ' raster map: ' + OutRName + ', try' +
                                                         ' using a smaller subcatchment map' +
                                                         ' resolution as input.')

                # Create maps for each subcatchment for use in coefficients map method
                # Create array with a unique number for each pixel. Area as rastarized vector map
                # and resolution as raster data map
                unique_array = np.resize(range(1, int((V_Xmax-V_Xmin) / abs(R_Xres)) *
                                                  int((V_Ymax-V_Ymin) / abs(R_Yres))+1),
                                            [int((V_Ymax-V_Ymin) / abs(R_Yres)),
                                             int((V_Xmax-V_Xmin) / abs(R_Xres))])
                # x and y resoution factor between rasterized vector and unique_array
                x_factor = int(round(sc.shape[1] / float(unique_array.shape[1])))
                y_factor = int(round(sc.shape[0] / float(unique_array.shape[0])))
                # Initializing array for resampling and working array
                unique_array_resample = np.zeros(sc.shape)
                ones_array = np.ones([y_factor, x_factor])
                # Resampling
                # looping x
                for m in range(0, unique_array.shape[1]):
                    # looping y
                    for n in range(0, unique_array.shape[0]):
                        value = unique_array[n, m]
                        unique_array_resample[n*y_factor:n*y_factor+y_factor,
                                              m*x_factor:m*x_factor+x_factor] = ones_array * value

                # Creating map for each subcatchment and save in dict
                catchment_maps = {}
                for catchment in subbasins:
                    # Init maps
                    temp_map = np.where(sc == catchment, unique_array_resample, 0.0)
                    catch_size = len(np.nonzero(temp_map)[0])
                    catchment_map =  unique_array * 0.0
                    catchment_map = catchment_map.reshape(1, catchment_map.size)

                    # Calculate coefficients
                    for i in np.unique(temp_map)[1:]:
                        count = len(np.nonzero(np.where(temp_map == i, temp_map, 0.0))[0]) /\
                                float(catch_size)
                        catchment_map[0, int(i-1)] = count

                    # Coefficients map
                    catchment_map = catchment_map.reshape(unique_array.shape)

                    # Place coefficient map in array with same size as raster data map
                    catchment_map_large = np.zeros([R_Ysize, R_Xsize])
                    x_indent = abs((R_Xleft - sc_Xleft) / R_Xres)
                    y_indent = abs((R_Ytop - sc_Ytop) / R_Yres)
                    # looping x
                    for m in range(0, catchment_map.shape[1]):
                        # looping y
                        for n in range(0, catchment_map.shape[0]):
                            catchment_map_large[int(y_indent+n), int(x_indent+m)] =\
                                catchment_map[n, m]

                    # Put final coefficient map in a dict with key = 'subcatch ID'
                    catchment_maps[str(catchment)] = catchment_map_large

                # Values for comparing next raster data map
                first = False
                R_Xres_old = R_Xres
                R_Yres_old = R_Yres
                R_Xleft_old = R_Xleft
                R_Ytop_old = R_Ytop
                R_Xsize_old = R_Xsize
                R_Ysize_old = R_Ysize

            if NoDataValue is not None:
                    R_map_array[R_map_array == NoDataValue] = np.nan

            # Extract data from raster map using coefficients maps
            for catchment in subbasins:
                # Check for NoDataValues
                if (np.isnan(R_map_array[catchment_maps[str(catchment)] > 0])).any():
                    result_ts[ind, catchment-1] = float(-99.0)
                elif corr_by_num is not None:
                    value = np.nansum((R_map_array+corr_by_num) * catchment_maps[str(catchment)])
                    result_ts[ind, catchment-1] = float(value)
                elif corr_by_fact is not None:
                    value = np.nansum((R_map_array*corr_by_fact) * catchment_maps[str(catchment)])
                    result_ts[ind, catchment-1] = float(value)
                else:
                    value = np.nansum(R_map_array * catchment_maps[str(catchment)])
                    result_ts[ind, catchment-1] = float(value)

    # Return results
    return dates, result_ts
