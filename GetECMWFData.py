##Download ECMWF data=name
##Budyko=group
##ParameterFile|tmax_dst_folder|Select maximum temperature folder|True|False
##ParameterFile|tmin_dst_folder|Select minimum temperature folder|True|False
##ParameterString|start_date|Start date [yyyymmdd]. Must be after 19790101|20130101|False
##ParameterString|end_date|End date [yyyymmdd]. It is recomended that no more than 6 months of data is downloaded at a time.|20130601|False
##*ParameterExtent|subset_extent|Subset to download. Leave default value to download Africa dataset|-20,55,-40,40
##ParameterString|email|Email registered with ECMWF||False
##ParameterString|token|ECMWF token||False

import os
import sys
from datetime import datetime
from qgis.core import QgsProcessingException
if not os.path.dirname(scriptDescriptionFile) in sys.path:
    sys.path.append(os.path.dirname(scriptDescriptionFile))
import DownloadECMWFClimateData

[left_long, right_long, bottom_lat, top_lat] = [float(i) for i in subset_extent.split(",")]

# Check coordinates
if (left_long >= right_long) or (bottom_lat >= top_lat):
    raise QgsProcessingException('Error in coordinates: \"Left :' + str(left_long) +
    '< Right: ' + str(right_long) + ', Top :' + str(top_lat) + '> Bottom :' + str(bottom_lat) + '\"')

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

if os.path.isdir(tmax_dst_folder) and os.path.isdir(tmin_dst_folder):
    # Download, extract and translate to GeoTIFF
    DownloadECMWFClimateData.ECMWFImport(email, token, start_date, end_date, tmax_dst_folder,
                                         tmin_dst_folder, left_long, right_long, top_lat,
                                         bottom_lat, progress)
else:
    raise QgsProcessingException('No such directory: \"' + dst_folder + '\" ')
