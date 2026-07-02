// GIS Mapping Module - Smart City Analytics Platform
// Integrates Leaflet.js to display traffic density, crime hotspots, and public transport layers.

let cityMap = null;
let currentCityName = "";
let currentLayerName = "traffic"; // default layer

// Layer groups
const trafficLayerGroup = L.layerGroup();
const crimeLayerGroup = L.layerGroup();
const transitLayerGroup = L.layerGroup();

// City centers
const CITY_COORDINATES = {
    "Mumbai": [19.0760, 72.8777],
    "Bengaluru": [12.9716, 77.5946],
    "New Delhi": [28.6139, 77.2090]
};

function initGISMap(city) {
    currentCityName = city;
    const center = CITY_COORDINATES[city] || [40.7128, -74.0060];
    
    // Destroy previous map instance if exists
    if (cityMap !== null) {
        cityMap.remove();
    }
    
    // Initialize Leaflet Map
    cityMap = L.map('exec-map', {
        center: center,
        zoom: 13,
        zoomControl: false,
        attributionControl: false
    });
    
    // Set up map tiles - Using CartoDB Dark Matter tiles which looks super premium!
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 20
    }).addTo(cityMap);
    
    // Add custom zoom control in bottom right
    L.control.zoom({
        position: 'bottomright'
    }).addTo(cityMap);

    // Generate layers for this city
    generateSpatialLayers(center);
    
    // Load default layer
    toggleGISLayer(currentLayerName);
}

function toggleGISLayer(layerName) {
    currentLayerName = layerName;
    
    // Clear all layers
    cityMap.removeLayer(trafficLayerGroup);
    cityMap.removeLayer(crimeLayerGroup);
    cityMap.removeLayer(transitLayerGroup);
    
    // Add selected layer
    if (layerName === "traffic") {
        trafficLayerGroup.addTo(cityMap);
    } else if (layerName === "crime") {
        crimeLayerGroup.addTo(cityMap);
    } else if (layerName === "transit") {
        transitLayerGroup.addTo(cityMap);
    }
}

function generateSpatialLayers(center) {
    const lat = center[0];
    const lng = center[1];
    
    // Clear previous layers content
    trafficLayerGroup.clearLayers();
    crimeLayerGroup.clearLayers();
    transitLayerGroup.clearLayers();
    
    // ------------------------------------
    // 🚦 Layer 1: Traffic Density Lines
    // ------------------------------------
    // Create simulated road segments
    const roads = [
        // Main highway (Green/Orange)
        [[lat - 0.02, lng - 0.04], [lat - 0.01, lng - 0.02], [lat, lng], [lat + 0.01, lng + 0.02], [lat + 0.02, lng + 0.04]],
        // Ring road (Red/Orange)
        [[lat + 0.015, lng - 0.03], [lat + 0.025, lng], [lat + 0.015, lng + 0.03], [lat - 0.015, lng + 0.03], [lat - 0.025, lng], [lat - 0.015, lng - 0.03]],
        // Downtown grid lines
        [[lat - 0.008, lng - 0.01], [lat + 0.008, lng - 0.01]],
        [[lat - 0.008, lng + 0.01], [lat + 0.008, lng + 0.01]],
        [[lat, lng - 0.015], [lat, lng + 0.015]]
    ];
    
    const trafficColors = ["#ef4444", "#f59e0b", "#10b981"]; // Red, Orange, Green
    
    roads.forEach((road, index) => {
        // Metropolis has more red traffic, Greenville has more green traffic
        let colorIndex = (index + currentCityName.length) % 3;
        if (currentCityName === "Mumbai") {
            colorIndex = index % 2; // only red/orange
        } else if (currentCityName === "Bengaluru") {
            colorIndex = (index % 2) + 1; // only orange/green
        }
        
        const densityColor = trafficColors[colorIndex];
        const opacity = densityColor === "#ef4444" ? 0.85 : 0.65;
        const weight = densityColor === "#ef4444" ? 6 : 4;
        const statusText = densityColor === "#ef4444" ? "Heavy Congestion" : (densityColor === "#f59e0b" ? "Moderate Traffic" : "Free Flow");
        
        const polyline = L.polyline(road, {
            color: densityColor,
            weight: weight,
            opacity: opacity
        });
        
        polyline.bindPopup(`<strong>Road Segment ID:</strong> RD-${1000 + index}<br><strong>Status:</strong> ${statusText}<br><strong>Speed:</strong> ${densityColor === "#ef4444" ? "18 km/h" : "55 km/h"}`);
        trafficLayerGroup.addLayer(polyline);
    });

    // ------------------------------------
    // 🚔 Layer 2: Crime Hotspots (Heat circles)
    // ------------------------------------
    const crimeHotspots = [
        { coords: [lat + 0.005, lng - 0.005], radius: 250, weight: 1.4, desc: "Burglary & Theft Hotspot" },
        { coords: [lat - 0.01, lng + 0.008], radius: 400, weight: 2.1, desc: "Assault & Vandalism Hotspot" },
        { coords: [lat + 0.018, lng + 0.02], radius: 180, weight: 0.8, desc: "Larceny Hotspot" }
    ];
    
    // Add more crime hotspots for Metropolis
    if (currentCityName === "Mumbai") {
        crimeHotspots.push({ coords: [lat - 0.015, lng - 0.012], radius: 320, weight: 1.8, desc: "Robbery Concentration Zone" });
    }
    
    crimeHotspots.forEach((spot, index) => {
        // Draw double rings representing heat core and outer glow
        const innerCircle = L.circle(spot.coords, {
            color: '#ef4444',
            fillColor: '#ef4444',
            fillOpacity: 0.4,
            radius: spot.radius * 0.4
        });
        
        const outerCircle = L.circle(spot.coords, {
            color: '#ef4444',
            fillColor: '#ef4444',
            fillOpacity: 0.12,
            weight: 1,
            dashArray: '5, 5',
            radius: spot.radius
        });
        
        const popupText = `<strong>Crime Zone ${index + 1}</strong><br><strong>Classification:</strong> ${spot.desc}<br><strong>Incident Index:</strong> ${spot.weight}/10.0`;
        innerCircle.bindPopup(popupText);
        outerCircle.bindPopup(popupText);
        
        crimeLayerGroup.addLayer(innerCircle);
        crimeLayerGroup.addLayer(outerCircle);
    });

    // ------------------------------------
    // 🚌 Layer 3: Public Transport Nodes & Routes
    // ------------------------------------
    // Bus & Metro Station Markers
    const transitStations = [
        { coords: [lat, lng], type: "Metro Station", name: "CST Terminal Hub" },
        { coords: [lat + 0.012, lng + 0.012], type: "Metro Station", name: "Bandra Kurla Terminus" },
        { coords: [lat - 0.015, lng - 0.015], type: "Metro Station", name: "Gateway of India Station" },
        { coords: [lat + 0.005, lng - 0.018], type: "Bus Stop", name: "Nariman Point Loop" },
        { coords: [lat - 0.012, lng + 0.018], type: "Bus Stop", name: "Andheri East Crossing" }
    ];
    
    // Custom transit station icons
    transitStations.forEach(station => {
        const markerColor = station.type === "Metro Station" ? "#a855f7" : "#3b82f6"; // purple for metro, blue for bus
        const markerHtml = `<div style="background-color: ${markerColor}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 6px ${markerColor};"></div>`;
        
        const myIcon = L.divIcon({
            html: markerHtml,
            className: "custom-transit-icon",
            iconSize: [12, 12]
        });
        
        const marker = L.marker(station.coords, { icon: myIcon });
        marker.bindPopup(`<strong>${station.name}</strong><br><strong>Type:</strong> ${station.type}<br><strong>Average Daily Flow:</strong> ${station.type === "Metro Station" ? "14,500 boardings" : "2,300 boardings"}`);
        transitLayerGroup.addLayer(marker);
    });
    
    // Transit lines
    const metroLineCoords = [
        [lat - 0.015, lng - 0.015],
        [lat, lng],
        [lat + 0.012, lng + 0.012]
    ];
    
    const metroLine = L.polyline(metroLineCoords, {
        color: "#a855f7",
        weight: 4,
        opacity: 0.75,
        dashArray: "1, 8"
    });
    
    metroLine.bindPopup("<strong>Transit Core:</strong> Metro Line Alpha");
    transitLayerGroup.addLayer(metroLine);
}
