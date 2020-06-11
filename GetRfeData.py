##Download FEWS-RFE data=name
##Budyko=group
##ParameterFile|dst_folder|Select precipitation folder|True|False
##ParameterString|start_date|Start date [yyyymmdd]. Must be after 20010101.|20130101|False
##ParameterString|end_date|End date [yyyymmdd]. For dates older than a year, the whole year will be downloaded.|20130101|False
##*ParameterExtent|subset_extent|Subset to download. Leave default value to download African dataset.|0,1,0,1

import os
import sys
from datetime import date, datetime
from qgis.core import QgsProcessingException
if not os.path.dirname(scriptDescriptionFile) in sys.path:
    sys.path.append(os.path.dirname(scriptDescriptionFile))
import DownloadRfeClimateData

if os.path.isdir(dst_folder):
    # Creating log file

    with open(os.path.join(dst_folder, "Download_log.txt"), "w") as log_file:
        # Write current date to log file
        now = date.today()
        log_file.write('Run: ' + now.strftime('%Y%m%d') + '\n')
        log_file.write('Data source: FEWS-RFE\n')

        # Get dates
        try:
            start_date = datetime.strptime(start_date, "%Y%m%d").date()
        except ValueError:
            raise QgsProcessingException('Error in data format: \"' + start_date +
                                                 '\". Must be in YYYYMMDD.')

        try:
            end_date = datetime.strptime(end_date, "%Y%m%d").date()
        except ValueError:
            raise QgsProcessingException('Error in data format: ' + end_date +
                                                 '\". Must be in YYYYMMDD.')

        number_of_iterations = float((end_date.year - start_date.year + 1)*3)

        # Download, extract and translate to GeoTIFF
        iteration = 0
        for year in range(start_date.year, end_date.year+1):
            feedback.pushConsoleInfo("Downloading and extracting RFE precipitation data for " +
                                    str(year) + "...")
            if year == now.year:
                if start_date < date(now.year, 1, 1):
                    iteration = DownloadRfeClimateData.RfeImportDays(date(year, 1, 1), end_date,
                                                                     dst_folder, log_file,
                                                                     progress, iteration,
                                                                     number_of_iterations,
                                                                     subset_extent)
                else:
                    iteration = DownloadRfeClimateData.RfeImportDays(start_date, end_date,
                                                                     dst_folder, log_file,
                                                                     progress, iteration,
                                                                     number_of_iterations,
                                                                     subset_extent)
            else:
                iteration = DownloadRfeClimateData.RfeImportYear(year, dst_folder, log_file,
                                                                 progress, iteration,
                                                                 number_of_iterations,
                                                                 subset_extent)
else:
    raise QgsProcessingException('No such directory: \"' + dst_folder + '\" ')
