## load providers
# qgs.initQgis()
####

import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os

region = 'RAMPAO'
countries = ['BEN', 'CIV', 'CPV', 'GIN', 'GMB', 'GNB', 'MRT', 'SEN', 'SLE', 'TGO', 'LBR', 'GHA', 'NGA']
country_names = {
    'BEN': "Bénin",
    'CIV': "Côte d'Ivoire",
    'CPV': "Cap Vert",
    'GIN': "Guinée",
    'GMB': "Gambie",
    'GNB': "Guinée Bissau",
    'MRT': "Mauritanie",
    'SEN': "Sénégal",
    'SLE': "Sierra Leone",
    'TGO': "Togo",
    'LBR': "Liberia",
    'GHA': "Ghana",
    'NGA': "Nigeria"
    }

# set current directory
os.chdir("/Marine")
# create region folder
if not os.path.isdir("./" + region):
    os.makedirs("./" + region)

# create qgs folder
if not os.path.isdir("./" + region + "/qgs"):
    os.makedirs("./" + region + "/qgs")

# create tmp folder
if not os.path.isdir("./" + region + "/tmp"):
    os.makedirs("./" + region + "/tmp")


# Get the project instance
project = QgsProject.instance() 
project.write("./" + region + "/" + 'sompa.qgs')
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

# load region layer
regionLayer = iface.addVectorLayer("dbname='d6biopamarest' host=pgsql96-srv1.jrc.org port=5432 authcfg=xky3xl0 key='country_id' type=MultiPolygon checkPrimaryKeyUnicity='1' table=\"geo\".\"mv_gaul_eez_dissolved\" (geom) sql=", 
    "countries", "postgres")
if not regionLayer.isValid():
  print("Layer failed to load!")

# Select region from DOPA 3 processing
regionLayer.selectByExpression(" OR ".join(['"iso3" LIKE\'%{:s}%\''.format(i) for i in countries]), QgsVectorLayer.SetSelection)
# save selection to file
error = QgsVectorFileWriter.writeAsVectorFormat(
    regionLayer,       # layer: QgsVectorLayer
    "./" + region + "/tmp/sompa_" + region,         # fileName: str
    "utf-8",         # fileEncoding: str
    QgsCoordinateReferenceSystem("EPSG:4326"),            # destCRS: QgsCoordinateReferenceSystem()
    "GeoJSON",       # driverName: str
    True             # onlySeleted: bool
    )
if error[0] != QgsVectorFileWriter.NoError:
    print("File not written!")

# remove layer
QgsProject.instance().removeMapLayer(regionLayer)
regionLayer = iface.addVectorLayer("./" + region + "/tmp/sompa_" + region+".geojson", 
    "region", "ogr")
if not regionLayer:
  print("region layer failed to load!")

# symbology
# countries: no fill for current country; 50% white for others
# wdpa_poly: national: MPA outline blue with 80% fill, Coastal turquoise, Terr green
# international: hashing with same colours as outline of National
# wdpa_points: 

# load PA
# WDPA Feature Server: https://gis.unep-wcmc.org/arcgis/rest/services/wdpa/public/MapServer
wdpa_version = 'May2021'
uri = "crs='EPSG:3857' filter='' url='https://gis.unep-wcmc.org/arcgis/rest/services/wdpa/public/MapServer/1' table="" sql="
wdpa = QgsVectorLayer(uri, "WDPA_poly_"+wdpa_version, "arcgisfeatureserver")
if not wdpa.isValid():
  print("PA layer failed to load!")
# filter APs
wdpa.selectByExpression(" OR ".join(['"ISO3" LIKE\'%{:s}%\''.format(i) for i in countries]), QgsVectorLayer.SetSelection)
tmp = processing.run("native:extractbyexpression",{
    'INPUT': wdpa,
    'EXPRESSION':" OR ".join(['"ISO3" LIKE\'%{:s}%\''.format(i) for i in countries]),
    'OUTPUT':'TEMPORARY_OUTPUT'
    })
wdpa_poly = QgsProject.instance().addMapLayer(tmp['OUTPUT'])
wdpa_poly.name = "WDPA Poly"
wdpa_poly.setName = "Aires protégées (polygones)"
iface.setActiveLayer(wdpa_poly)
exec(open('./marine_pa_legend_py3_fr.py'.encode('utf-8')).read())


wdpa = QgsVectorLayer(uri, "WDPA_point_" + wdpa_version, "arcgisfeatureserver")
if not wdpa.isValid():
  print("PA layer failed to load!")

# filter APs
wdpa.selectByExpression(" OR ".join(['"ISO3" LIKE\'%{:s}%\''.format(i) for i in countries]), QgsVectorLayer.SetSelection)
tmp = processing.run("native:extractbyexpression",{
    'INPUT': wdpa,
    'EXPRESSION':" OR ".join(['"ISO3" LIKE\'%{:s}%\''.format(i) for i in countries]),
    'OUTPUT':'TEMPORARY_OUTPUT'
    })
wdpa_point = QgsProject.instance().addMapLayer(tmp['OUTPUT'])
wdpa_point.name = "WDPA Point"
wdpa_point.setName = "Aires protégées (points)"
iface.setActiveLayer(wdpa_point)
exec(open('./marine_pa_point_legend_py3_fr.py'.encode('utf-8')).read())

# countries
regionLayer.setName("RAMPAO membres et candidats")
renderer = regionLayer.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'255,255,255,100', 'outline_color': '#aaaaaa'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
regionLayer.setRenderer(renderer)
regionLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(regionLayer.id())


# background
uri = "url=http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&type=xyz"
mts_layer=QgsRasterLayer(uri,'Background: CartoDb Positron','wms')
bckgr = project.addMapLayer(mts_layer)

# Set canvas extent
canvas = iface.mapCanvas()

# base print layout
# get a reference to the layout manager
manager = project.layoutManager()
#make a new print layout object
layout = QgsPrintLayout(project)
#needs to call this according to API documentaiton
layout.initializeDefaults()
#cosmetic
layout.setName('map_rampao_pa')
#add layout to manager
manager.addLayout(layout)

#create a map item to add
itemMap = QgsLayoutItemMap.create(layout)
# lock layers
itemMap.setKeepLayerSet(False)
itemMap.setLayers([wdpa_point, wdpa_poly, regionLayer, bckgr])
itemMap.setKeepLayerSet(True)

# add to layout
layout.addLayoutItem(itemMap)
# set size
itemMap.attemptResize(QgsLayoutSize(200, 200, QgsUnitTypes.LayoutMillimeters))
itemMap.attemptMove(QgsLayoutPoint(10,5,QgsUnitTypes.LayoutMillimeters))
itemMap.zoomToExtent(regionLayer.extent())

# add grid linked to map
itemMap.grid().setName("graticule")
itemMap.grid().setEnabled(True)
itemMap.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap.grid().setIntervalX(5)
itemMap.grid().setIntervalY(5)
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
itemLegend.setTitle("Aires protégées des pays _nmembres et candidats _ndu RAMPAO")
itemLegend.setWrapString("_n")
itemLegend.setResizeToContents(False)
layout.addLayoutItem(itemLegend)
itemLegend.attemptResize(QgsLayoutSize(77, 150, QgsUnitTypes.LayoutMillimeters))
itemLegend.attemptMove(QgsLayoutPoint(220,0,QgsUnitTypes.LayoutMillimeters))

# text box
itemLabel = QgsLayoutItemLabel.create(layout)
itemLabel.setText("Système de coordonnées: [% @project_crs %] \n\
Sources des données:\n\
WDPA Jan20 (WCMC) \n\
Combined GAUL EEZ (JRC/DOPA)")
#itemLabel.adjustSizeToText()
itemLabel.setFixedSize(QgsLayoutSize(100,40,QgsUnitTypes.LayoutMillimeters))
itemLabel.attemptMove(QgsLayoutPoint(220,170,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabel)

# North arrow
itemNorth = QgsLayoutItemPicture.create(layout)
itemNorth.setPicturePath("C:/PROGRA~1/QGIS3~1.2/apps/qgis/svg/arrows/NorthArrow_04.svg")
itemNorth.setFixedSize(QgsLayoutSize(10,10,QgsUnitTypes.LayoutMillimeters))
itemNorth.attemptMove(QgsLayoutPoint(200,190,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemNorth)

# BIOPAMA logo
itemLogo = QgsLayoutItemPicture.create(layout)
itemLogo.setPicturePath("E:/weyname/BIOPAMA/DOC/pen_biopama_logo_1.png")
layout.addLayoutItem(itemLogo)
itemLogo.setFixedSize(QgsLayoutSize(50,10,QgsUnitTypes.LayoutMillimeters))
itemLogo.attemptMove(QgsLayoutPoint(220,190,QgsUnitTypes.LayoutMillimeters))
# contact text box
itemContact = QgsLayoutItemLabel.create(layout)
itemContact.setText("Contact: melanie.weynants@ec.europa.eu")
#itemContact.adjustSizeToText()
itemContact.setFixedSize(QgsLayoutSize(100,10,QgsUnitTypes.LayoutMillimeters))
itemContact.attemptMove(QgsLayoutPoint(220,200,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemContact)

# export general map
# print to png
export = QgsLayoutExporter(layout)
expSett = QgsLayoutExporter.ImageExportSettings()
expSett.dpi = 150
export.exportToImage("./RAMPAO/sompa_maps/"  + layout.name() + ".png", expSett)


# loop on countries and export maps
layouts = {}
for iso3 in countries:
    extent = NULL
    # zoom to KLC
    regionLayer.selectByExpression('"iso3" LIKE \''+iso3+'\'', QgsVectorLayer.SetSelection)    
    extent = regionLayer.boundingBoxOfSelected()
    regionLayer.removeSelection()
    # canvas.setExtent(extent.buffered(0.08))
    # show only PAs from iso3
    try:
        wdpa_poly.setSubsetString('"ISO3" = \'' + iso3 + '\'')
        wdpa_point.setSubsetString('"ISO3" = \'' + iso3 + '\'')
    except:
        print("error in " + iso3)
    # create print layout
    layouts[iso3] = manager.duplicateLayout(layout, 'rampao_ap_'+iso3)    
    for item in layouts[iso3].items():
        # Map
        if item.type() == 65639:
            # zoom to extent
            item.zoomToExtent(extent.buffered(0.08))
            # refresh
            item.refresh()
            # update grid
            item.grid().setIntervalX(1)
            item.grid().setIntervalY(1)
        # Legend
        if item.type() == 65642:
            item.setTitle("Aires protégées - " + country_names[iso3])
            item.setAutoUpdateModel(True)
    # print to png
    export = QgsLayoutExporter(layouts[iso3])
    expSett = QgsLayoutExporter.ImageExportSettings()
    expSett.dpi = 150
    export.exportToImage("./RAMPAO/sompa_maps/map_pa_"  + iso3 + ".png", expSett)

