# try to convert to python 3
layer = iface.activeLayer()
# create a new rule-based renderer
symbol = QgsSymbol.defaultSymbol(layer.geometryType())
renderer = QgsRuleBasedRenderer(symbol)
root_rule = renderer.rootRule()

def rule_based_style(layer, renderer, label, expression, colour, colour1 = ''):
    if (colour1 == ''):
         colour1 = colour
    
    rule = root_rule.children()[0].clone()
    rule.setLabel(label)
    rule.setFilterExpression(expression)    
    rule.symbol().symbolLayer(0).setStrokeColor(QColor(colour1))
    rule.symbol().symbolLayer(0).setColor(QColor(int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7],16), 192))
    root_rule.appendChild(rule)
    
# simpleFill
simpleFillLayer = QgsSimpleMarkerSymbolLayer.create({'outline_width':'0.5', 'color_alpha':'0.75'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0, simpleFillLayer)
rule_based_style(layer, renderer, 'Terrestrial', '\"MARINE\" = 0 AND "STATUS" = \'Designated\' AND "DESIG_TYPE" = \'National\' ', '#90c04e')
rule_based_style(layer, renderer, 'Coastal', '\"MARINE\" = 2 AND "STATUS" = \'Designated\' AND "DESIG_TYPE" = \'National\' ', '#679b95')
rule_based_style(layer, renderer, 'Marine', '\"MARINE\" = 1 AND "STATUS" = \'Designated\' AND "DESIG_TYPE" = \'National\' ', '#70b6d1')

rule_based_style(layer, renderer, 'International designation - Terrestrial', ' "DESIG_TYPE" = \'International\' AND \"MARINE\" = 0 ', '#90c04e', '#cc775d')
rule_based_style(layer, renderer, 'International designation - Coastal', ' "DESIG_TYPE" = \'International\' AND \"MARINE\" = 2 ', '#679b95', '#cc775d')
rule_based_style(layer, renderer, 'International designation - Coastal', ' "DESIG_TYPE" = \'International\' AND \"MARINE\" = 1 ', '#70b6d1', '#cc775d')

rule_based_style(layer, renderer, 'Proposed - Terrestrial', ' \"MARINE\" = 0 AND "STATUS" = \'Proposed\' ', '#90c04e', '#787878')
rule_based_style(layer, renderer, 'Proposed - Coastal', ' \"MARINE\" = 2 AND "STATUS" = \'Proposed\' ', '#90c04e', '#787878')
rule_based_style(layer, renderer, 'Proposed - Coastal', ' \"MARINE\" = 1 AND "STATUS" = \'Proposed\' ', '#90c04e', '#787878')


# QgsSvgMarkerSymbolLayer    
# C:/PROGRA~1/QGIS3~1.2/apps/qgis/./svg//symbol/landuse_swamp.svg
# C:/PROGRA~1/QGIS3~1.2/apps/qgis/./svg//gpsicons/fish.svg
# C:/PROGRA~1/QGIS3~1.2/apps/qgis/./svg//symbol/landuse_deciduous.svg

# C:/PROGRA~1/QGIS3~1.2/apps/qgis/./svg//gpsicons/deer.svg


# delete the default rule
root_rule.removeChildAt(0)
# render and refresh
layer.setRenderer(renderer)
layer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(layer.id())

## refine rules using categories
#
#fn = 'WDPAID'
#for rule in root_rule.children():
#    categs = []
#    # index of field fn in layer
#    idx = layer.dataProvider().fieldNameIndex(fn)
#    # find unique values
#    vals = set()
#    expression = rule.filterExpression()
#    for feature in layer.dataProvider().getFeatures(QgsFeatureRequest().setFilterExpression(expression)):
#        a = feature.attributes()[idx]
#        vals.add(a)
#    
#    for val in list(vals):
#        # create renderer object
#        categ = QgsRendererCategory(val, QgsFillSymbol().createSimple(
#        {'color':'#FFFFFFFF',
#        'style':'no',
#        'outline_color':'#FFFFFFFF', 
#        'outline_style':'no'}
#        ), str(val))
#        # entry for the list of category items
#        categs.append(categ)
#    
#    # create rendered object
#    q = QgsCategorizedSymbolRenderer(fn, categs)
#    p = renderer.refineRuleCategories(rule, q)
#    
## delete rule if it has no children
#n = len(root_rule.children())
#i=0
#while i<n:
#    subrule = root_rule.children()[i].children()
#    if len(subrule) < 1:
#        root_rule.removeChildAt(i)
#        n = len(root_rule.children())
#    else:
#        i = i+1 
#
## render and refresh
#layer.setRenderer(renderer)
#layer.triggerRepaint()
#iface.layerTreeView().refreshLayerSymbology(layer.id())
#
## change labels
#children = renderer.rootRule().children()
fieldName1 = "WDPAID"
fieldName2 = "NAME"
#
#for child in children: # Iterate through groups
#    if child.filter():
#        feat = next(layer.getFeatures(QgsFeatureRequest(child.filter())), None)
#        if feat:
#            for subChild in child.children(): # Iterate through subgroups
#                if subChild.filter():
#                    feat = next(layer.getFeatures(QgsFeatureRequest(subChild.filter())), None)
#                    if feat:
#                        subChild.setLabel( '{:g}'.format(feat.attribute(fieldName1)) + ": " + feat.attribute(fieldName2) )
#iface.layerTreeView().refreshLayerSymbology(layer.id())
#
## rule based feature labelling
#layer.setCustomProperty("labeling/fieldName", fieldName2)
#layer.setCustomProperty("labeling/placement", QgsPalLayerSettings.Horizontal)
#layer.setCustomProperty("labeling/predefinedPointPosition", QgsPalLayerSettings.BottomRight)
#layer.setCustomProperty("labeling/fontSize","7" )
#layer.setCustomProperty("labeling/bufferDraw", True)
#layer.setCustomProperty("labeling/enabled", True )
#layer.triggerRepaint()
## 