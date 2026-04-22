import re

with open('index.qmd', 'r', encoding='utf-8') as f:
    content = f.read()

new_ui_block = r'''### 2. Interactive Visualisation

#### FinTech Styled Dashboard Interface

We completely rebuilt the Earth Engine UI, removing the standard native map controls and replacing them with a custom dual panel layout governed by rigid spacing and modern typography. A left panel offers intelligence summaries and draw analysis, whilst a right panel explicitly lists spatial data layers.

Every layer is equipped with an interactive tooltip translating technical data into plain English, ensuring non technical users can interpret satellite imagery with ease.

::: {.scroll-container style="overflow-y: scroll; height: 450px; padding: 20px;"}
```javascript
// ── RIGHT PANEL (LAYERS & ANALYTICS) ─────────────────────

// Remove native layer control entirely for a cleaner UI
Map.setControlVisibility({ layerList: false, zoomControl: true, scaleControl: true });

var rightPanel = ui.Panel({
  style: {width: '360px', backgroundColor: '#ffffff', padding: '24px', position: 'top-right', border: '1px solid #dadce0'}
});

rightPanel.add(ui.Label('Data & Analytics', {fontWeight: 'bold', fontSize: '18px', margin: '0 0 16px 0', color: '#202124', fontFamily: 'Arial, sans-serif'}));

// Iterate through layers dynamically creating toggle switches and setting sliders
var mapLayersArray = Map.layers();
var numLayers = mapLayersArray.length();

var buildLayerRow = function(index) {
  var layerObj = mapLayersArray.get(index);
  var name = layerObj.getName();
  var infoText = layerDefinitions[name];
  
  if (!infoText) return; 
  
  var isHero = name === 'Combined Heat Vulnerability (Score 0-1)';
  layerObj.setShown(isHero);

  var checkbox = ui.Checkbox({
    label: name,
    value: isHero,
    style: {fontWeight: 'bold', color: '#3c4043', fontSize: '13px', margin: '4px 0 2px 0'}
  });
  
  checkbox.onChange(function(checked) { layerObj.setShown(checked); });
  
  var infoBlock = ui.Label(infoText, {fontSize: '12px', color: '#5f6368', margin: '0 0 4px 24px', shown: false});
  var opacityLabel = ui.Label('Opacity Override:', {fontSize: '11px', color: '#80868b', margin: '0 0 0 24px', shown: false});
  var opacitySlider = ui.Slider({min: 0, max: 1, value: 1, step: 0.1, style: {margin: '0 0 12px 24px', stretch: 'horizontal', shown: false}});
  opacitySlider.onChange(function(val) { layerObj.setOpacity(val); });

  var toggleBtn = ui.Button({label: '⚙️ Settings & Info', style: {margin: '0 0 8px 18px', padding: '0', color: '#1a73e8'}});
  
  toggleBtn.onClick(function() { 
    var state = !infoBlock.style().get('shown');
    infoBlock.style().set('shown', state);
    opacityLabel.style().set('shown', state);
    opacitySlider.style().set('shown', state);
  });
  
  var row = ui.Panel({
    widgets: [checkbox, toggleBtn, infoBlock, opacityLabel, opacitySlider],
    layout: ui.Panel.Layout.Flow('vertical'),
    style: {margin: '0 0 8px 0', padding: '0 0 4px 0'}
  });
  
  rightPanel.add(row);
};

for (var i = numLayers - 1; i >= 0; i--) { buildLayerRow(i); }
ui.root.insert(2, rightPanel);
```
:::

#### Immediate Borough Statistics Loading

When a borough is selected, a pie chart and mean vulnerability overview is constructed. By pulling from the precomputed statistics asset rather than calling heavy reducers dynamically, the UI refreshes instantly.

::: {.scroll-container style="overflow-y: scroll; height: 360px; padding: 20px;"}
```javascript
function updateBoroughPanel(boroughName, infoPanel) {
  var borough = londonBoroughs.filter(ee.Filter.eq('NAME', boroughName));
  var geom    = borough.geometry();

  // Zoom the map to the borough
  Map.centerObject(borough, 11);

  // Get stats from the pre-aggregated collection
  var boroughFeat = boroughStats.filter(ee.Filter.eq('NAME', boroughName)).first();

  boroughFeat.evaluate(function(feat) {
    if (!feat) return;
    var props = feat.properties;

    // Clear the info panel and rebuild with modern fintech styling
    infoPanel.clear();
    infoPanel.add(ui.Label(boroughName, {fontWeight: 'bold', fontSize: '18px', color: '#1a73e8', margin: '0 0 12px 0'}));
    
    var heatScore = (props.meanHeatVuln * 100).toFixed(1);
    var coldScore = (props.meanColdVuln * 100).toFixed(1);

    infoPanel.add(ui.Label('Average Heat Vulnerability: ' + heatScore, {fontSize: '14px', fontWeight: 'bold', color: '#c0392b', margin: '0 0 4px 0'}));
    infoPanel.add(ui.Label('Average Cold Vulnerability: ' + coldScore, {fontSize: '14px', fontWeight: 'bold', color: '#08306b', margin: '0 0 12px 0'}));
```
:::'''

start_idx = content.find('### 2. Interactive Visualisation')
end_idx = content.find('### 3. Insights and Objectives')

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_ui_block + '\n\n' + content[end_idx:]
    with open('index.qmd', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Success")
else:
    print("Failed to find boundaries")
