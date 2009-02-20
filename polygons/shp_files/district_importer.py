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
