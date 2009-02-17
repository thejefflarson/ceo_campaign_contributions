#! /usr/bin/python
from django.core.management import setup_environ
from beckett import settings 
setup_environ(settings)
import django, glob
from beckett.finance.models import Zip
from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.models import GeometryColumns, SpatialRefSys
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.utils.layermapping import LayerMapping


files = glob.glob("*.shp")
print files
for file in files:
    ds = DataSource(file)
    print ds.layer_count
    layer = ds[0]
    print layer.fields
    print layer.extent.wkt
    print layer.geom_type
    #print layer.get_fields('ZCTA')
    srs = SpatialReference('NAD83')
    mapping = {'code' : 'ZCTA',
            'poly' : 'POLYGON',
            }
    try:
        lm = LayerMapping(Zip, ds, mapping, source_srs=srs)
        lm.save(verbose=True)
    except:
        print "dups"
