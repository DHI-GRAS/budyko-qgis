# budyko_qgis
QGIS interface to Budyko Hydological Model maintained by DTU Environment

## Installation

Download and install `budyko_model` from https://github.com/KittelC/Budyko_model/archive/master.zip into QGIS Python, e.g. by downloading the archive and `pip`-installing it from the OSGeo4W shell.

Place this folder somewhere below `.qgis2/processing/scripts`.


## Dependencies

These are the dependencies for `Budyko_model` and where to get them for
QGIS Python on Windows

```yaml
- numpy  # -- osgeo
- scipy  # -- osgeo
- matplotlib  # -- osgeo
- osgeo/osr  # -- osgeo
- spotpy  # -- pip
  - numpy  # -- osgeo
  - scipy  # -- osgeo
# - pandas  # -- optional, osgeo
# - mpi4py  # -- optional
# - cmf  # optional, water and solute fluxes -- pip
# - pathos # optional, parallel graph management -- pip
# - matplotlib  # optional, -- osgeo
```
