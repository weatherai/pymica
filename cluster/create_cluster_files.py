'''
Generates the cluster rasters from the geometries.
The generated file can be used to calculate the multiregressions
using clusters.
'''
from osgeo import ogr, osr, gdal
import numpy
from scipy.ndimage import gaussian_filter


def create_reprojected_geoms(file_name, epsg):
    '''Reprojects an ogr file to the desired projection
    Taken from:
    https://pcjericks.github.io/py-gdalogr-cookbook/projection.html#reproject-a-layer

    Args:
        file_name (str): The file to reproject path
        epsg (int): The new projection EPSG code

    Returns:
        osgeo.ogr.DataSource: The reprojected ogr datasource object
    '''
    out_proj = osr.SpatialReference()
    out_proj.ImportFromEPSG(epsg)
    if len(out_proj.ExportToPrettyWkt()) <= 1:
        raise ValueError("Wrong EPSG code: {}".format(epsg))

    in_proj = osr.SpatialReference()
    in_proj.ImportFromEPSG(4326)

    transf = osr.CoordinateTransformation(in_proj, out_proj)

    in_ds = ogr.Open(file_name)
    if in_ds is None:
        raise IOError("File {} doesn't exist".format(file_name))
    in_layer = in_ds.GetLayer()

    mem_driver = ogr.GetDriverByName('MEMORY')
    proj_ds = mem_driver.CreateDataSource('memData')
    proj_layer = proj_ds.CreateLayer("clusters", out_proj,
                                     geom_type=ogr.wkbMultiPolygon)

    in_layer_def = in_layer.GetLayerDefn()
    for i in range(0, in_layer_def.GetFieldCount()):
        field_def = in_layer_def.GetFieldDefn(i)
        proj_layer.CreateField(field_def)

    out_layer_def = proj_layer.GetLayerDefn()

    feature = in_layer.GetNextFeature()
    while feature:
        geom = feature.GetGeometryRef()
        geom.Transform(transf)
        proj_feat = ogr.Feature(out_layer_def)
        proj_feat.SetGeometry(geom)
        for i in range(0, out_layer_def.GetFieldCount()):
            proj_feat.SetField(out_layer_def.GetFieldDefn(i).GetNameRef(),
                               feature.GetField(i))
        proj_layer.CreateFeature(proj_feat)
        proj_feat = None
        feature = in_layer.GetNextFeature()

    return proj_ds


def rasterize_clusters(ds_in, out_conf, sigma=15):
    """Takes the clusters file the GeoJSON generated by the web interface
    and rasterizes and blurs them so they can be used in the pymica functions.
    The output projection is the same as the input layers

    Args:
        ds_in (str): The input GeoJSON file path
        out_conf (dict): The output properties. Must include the keys:
                         out_file: The output file
                         size: The output image file (x,y)
                         geotransform: The output file geotransform
    """
    if not all(k in out_conf for k in ("out_file", "size", "geotransform")):
        raise ValueError("The out_conf parameter doesn't have all" +
                         "the needed elements")

    layer = ds_in.GetLayer()
    num_layers = layer.GetFeatureCount()
    proj = layer.GetSpatialRef()

    driver = gdal.GetDriverByName('GTIFF')
    ds_out = driver.Create(out_conf['out_file'], out_conf['size'][0],
                           out_conf['size'][1],
                           num_layers, gdal.GDT_Float32)
    ds_out.SetGeoTransform(out_conf['geotransform'])
    ds_out.SetProjection(proj.ExportToWkt())

    for i in range(num_layers):
        layer.SetAttributeFilter('cluster={}'.format(i))
        gdal.RasterizeLayer(ds_out, [i + 1], layer, burn_values=[1])

    data = ds_out.ReadAsArray().astype(numpy.float32)
    for i in range(num_layers):
        blurred = gaussian_filter(data[i], sigma)
        ds_out.GetRasterBand(i + 1).WriteArray(blurred)

    ds_out = None
