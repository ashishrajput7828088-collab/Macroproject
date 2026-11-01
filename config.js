/**
 * Arogya Gwalior - Frontend Map & System Configuration
 * Supports configurable Mapbox Access Tokens, Map Providers, and Global Coordinates.
 */

const AROGYA_CONFIG = {
  // Public Mapbox token is supplied by the backend environment when configured.
  mapboxToken: "",

  // Default City Center
  center: {
    lat: 26.2183,
    lng: 78.1828,
    zoom: 13,
    city: "Gwalior",
    state: "Madhya Pradesh",
    country: "India"
  },

  // Available Map Tile Providers
  tileProviders: {
    cartoVoyager: {
      name: "Google Style Crisp Map (Carto Voyager)",
      url: "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxNativeZoom: 19,
      maxZoom: 20
    },
    arcgisStreets: {
      name: "Esri World Street Map",
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
      attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, HERE, Garmin, FAO, NOAA, USGS, EPA, NPS',
      maxNativeZoom: 19,
      maxZoom: 20
    },
    arcgisSatellite: {
      name: "Esri World Imagery",
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attribution: 'Imagery &copy; <a href="https://www.esri.com/">Esri</a>, Maxar, Earthstar Geographics, and the GIS User Community',
      maxNativeZoom: 19,
      maxZoom: 20
    },
    mapboxStreets: {
      name: "Mapbox HD Streets",
      url: "https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token={token}",
      attribution: '&copy; <a href="https://www.mapbox.com/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      maxNativeZoom: 20,
      maxZoom: 20
    },
    mapboxSatellite: {
      name: "Satellite Hybrid (Earth View)",
      url: "https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token={token}",
      attribution: '&copy; <a href="https://www.mapbox.com/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      maxNativeZoom: 20,
      maxZoom: 20
    },
    osm: {
      name: "OpenStreetMap Standard",
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
      maxNativeZoom: 19,
      maxZoom: 20
    },
  },

  defaultProvider: "arcgisStreets"
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = AROGYA_CONFIG;
}
