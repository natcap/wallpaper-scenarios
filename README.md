Tiling Landcover Rasters for Scenarios
======================================

This repo contains a script ``wallpaper_raster.py`` that can be used to tile one part of a raster into another given vectors that specify the areas. It can be used at the command line as follows:

```
python wallpaper_raster.py --raster_path_list .\Test_Data\lulc --scenarios_vector_path .\Test_Data\Scenarios.shp --parcels_vector_path .\Test_Data\Test_Parcels.shp
```

Command line arguments
----------------------

 * ``--raster_path_list`` -- a list of at least one path to single band rasters on disk that will be used to wallpaper.
 * ``--scenarios_vector_path`` -- a path to a single layer vector containing any number of polygon features. These features are uniquely identified by a field name of ``"Scenario"`` which can be overridden with the command line argument of ``--scenario_id_field [alternatve field name]``. The features in this vector indicate a single region in each of the rasters given in ``raster_path_list`` which should be used to tile into parcels.
 * ``parcels_vector_path`` -- a path to a single layer vector containing polygon features that indicate where tiling should occur in a given raster. The values written into these regions are copied from the polygons indicated in the Scenarios vector.

Output
------

Output will be generated in a folder in the current working directory called ``"wallpaper_workspace"`` this value can be overriden with the ``--workspace_dir`` command line argument. After a successful run, the directory will contain a set of GeoTiff files named ``{raster_base}_{scenario}.tif`` where ``raster_base`` is the base name of the raster processsed from the ``--raster_path_list`` argument and ``scenario`` is the value of the feature field in the vector given by ``--scenarios_vector_path``. These files will have the coverages indicated by the vector defined at ``parcels_vector_path_list``.

Installation/Requirments
------------------------

Dependancies are specified in `requirements.txt`. Additionally you can use the `therealspring/inspring:latest` docker container to run this script as follows:

```
docker run --rm -it -v %CD%:/usr/local/workspace therealspring/inspring:latest .\wallpaper_raster.py --raster_path_list .\Test_Data\lulc --scenarios_vector_path .\Test_Data\Scenarios.shp --parcels_vector_path .\Test_Data\Test_Parcels.shp
```

If using a Docker container, note that file paths must be below and relative to the current working directory (``%CD%`` on windows and ```pwd``` on Linux).
