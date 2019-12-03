// Initialize the platform object:
var platform = new H.service.Platform({
    'apikey': 'PBIwVuBS9MMg2YgdurJi1XKqVMD3cMxv3j5vTxZga5E',
});


// info about lng and lat
console.log(lng);
console.log(lat);

// Obtain the default map types from the platform object
var maptypes = platform.createDefaultLayers();

// Instantiate (and display) a map object:
var map = new H.Map(
    document.getElementById('mapContainer'),
    maptypes.vector.normal.map,
    {
        zoom: 17,
        center: {lng: lng, lat: lat},

    });

function addMarkersToMap(map) {
    var campoMarker = new H.map.Marker({lng: lng, lat: lat});
    map.addObject(campoMarker);
}

addMarkersToMap(map);

// Add control for ui
var ui = H.ui.UI.createDefault(map, maptypes, 'it-IT');
var mapSettings = ui.getControl('mapsettings');
var zoom = ui.getControl('zoom');
var scalebar = ui.getControl('scalebar');

mapSettings.setAlignment('top-left');
zoom.setAlignment('top-left');
scalebar.setAlignment('top-left');