import os
from datetime import date, timedelta
import processing
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.tools import dataobjects, system
import numpy as np


def ZonalStats(start_date, end_date, vec_name, sb_column, file_list, subcatchmap_res,
               corr_by_num=None, corr_by_fact=None, progress = None):

    if not os.path.isfile(vec_name):
        raise GeoAlgorithmExecutionException('No shapefile: \"' + vec_name + '\" ')
    if not file_list:
        raise GeoAlgorithmExecutionException('List of files is empty')

    # Creating a list of dates (year + julian day)
    dates = []
    for n in range((end_date-start_date).days + 1):
        d = start_date + timedelta(days=n)
        dates.append(d.strftime("%Y%j"))

    # Initialising array for results
    layer = dataobjects.getObjectFromUri(vec_name)
    if layer.crs().toProj4() != "+proj=longlat +datum=WGS84 +no_defs":
        raise IOError('Vector file must be in geographic WGS 1984 projection')
    result_ts = np.ones([len(dates), layer.featureCount()]) * -99.0

    # Extracting data and saving in array
    for file_name in file_list:
        if (file_name.endswith('.tif')) or (file_name.endswith('.tiff')):
            f = os.path.split(file_name)[1]
            file_date = date(int(f[0:4]), int(f[4:6]), int(f[6:8]))
            ind = dates.index(file_date.strftime("%Y%j"))  # index in dates list
        else:
            continue
        if progress is not None:
            progress.setConsoleInfo("Processing %s..." % file_name)

        # Check the raster projection and get the resolution
        raster = dataobjects.getObjectFromUri(file_name)
        if raster.crs().toProj4() != "+proj=longlat +datum=WGS84 +no_defs":
            raise IOError('Datafiles must be in geographic WGS 1984 projection')
        resolution = raster.rasterUnitsPerPixelX()

        # Resample raster to given resolution
        temp_rast_name = system.getTempFilename("tif")
        warp_params = {"INPUT": file_name, "OUTPUT": temp_rast_name, "DEST_SRS": "EPSG:4326",
                       "METHOD": 0, "TR": subcatchmap_res, "USE_RASTER_EXTENT": True,
                       "RASTER_EXTENT": dataobjects.extent([layer]), "EXTENT_CRS": "EPSG:4326"}
        processing.runalg("gdalogr:warpreproject", warp_params)
        out_rast_name = system.getTempFilename("tif")

        # Apply correction factors if given and normalize resampled data so that sums in a given
        # zone are the same as in original raster
        normalization_factor = resolution**2/float(subcatchmap_res)**2
        if corr_by_num is not None:
            formula = "(A+%f)/%f" % (corr_by_num, normalization_factor)
        elif corr_by_fact is not None:
            formula = "(A*%f)/%f" % (corr_by_fact, normalization_factor)
        else:
            formula = "A/%f" % (normalization_factor)
        calculator_params = {"INPUT_A": temp_rast_name, "OUTPUT": out_rast_name,
                             "FORMULA": formula}
        processing.runalg("gdalogr:rastercalculator", calculator_params)

        # Run zonal stats
        zs_output_name = system.getTempFilename("shp")
        zonal_statistics_params = {"INPUT_RASTER": out_rast_name, "RASTER_BAND": 1,
                                   "INPUT_VECTOR": vec_name, "COLUMN_PREFIX": "stats_",
                                   "GLOBAL_EXTENT": False, "OUTPUT_LAYER": zs_output_name}
        processing.runalg("qgis:zonalstatistics", zonal_statistics_params)

        # Save result
        zs_output = dataobjects.getObjectFromUri(zs_output_name)
        for feature in zs_output.getFeatures():
            subbasin_id = feature[sb_column]
            subbasin_value = feature["stats_sum"]
            try:
                result_ts[ind, subbasin_id-1] = subbasin_value
            except TypeError:
                result_ts[ind, subbasin_id-1] = -99.0

    # Return results
    return dates, result_ts
