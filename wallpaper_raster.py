"""Tile a raster by another raster in an area defined by a mask."""
import argparse
import logging
import os
import sys

from osgeo import gdal
import pygeoprocessing

gdal.SetCacheMax(2**27)

logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
    stream=sys.stdout)

LOGGER = logging.getLogger(__name__)


def _makedirs(dir_path):
    """Make a directory at `dir_path`."""
    try:
        os.makedirs(dir_path)
    except OSError:
        pass


def _get_vector_fields(vector_path, field_name):
    """Return list of unique values in `field_name` in `vector_path`."""
    vector = gdal.OpenEx(vector_path, gdal.OF_VECTOR)
    layer = vector.GetLayer()
    return {feature.GetField(field_name) for feature in layer}


def _extract_intersecting_array_from_raster(
        feature, feature_projection_wkt, raster_path):
    """Extract numpy array from the raster that intersects with the feature.

    Args:
        feature (ogr.Feature): feature to use as a georeference to extract
            the array.
        feature_projection_wkt (str): a WKT form of the feature SRS.
        raster_path (str): path to raster to extract the intersecting
            bounding box from.

    """
    raster_info = pygeoprocessing.get_raster_info(raster_path)
    raster_info = pygeoprocessing.get_raster_info(raster_path)
    raster = gdal.OpenEx(raster_path, gdal.OF_RASTER)
    raster_gt_inv = gdal.InvGeoTransform(raster_info['geotransform'])

    # get the boundary of the feature in non-interleaved format,
    # .GetEnvelope returns in interleaved i.e.
    # (x_min, x_max, y_min, y_max) to
    # (x_min, y_min, x_max, y_max)
    scenario_boundary = [
        feature.GetGeometryRef().GetEnvelope()[i]
        for i in [0, 2, 1, 3]]
    scenario_bb = pygeoprocessing.transform_bounding_box(
        scenario_boundary,
        feature_projection_wkt,
        raster_info['projection_wkt'])
    LOGGER.debug(f'{scenario_boundary} {scenario_bb}')

    x_min, y_min = [
        int(v) for v in gdal.ApplyGeoTransform(
            raster_gt_inv, scenario_bb[0], scenario_bb[3])]
    x_max, y_max = [
        int(v) for v in gdal.ApplyGeoTransform(
            raster_gt_inv, scenario_bb[2], scenario_bb[1])]

    array = raster.ReadAsArray(
        xoff=x_min, yoff=y_min, xsize=x_max-x_min, ysize=y_max-y_min)
    return array


def _create_vector_mask(
        base_raster_path, vector_path, target_mask_raster_path):
    """Create a nodata/1 mask of `raster` that is 1 where vector covers.

    Args:
        base_raster_path (str): path to base raster to use as size/projection
            for `target_mask_raster_path`.
        vector_path (str): path to vector to use as mask for base
        target_mask_raster_path (str): file that is created that is nodata
            by default and 1 where vector intersects.

    Returns:
        None.

    """
    pygeoprocessing.new_raster_from_base(
        base_raster_path, target_mask_raster_path, gdal.GDT_Byte, [0])
    pygeoprocessing.rasterize(
        vector_path, target_mask_raster_path, burn_values=[1])


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description='Tile a raster by another raster with a mask')
    parser.add_argument(
        '--raster_path_list', nargs='+', required=True,
        help='Paths to base raster to tile over')
    parser.add_argument(
        '--scenarios_vector_path', help=(
            'This vector defines the region in the base raster that will act '
            'as the tile to wallpaper.'))
    parser.add_argument(
        '--scenario_id_field', default='Scenario',
        help='name of id field in the scenario polygon')
    parser.add_argument(
        '--parcels_vector_path', help=(
            'Polygons to tile the base raster over with the scenario region.'))
    parser.add_argument(
        '--workspace_dir', default='wallpaper_workspace',
        help='target directory')
    args = parser.parse_args()

    _makedirs(args.workspace_dir)

    scenario_vector_info = pygeoprocessing.get_vector_info(
        args.scenarios_vector_path)

    for raster_path in args.raster_path_list:
        basename = os.path.splitext(os.path.basename(raster_path))[0]
        churn_dir = os.path.join(args.workspace_dir, f'churn')
        _makedirs(churn_dir)

        scenario_vector = gdal.OpenEx(
            args.scenarios_vector_path, gdal.OF_VECTOR)
        scenario_layer = scenario_vector.GetLayer()

        parcel_mask_raster_path = os.path.join(
            churn_dir, f'parcel_mask_{basename}.tif')

        # Create a vector mask
        pygeoprocessing.new_raster_from_base(
            raster_path, parcel_mask_raster_path, gdal.GDT_Byte, [0])
        pygeoprocessing.rasterize(
            args.parcels_vector_path, parcel_mask_raster_path, burn_values=[1])

        for scenario_feature in scenario_layer:
            scenario_array = _extract_intersecting_array_from_raster(
                scenario_feature, scenario_vector_info['projection_wkt'],
                raster_path)
            LOGGER.debug(scenario_array)


if __name__ == '__main__':
    main()

# orkspace = r"E:\NatCap\Golf\Comparison\Data"
# folder = os.path.join(workspace, r"pol\Data_1m")
# parcels = os.path.join(workspace, "golf_courses.shp")
# scenarios = os.path.join(workspace, "scenarios.shp")
# rasters = {'lulc': os.path.join(workspace, "mulc.tif")}
# distance = 1340
# tier = 1
# tm0 = time.time()/60
