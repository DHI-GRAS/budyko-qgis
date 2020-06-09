from ECMWFDataServer import ECMWFDataServer
from datetime import date, timedelta, datetime
import os
import processing
from processing.tools import dataobjects
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import shutil


def ECMWFImport(email, token, startdate, enddate, tmax_dst_folder, tmin_dst_folder, LeftLon,
                RightLon, TopLat, BottomLat, progress):
    """Importing ECMWF temperature data using the
    ECMWFDataServer class provided by ECMWF"""
    DownloadDirectory = os.path.join(tmax_dst_folder, 'Temporary')

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Get max enddate (updated once a month, with two months delay: for June 2016, end of March)
    # and min startdate (1979-01-01)
    enddate_adjust = (datetime.now()-timedelta(days=60)).date()
    max_enddate = date(enddate_adjust.year, enddate_adjust.month, 1) - timedelta(days=1)

    min_startdate = datetime.strptime(('1979-01-01'), "%Y-%m-%d").date()
    if startdate < min_startdate:
        startdate = min_startdate
        feedback.pushConsoleInfo("Start date corrected to: " + startdate.strftime('%Y%m%d') + "...")
    if enddate > max_enddate:
        enddate = max_enddate
        feedback.pushConsoleInfo("End date corrected to: " + enddate.strftime('%Y%m%d') + "...")
    if startdate > max_enddate:
        return

    # Get dates
    FirstYear = startdate.year
    FirstMonth = startdate.month
    FirstDay = startdate.day
    LastYear = enddate.year
    LastMonth = enddate.month
    LastDay = enddate.day

    # Start data server
    server = ECMWFDataServer('https://api.ecmwf.int/v1', token, email)

    # Run all at a time
    dst_file = os.path.join(DownloadDirectory,
                            startdate.strftime('%Y%m%d')+'_to_'+enddate.strftime('%Y%m%d')+'.grb')
    GetECMWF(server, FirstYear, FirstMonth, FirstDay, LastYear, LastMonth, LastDay, LeftLon,
             RightLon, TopLat, BottomLat, dst_file, progress)
    tiff_filelist = gdal2GeoTiff_ECMWF_WGS84(dst_file, progress)

    Max_Daily_FileList, Min_Daily_FileList = ECMWF2DailyMaps(tiff_filelist, progress)

    # Move files and clean up
    for f in Max_Daily_FileList:
        try:
            shutil.copy(f, os.path.join(tmax_dst_folder, os.path.split(f)[1]))
        except:
            pass
    for f in Min_Daily_FileList:
        try:
            shutil.copy(f, os.path.join(tmin_dst_folder, os.path.split(f)[1]))
        except:
            pass

    for f in os.listdir(DownloadDirectory):
        try:
            os.remove(f)
        except:
            pass

    try:
        shutil.rmtree(DownloadDirectory)  # Remove Temp dir
    except:
        pass

    server = None


def GetECMWF(server, FirstYear, FirstMonth, FirstDay, LastYear, LastMonth, LastDay, LeftLon,
             RightLon, TopLat, BottomLat, dst_file, progress):
    feedback.pushConsoleInfo("Sending data request to ECMWF. It might take a long time to get it " +
                            "processed, please be patient...")
    server.retrieve({
        'dataset' : "interim",
        'date'    : str(FirstYear) +'-'+ str(FirstMonth).zfill(2) +'-'+ str(FirstDay).zfill(2) + '/to/' + str(LastYear) +'-'+ str(LastMonth).zfill(2) +'-'+ str(LastDay).zfill(2),
        'time'    : "00:00:00/06:00:00/12:00:00/18:00:00",
        'grid'    : "0.75/0.75",
        'step'    : "0",
        'levtype' : "sfc",
        'type'    : "an",
        'param'   : "167.128",
        'area'    : str(TopLat) + '/' + str(LeftLon) + '/' + str(BottomLat) + '/' + str(RightLon),
        'target'  : dst_file
        })

    return


def gdal2GeoTiff_ECMWF_WGS84(Filename, progress):
    feedback.pushConsoleInfo("Translating to GeoTIFF...")
    tiff_filename_base = os.path.split(Filename)[0] + os.sep
    tiff_filelist = []

    d=datetime(1970, 1, 1)

    # Read raster bands from file
    data = gdal.Open(Filename, GA_ReadOnly)
    number_of_bands = data.RasterCount

    # Get extent
    extent = dataobjects.extent([Filename])

    for i in range(1, number_of_bands+1):
        #data = gdal.Open(Filename, GA_ReadOnly)
        band = data.GetRasterBand(i)
        htime = band.GetMetadata()['GRIB_REF_TIME']
        userange = len(htime)-7
        UTCtime_delta = int(band.GetMetadata()['GRIB_REF_TIME'][0:userange])
        #data = None
        tiff_filename = tiff_filename_base + str((d + timedelta(seconds=UTCtime_delta)).year) + \
                        str((d + timedelta(seconds=UTCtime_delta)).month).zfill(2) + \
                        str((d + timedelta(seconds=UTCtime_delta)).day).zfill(2) + '_' + \
                        str((d + timedelta(seconds=UTCtime_delta)).hour).zfill(2) + 'ECMWF.tif'

        # Convert to GeoTIFF using processing GDAL
        param = {'INPUT': Filename, 'OUTSIZE': 100, 'OUTSIZE_PERC': True, 'NO_DATA': "",
                 'EXPAND': 0, 'SRS': 'EPSG:4326', 'PROJWIN': extent, 'SDS': False,
                 'EXTRA': '-b '+str(i), 'OUTPUT': tiff_filename}
        processing.runalg("gdalogr:translate", param)
        tiff_filelist.append(tiff_filename)

    data = None
    return tiff_filelist


def ECMWF2DailyMaps(filelist, progress):
    feedback.pushConsoleInfo("Computing daily maps...")
    # Get all days
    dates = []
    Tmax_Daily_FileList = []
    Tmin_Daily_FileList = []
    for f in filelist:
        dates.append(os.path.split(f)[1][0:8])

    # Get unique dates
    unique_dates = list(set(dates))

    layer = dataobjects.getObjectFromUri(filelist[0])
    extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+\
             str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())

    # Calculate daily maps
    for datestr in unique_dates:
        # If all four daily maps exist
        if dates.count(datestr) == 4:
            maps = []
            # Get the four maps
            for f in filelist:
                if (datestr in f):
                    maps.append(f)

            # Do map calculations using processing GRASS
            # TMAX
            out_file = os.path.split(maps[0])[0] + os.sep + datestr + '_TMAX_' + 'ECMWF' + '.tif'
            Tmax_Daily_FileList.append(out_file)
            formula = 'maximum(maximum(A,B),maximum(C,D))'
            doMapCalc(maps, out_file, formula)

            # TMIN
            out_file = os.path.split(maps[0])[0] + os.sep + datestr + '_TMIN_' + 'ECMWF' + '.tif'
            Tmin_Daily_FileList.append(out_file)
            formula = 'minimum(minimum(A,B),minimum(C,D))'
            doMapCalc(maps, out_file, formula)

    return Tmax_Daily_FileList, Tmin_Daily_FileList


def doMapCalc(maps, out_file, formula):
    param = {'INPUT_A':maps[0], 'INPUT_B':maps[1], 'INPUT_C':maps[2], 'INPUT_D':maps[3],
             'FORMULA':formula, 'OUTPUT':out_file}
    processing.runalg("gdalogr:rastercalculator", param)
