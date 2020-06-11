# Definition of inputs and outputs
# ==================================
##Budyko=group
##Merge, reproject and subset=name
##ParameterMultipleInput|inputImages|Input images|3|
##ParameterCrs|projection|Metric coordinate system (UTM)|
##ParameterExtent|extent|Spatial extent|
##ParameterCrs|extentProjection|Coordinate system of the extent|EPSG:4326|False
##ParameterNumber|resolution|Spatial resolution in target coordinate system (leave as 0 for no change)|0.0|100000000.0|0.0|
##OutputRaster|outputImage|Output image

# This script is not made as a model because there is no ParameterMultipleInput in the QGIS 2.x
# modeler (it exists in QGIS 3.x)

# Run Build Virtual Raster to merge the images
params = {
    "INPUT": inputImages,
    "RESOLUTION": "0",
    "SEPARATE": False,
    "PROJ_DIFFERENCE": False,
    "OUTPUT": None,
}
vrtOutput = processing.runalg("gdalogr:buildvirtualraster", params)

# Run GDAL warp to reproject, resample and subset
params = {
    "INPUT": vrtOutput["OUTPUT"],
    "DEST_SRS": projection,
    "METHOD": 5,
    "TR": resolution,
    "USE_RASTER_EXTENT": True,
    "RASTER_EXTENT": extent,
    "EXTENT_CRS": extentProjection,
    "NO_DATA": "-32768",
    "OUTPUT": outputImage,
}
processing.runalg("gdalogr:warpreproject", params)
