import urllib
import tarfile
from datetime import date, timedelta
import os
import processing
from processing.tools import dataobjects
import shutil


def RfeImportYear(year, TargetDirectory, log_file, progress, iteration, number_of_iterations,
                  subset_extent):
    """Importing and extracting FEWS RFE from web server for a given year."""
    # Set initial values
    iteration += 1
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary'
    BIL_filelist = []

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Downloading climate data
    try:
        UrlToRead ='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/daily/rfe/downloads/yearly/rfe_' + str(year) + '.tar.gz'
        dst_file = DownloadDirectory + os.sep + 'rfe_' + str(year) + '.tar.gz'
        rday = urllib.urlretrieve(UrlToRead, dst_file)
        progress.setPercentage(iteration/number_of_iterations*100)
        iteration += 1
        feedback.pushConsoleInfo("Extracting data...")
        # Extract year
        tar = tarfile.open(dst_file)
        tar.extractall(DownloadDirectory)
        tar.close()
        # Extract days
        tar_dir = dst_file.split('.tar.gz')[0]
        if os.path.isdir(tar_dir):
            dirs = os.listdir(tar_dir)
            for f in dirs:
                dst_file = tar_dir + os.sep + f
                tar = tarfile.open(dst_file)
                tar.extractall(DownloadDirectory)
                tar.close()
                BIL_filelist.append(DownloadDirectory + os.sep + f.split('.tar.gz')[0] + '.bil')
        progress.setPercentage(iteration/number_of_iterations*100)
    except tarfile.ReadError:
        tar.close()
        os.remove(dst_file)

    # Translate to GeoTIFF
    iteration = Rfe2GeoTIFF_WGS84(BIL_filelist, TargetDirectory, log_file, progress, iteration,
                                  number_of_iterations, subset_extent)
    try:
        shutil.rmtree(DownloadDirectory)  # Remove Temp dir
    except:
        pass
    return iteration


def RfeImportDays(startdate, enddate, TargetDirectory, log_file, progress, iteration,
                  number_of_iterations, subset_extent):
    """Importing and extracting FEWS RFE from web server for a given year"""
    # Set initial values
    iteration += 2
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary'
    BIL_filelist = []

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)

    # Get date info
    FirstYear = startdate.year
    LastYear = enddate.year

    # Looping through years
    for i in range(FirstYear, LastYear+1):
        if i == FirstYear:
            StartDay = (startdate - date(FirstYear, 1, 1)).days + 1
        else:
            StartDay = 1
        if i == LastYear:
            EndDay = (enddate-date(LastYear, 1, 1)).days + 1
        else:
            EndDay = (date(i, 12, 31) - date(i, 1, 1)).days + 1

        # Looping through days
        for j in range(StartDay, EndDay+1):
            # Downloading climate data
            try:
                daystr = str(i)+str(j)
                UrlToRead ='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/daily/rfe/downloads/daily/rain_' + daystr + '.tar.gz'
                dst_file = DownloadDirectory + os.sep + 'rain_' + daystr + '.tar.gz'
                rday=urllib.urlretrieve(UrlToRead, dst_file)
                # Extract
                tar = tarfile.open(dst_file)
                tar.extractall(DownloadDirectory)
                tar.close()
                BIL_filelist.append(dst_file.split('.tar.gz')[0] + '.bil')
            except tarfile.ReadError:
                try:
                    tar.close()
                except:
                    None
                os.remove(dst_file)

    progress.setPercentage(iteration/number_of_iterations*100)

    # Translate to GeoTIFF
    iteration = Rfe2GeoTIFF_WGS84(BIL_filelist, TargetDirectory, log_file, progress, iteration,
                                  number_of_iterations, subset_extent)
    try:
        shutil.rmtree(DownloadDirectory)  # Remove Temp dir
    except:
        pass
    return iteration


def Rfe2GeoTIFF_WGS84(BIL_filelist, dst_folder, log_file, progress, iteration,
                      number_of_iterations, subset_extent):
    """OBS: Files must be in WGS84 """

    iteration += 1
    feedback.pushConsoleInfo("Translating to GeoTIFF...")
    for BIL_filename in BIL_filelist:
        filename = os.path.split(BIL_filename)[1].split('.bil')[0]
        file_date = date(int(filename[5:9]), 1, 1) + timedelta(days=int(filename[9:])-1)
        TIFF_filename = os.path.join(dst_folder,
                                     file_date.strftime('%Y%m%d') + '_' + filename[0:5] + '.tif')
        call_gdal_translate(BIL_filename, TIFF_filename, subset_extent, progress)
    progress.setPercentage(iteration/number_of_iterations*100)
    return iteration


def call_gdal_translate(in_filename, out_filename, newExtent, progress):

    try:

        ext = dataobjects.extent([in_filename])
        if ext == '0,0,0,0':
            feedback.pushConsoleInfo("Cannot find downloaded raster extent! Not subsetting.")
            return
        [xmin, xmax, ymin, ymax] = [float(i) for i in ext.split(",")]

        # get the minimum extent of the subset extent and the file extent
        if not newExtent == "0,1,0,1":
            extents = newExtent.split(",")
            try:
                [nxmin, nxmax, nymin, nymax] = [float(i) for i in extents]
            except ValueError:
                feedback.setProgressText('Invalid subset extent! Not subsetting.')
                return
            xmin = max(nxmin, xmin)
            xmax = min(nxmax, xmax)
            ymin = max(nymin, ymin)
            ymax = min(nymax, ymax)

        subset = str(xmin)+","+str(xmax)+","+str(ymin)+","+str(ymax)

        # call gdal_translateconvertformat
        feedback.setProgressText('Processing '+out_filename)
        print('Processing '+out_filename)
        param = {'INPUT': in_filename, 'OUTSIZE': 100, 'OUTSIZE_PERC': True, 'NO_DATA': "",
                 'EXPAND': 0, 'SRS': "EPSG:4326", 'PROJWIN': subset, 'SDS': False, 'RTYPE': 5,
                 'COMPRESS': 4, 'JPEGCOMPRESSION': 75, 'ZLEVEL': 6, 'PREDICTOR': 1, 'TILED': False,
                 'BIGTIFF': 0, 'TFW': False, 'EXTRA': '-co "COMPRESS=LZW"', 'OUTPUT': out_filename}
        processing.runalg('gdalogr:translate', param)

    except Exception as e:
        feedback.pushConsoleInfo('Fail')
