##Budyko=group
##Budyko Hydrological Model=name
##ParameterFile|GEOMETRY_FILE|
##ParameterFile|OBS_REACH_FILE|Observed-discharge file|False|True
##ParameterFile|OUTDIR|Output directory for plots|True|True

from middle_layer import main

main(
    obs_reach_file=OBS_REACH_FILE,
    outdir=OUTDIR,
)
