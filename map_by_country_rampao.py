# Map seagrass beds, coral reefs, mangroves and protected areas in specific 
# region and export statistics
from qgis.core import *

#### for standdalone script
## supply path to qgis install location
#QgsApplication.setPrefixPath("/path/to/qgis/installation", True)
#
## create a reference to the QgsApplication, setting the
## second argument to False disables the GUI
#qgs = QgsApplication([], False)
#
## load providers
#qgs.initQgis()
####

import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os

region = 'RAMPAO'
countries = ['CPV', 'GIN', 'GMB', 'GNB', 'MRT', 'SEN', 'SLE']

# set current directory
os.chdir("E:/weyname/BIOPAMA/GIS/Marine")
# create region folder
if not os.path.isdir("./" + region):
    os.makedirs("./" + region)

# Get the project instance
project = QgsProject.instance() 
project.write("./" + region + "/" + region + '.qgs')
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

# load region layer
regionLayer = QgsVectorLayer("//ies-ud01/spatial_datasets/Derived_Datasets/DOPA_PROCESSING_2018/dopa.gpkg|layerid=1", 
    "countries", "ogr")
if not regionLayer.isValid():
  print("Layer failed to load!")

# Select region from DOPA 3 processing
regionLayer.selectByExpression(" OR ".join(['"iso3" LIKE\'%{:s}%\''.format(i) for i in countries]), QgsVectorLayer.SetSelection)
# save selection to file
error = QgsVectorFileWriter.writeAsVectorFormat(
    tmp,       # layer: QgsVectorLayer
    "./" + region + "/" + region,         # fileName: str
    "utf-8",         # fileEncoding: str
    QgsCoordinateReferenceSystem("EPSG:4326"),            # destCRS: QgsCoordinateReferenceSystem()
    "GeoJSON",       # driverName: str
    True             # onlySeleted: bool
    )
if error[0] != QgsVectorFileWriter.NoError:
    print("File not written!")

# remove layer
QgsProject.instance().removeMapLayer(regionLayer)
regionLayer = iface.addVectorLayer("./" + region + "/" + region+".geojson", 
    "region", "ogr")
if not regionLayer:
  print("region layer failed to load!")
    
# load PA
wdpa = QgsVectorLayer("./lucy_rampao_results/shapefiles/wdpa_Jul_2018.shp", "pa", "ogr")#"E:/weyname/BIOPAMA/GIS/data/Original/WDPA/WDPA_Feb2019_Public.gdb|layerid=0")
if not wdpa.isValid():
  print("PA layer failed to load!")

# # select region
# wdpa.selectByExpression('"ISO3" IN \'' + countries + '\'', QgsVectorLayer.SetSelection)
# # dissolve selection but keep fields: ISO3, MARINE
# processing.run('qgis:dissolve', {
    # 'INPUT': QgsProcessingFeatureSourceDefinition(wdpa,True),
    # 'FIELD': ['ISO3', 'MARINE'], 
    # 'OUTPUT': "./" + region + "/wdpa_" + region + "_54009.geojson"
    # })
# # problem when overlapping polygons. Solution: subtract Coastal and Marine from Terrestrial; Marine from Coastal
# processing.run('qgis:difference', {
    # 'INPUT' : QgsProcessingFeatureSourceDefinition(iface.activeLayer().selectByExpression('"MARINE" = 0'), True),
    # 'OVERLAY' : QgsProcessingFeatureSourceDefinition(iface.activeLayer().selectByExpression('"MARINE" != 0'), True),
    # 'OUTPUT' : 'memory'
    # })
# dissolve polygons by ISO3
tmp = processing.run('qgis:dissolve', {
    'INPUT': wdpa,
    'FIELD': 'iso3', 
    'OUTPUT': "./" + region + "/wdpa_" + region + "_dissolved.geojson"
    })
# remove wdpa layer
QgsProject.instance().removeMapLayer(wdpa)
# save to file and reproject in Mollweide
error = QgsVectorFileWriter.writeAsVectorFormat(
    QgsVectorLayer(tmp['OUTPUT'], "pa","ogr"),       # layer: QgsVectorLayer
    "./" + region + "/wdpa_" + region + "_dissolved_54009",         # fileName: str
    "utf-8",         # fileEncoding: str
    QgsCoordinateReferenceSystem("EPSG:54009"),            # destCRS: QgsCoordinateReferenceSystem()
    "GeoJSON",       # driverName: str
    False             # onlySelected: bool
    )

if error[0] == QgsVectorFileWriter.NoError:
    print("success!")

regionPaLayer = iface.addVectorLayer('./' + region + '/wdpa_' + region + "_dissolved_54009.geojson", 
    "pa", "ogr")

if not regionPaLayer:
  print("Layer failed to load!")

#"MARINE" > 0 (0 terrestrial, 1: coastal, 2: marine)

# download data or set path to data

d = {
    'seagrass': "E:/weyname/BIOPAMA/GIS/data/Original/wcmc_marine/014_001_WCMC013-014_SeagrassPtPy2018_v6/01_Data/WCMC_013_014_SeagrassesPy_v6.shp",
    'coral': "E:/weyname/BIOPAMA/GIS/data/Original/wcmc_marine/14_001_WCMC008_CoralReefs2010_v4/01_Data/WCMC008_CoralReef2010_Py_v4.shp",
    'mangrove': "E:/weyname/BIOPAMA/GIS/data/Original/wcmc_marine/GMW_001_GlobalMangroveWatch/01_Data/GMW_2010_v2.shp",
    'modSeagrass': "E:/weyname/BIOPAMA/GIS/Marine/MaxentModeledSeagrassExtent_4326.shp"
    }
#name = 'coral'
#filename = d[name]
#project.setCrs(QgsCoordinateReferenceSystem("EPSG:54009"))
def paStats(name):
  # load layer
  layer = QgsVectorLayer(d[name])
  if not layer.isValid():
    print("Layer failed to load!")
  # check that crs = regionLayer
  if layer.crs() != regionLayer.crs():
      # abort
      print("Incompatible CRS")
      return(print("Incompatible CRS"))      
  # intersect with region
  field = {'seagrass' : "LAYER_NAME",
            'coral' : "LAYER_NAME",
            'mangrove' : "pxlval",
            'modSeagrass' : "gridcode"}
  tmp = processing.run("qgis:intersection",{
          'INPUT': layer,
          'OVERLAY': regionLayer,
          'INPUT_FIELDS': field[name],
          'OVERLAY_FIELDS':'iso3',
          'OUTPUT': './' + region + '/' + name + 'I_' + region + '.geojson'
          })
  QgsProject.instance().removeMapLayer(layer)
  layer = iface.addVectorLayer(tmp['OUTPUT'], name, 'ogr')
  # reproject to Mollweide
  error = QgsVectorFileWriter.writeAsVectorFormat(
      layer,       # layer: QgsVectorLayer
      './' + region + '/' + name + 'I_' + region + '_54009',         # fileName: str
      "utf-8",         # fileEncoding: str
      QgsCoordinateReferenceSystem("EPSG:54009"),            # destCRS: QgsCoordinateReferenceSystem()
      "GeoJSON")       # driverName: str
  if error == QgsVectorFileWriter.NoError:
      print("success!")
  QgsProject.instance().removeMapLayer(layer)
  layer = iface.addVectorLayer('./' + region + '/' + name + 'I_' + region + '_54009.geojson', name, 'ogr')
  # check CRS
  print(name + " CRS : " +layer.crs().description())
  # zonal stat: IN/OUT PA
  # union
  tmp = processing.run("qgis:union", {
          'INPUT': layer,
          'OVERLAY': regionPaLayer,
          'OUTPUT': './' + region + '/' + name + "P_" + region + ".geojson"
          })
  QgsProject.instance().removeMapLayer(layer)
  layer = iface.addVectorLayer('./' + region + '/' + name + "P_" + region + ".geojson", name, 'ogr')
#  fields = []
#  for field in layer.fields():
#      fields = fields + [field.name()]
#  # compute area of polygons
  from qgis.PyQt.QtCore import QVariant
  caps = layer.dataProvider().capabilities()
  if caps & QgsVectorDataProvider.AddAttributes:
      res = layer.dataProvider().addAttributes(
          [QgsField("AreaUnion", QVariant.Double)])
  layer.updateFields()
  # get geometry  area
  with edit(layer):
      for feat in layer.getFeatures():
          feat[layer.fields().indexFromName("AreaUnion")] = feat.geometry().area()
          # set PA_DEF to '0' for unprotected features
          if feat[layer.fields().indexFromName("PA_DEF".lower())] == NULL:
              feat[layer.fields().indexFromName("PA_DEF".lower())] = '0'
          layer.updateFeature(feat)
  layer.updateFields()
  tmp = QgsFeatureRequest(QgsExpression
  ('("LAYER_NAME" IS NOT NULL) OR ("pxlval" IS NOT NULL) OR ("gridcode" IS NOT NULL)' )).setFlags(QgsFeatureRequest.NoGeometry)
#  for feat in layer.getFeatures(tmp):
#      print(feat.attributes())
#  # !!!! Potential double counting if orverlapping polygons !!!!!
  # sort that out:
  # export tmp to layer
  # flatten
  # !!!!!!!!!!!!!!!!!!!!
  # compute statistics
  features = layer.getFeatures(tmp)
  pa = layer.fields().indexFromName("PA_DEF".lower())
  area = layer.fields().indexFromName("AreaUnion")
  iso3 = layer.fields().indexFromName("iso3") # from layer
  iso3_pa = layer.fields().indexFromName("ISO3_2".lower())
  values = {}
  for feat in features:
      attrs = feat.attributes()
      try: 
          cat1 = unicode(attrs[iso3])
          cat2 = unicode(attrs[iso3_pa])
          cat3 = unicode(attrs[pa])
          cat = cat1 + ',' + cat2 + ',' + cat3
          value = float(attrs[area])*1e-6
          if cat not in values:
              values[cat] = []
          values[cat].append(value)
      except:
          pass
  stat = QgsStatisticalSummary(QgsStatisticalSummary.Sum | QgsStatisticalSummary.Count)
  results = dict()
  for (cat, v) in values.items():
      stat.calculate(v)
      results[cat] = tuple(cat.rsplit(',') + [stat.sum()])
  ### !!!!!!!!!!!!!!!!!!!!!
  tmp = np.fromiter(
                results.values(),
                dtype = np.dtype([('iso3', '<U10'),('iso3_pa', 'U10'),('pa', 'U10'), ('AreaSqkm', '<f8')]),
                count = len(results)
                )
  np.savetxt(fname = "./" + region + "/" + name + "_" + region + ".csv",
            X = tmp ,
            fmt = ['%s','%s','%s','%20.2f'],
            delimiter=",",
            header = ",".join(["{:s}".format(i) for i in tmp.dtype.names]),
            comments = '')
  # remove layer
  QgsProject.instance().removeMapLayer(layer)
  return results
#### end of function


seagrassRes = paStats('seagrass')
coralRes = paStats('coral')
mangroveRes = paStats('mangrove')
mseagrassRes = paStats('modSeagrass')

# map
# remove region and PA layers
QgsProject.instance().removeMapLayer(regionLayer)
QgsProject.instance().removeMapLayer(regionPaLayer)

## Background: mapbox
#uri = "crs=EPSG:3857&format&type=xyz&url=https://api.mapbox.com/styles/v1/mboni/cj978emxv180k2rmtgsz6i1b4/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWJvbmkiLCJhIjoiY2lzOHNzcWJtMDA0ODJ6czQ2eXQxOXNqeCJ9.geDRSQxeQQQkKDN9bZWeuw"
#mapboxLayer = QgsRasterLayer(uri, "mapbox", 'wms')
#if not mapboxLayer.isValid():
#    print("Mapbox failed to load!")
#mapbox = project.addMapLayer(mapboxLayer)

# Background: Esri light
#uri = "url=http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0&type=xyz"
#mts_layer=QgsRasterLayer(uri,'Background: ESRI World Light Gray','wms')
#if not mts_layer.isValid():
#    print ("Layer failed to load!")

uri = "url=http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&type=xyz"
mts_layer=QgsRasterLayer(uri,'Background: CartoDb Positron','wms')

esri = project.addMapLayer(mts_layer)

colours = {
    'seagrass': '#36aa49',
    'coral': '#e65025',
    'mangrove': '#720f11',
    'modSeagrass': '#36aa49'
    }
layers = dict()
extent = NULL
for name in colours.keys():
    try:
        layer = iface.addVectorLayer('./' + region + '/' + name + 'I_' + region + '.geojson', name, 'ogr')
        layers[name] = layer
        layer.setName(name + " distribution")
        renderer = layer.renderer() #singleSymbol renderer
        symLayer = QgsSimpleFillSymbolLayer.create({'color':colours[name], 'outline_style': 'no'})
        renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        # get extent and combine
        if extent.isNull():
            extent = layer.extent()
        else:
            extent.combineExtentWith(layer.extent())
    except:
        pass

# show PA
regionPaLayer = iface.addVectorLayer("./lucy_rampao_results/shapefiles/wdpa_Jul_2018.shp", "pa", "ogr")#iface.addVectorLayer('./' + region + '/wdpa_' + region + "_54009.geojson", "PA", "ogr")
regionPaLayer.setName("Protected areas (WDPA Jul 2018/JRC)")
renderer = regionPaLayer.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'255,255,255,100', 'outline_color': '#70b6d1'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
regionPaLayer.setRenderer(renderer)
regionPaLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(regionPaLayer.id())

# region layer
regionLayer = iface.addVectorLayer('./' + region + '/' + region + ".geojson", 
    "region", "ogr")
renderer = regionLayer.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'250,250,250,10', 'outline_color': '#91af90'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
regionLayer.setRenderer(renderer)
regionLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(regionLayer.id())

# Set canvas extent
canvas = iface.mapCanvas()
# zoom to coral, mangrove and seeagrass combined extent
# set CRS to WGS84
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
# zoom to extent
canvas.setExtent(extent.buffered(0.08))
# set CRS to native Mapbox (pseudo Mecator)
project.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))


# print layout
# get a reference to the layout manager
manager = project.layoutManager()
#make a new print layout object
layout = QgsPrintLayout(project)
#needs to call this according to API documentaiton
layout.initializeDefaults()
#cosmetic
layout.setName('map_coral_seagrass_mangrove_pa')
#add layout to manager
manager.addLayout(layout)

#create a map item to add
itemMap = QgsLayoutItemMap.create(layout)
# lock layers
itemMap.setLayers([regionPaLayer, layers['mangrove'], layers['coral'], layers['seagrass'], regionLayer, esri])
itemMap.setKeepLayerSet(True)

# add to layout
layout.addLayoutItem(itemMap)
# set size
itemMap.attemptResize(QgsLayoutSize(257, 170, QgsUnitTypes.LayoutMillimeters))
itemMap.attemptMove(QgsLayoutPoint(20,15,QgsUnitTypes.LayoutMillimeters))
itemMap.setExtent(canvas.extent())

# add grid linked to map
itemMap.grid().setName("graticule")
itemMap.grid().setEnabled(True)
itemMap.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap.grid().setIntervalX(2)
itemMap.grid().setIntervalY(2)
itemMap.grid().setAnnotationEnabled(True)
itemMap.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap.grid().setFramePenSize(0.5)
itemMap.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?

# Legend
itemLegend = QgsLayoutItemLegend.create(layout)
itemLegend.setAutoUpdateModel(False)
itemLegend.setLinkedMap(itemMap)
itemLegend.setLegendFilterByMapEnabled(True)
itemLegend.setTitle(region)
itemLegend.setResizeToContents(False)
itemLegend.attemptResize(QgsLayoutSize(85, 45, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLegend)
itemLegend.attemptMove(QgsLayoutPoint(205,10,QgsUnitTypes.LayoutMillimeters))

# text box
itemLabel = QgsLayoutItemLabel.create(layout)
itemLabel.setText("Coordinate Reference System: [% @project_crs %] \nData sources: \nhttp://data.unep-wcmc.org/datasets/ \nhttps://www.protectedplanet.net/")
#itemLabel.adjustSizeToText()
itemLabel.setFixedSize(QgsLayoutSize(100,25,QgsUnitTypes.LayoutMillimeters))
itemLabel.attemptMove(QgsLayoutPoint(15,185,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabel)

# North arrow
itemNorth = QgsLayoutItemPicture.create(layout)
itemNorth.setPicturePath("C:/PROGRA~1/QGIS3~1.2/apps/qgis/svg/arrows/NorthArrow_04.svg")
itemNorth.setFixedSize(QgsLayoutSize(10,10,QgsUnitTypes.LayoutMillimeters))
itemNorth.attemptMove(QgsLayoutPoint(25,160,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemNorth)

# BIOPAMA logo
itemLogo = QgsLayoutItemPicture.create(layout)
itemLogo.setPicturePath("../../DOC/pen_biopama_logo_1.png")
layout.addLayoutItem(itemLogo)
itemLogo.setFixedSize(QgsLayoutSize(50,10,QgsUnitTypes.LayoutMillimeters))
itemLogo.attemptMove(QgsLayoutPoint(230,190,QgsUnitTypes.LayoutMillimeters))


# print to png
export = QgsLayoutExporter(layout)
export.exportToImage("./" + region + "/" + layout.name() + "_" + region + ".png", QgsLayoutExporter.ImageExportSettings())

#'modSeagrass': '#36aa49'
# add modSeagrass to map
layers['modSeagrass'].setName("Modelled seagrass suitability")

# new print layout
layout1 = manager.duplicateLayout(layout, 'map_modelled_seagrass_pa')
# get mapItem and edit italic
# mapItem type = 65639
for item in layout1.items():
    # Map
    if item.type() == 65639:
        item.setKeepLayerSet(False)
        item.setLayers([regionLayer, regionPaLayer, layers['modSeagrass'], esri])
        item.setKeepLayerSet(True)
        item.refresh()
    # Legend    
    if item.type() == 65642:
        item.attemptResize(QgsLayoutSize(85, 45, QgsUnitTypes.LayoutMillimeters))

# Export print layout
export = QgsLayoutExporter(layout1)
export.exportToImage("./" + region + "/" + layout1.name() + "_" + region + ".png", export.ImageExportSettings())

# 
layout2 = manager.duplicateLayout(layout, 'map_pa')
for item in layout2.items():
    # Map
    if item.type() == 65639:
        item.setKeepLayerSet(False)
        item.setLayers([regionPaLayer, regionLayer, esri])
        item.setKeepLayerSet(True)
        item.refresh()
    # Legend    
    if item.type() == 65642:
        item.attemptResize(QgsLayoutSize(85, 35, QgsUnitTypes.LayoutMillimeters))

# Export print layout
export = QgsLayoutExporter(layout2)
export.exportToImage("./" + region + "/" + layout2.name() + "_" + region + ".png", export.ImageExportSettings())


# save project
project.write("./" + region + "/" + region + '.qgs')

#### for standalone script
## When your script is complete, call exitQgis() to remove the
## provider and layer registries from memory
#qgs.exitQgis()
####
