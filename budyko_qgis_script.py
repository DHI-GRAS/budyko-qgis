##Budyko=group
##Budyko Hydrological Model=name
##ParameterFile|GEOMETRY_FILE|Geometry setup|False|False
##ParameterFile|MODEL_FILE|Model setup|False|False
##ParameterFile|OBS_REACH_FILE|Observed-discharge file|False|False
##ParameterFile|PARAMETER_FILE|Model parameter file|False|True
##ParameterNumber|REACH_NUMBER|Reach number considered|0|10000|0
##ParameterString|STARTDATE|Start date YYYYJJJ|
##ParameterSelection|OUTPUT_TYPE|Output type|Hydrograph;Climatology;FDC|0
##OutputDirectory|OUTDIR|Output directory for plots
##ParameterSelection|TIME_STAMP|Time resolution|daily;monthly|0
##*ParameterNumber|N_CLASSES|Number of volume classes for FDC|0|1000|20
##*ParameterString|TITLE|Title for plot|||True

from budyko_model.scripts import middle_layer

middle_layer.main(
    geometry_file=GEOMETRY_FILE,
    model_file=MODEL_FILE,
    parameter_file=PARAMETER_FILE,
    obs_reach_file=OBS_REACH_FILE,
    outdir=OUTDIR,
    reach_number=REACH_NUMBER,
    startdate=STARTDATE,
    output_type=OUTPUT_TYPE,
    time_stamp=TIME_STAMP,
    n_classes=N_CLASSES,
    title=TITLE)
