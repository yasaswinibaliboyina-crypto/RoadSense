const API_BASE = "http://127.0.0.1:8000";

const stations = {
    ev: [
        { name: "IOCL NH-16 Charger", location: "Near Ankireddypalem Y-Junction", connector: "LEV AC", power: "3.3 kW", lat: 16.269778, lon: 80.466302 },
        { name: "Ather Kothapet", location: "Kothapet, Guntur", connector: "LEV DC", power: "3.3 kW", lat: 16.296253, lon: 80.449571 },
        { name: "Ather Sitaram Nagar", location: "Near Padmaja Petrol Bunk", connector: "LEV DC", power: "3.3 kW", lat: 16.304814, lon: 80.461698 },
        { name: "Ather Gorantla", location: "Gorantla, Guntur", connector: "LEV DC", power: "3.3 kW", lat: 16.329035, lon: 80.438296 },
        { name: "Ather Kaza Toll Plaza", location: "Kaza, NH-16", connector: "LEV DC", power: "3.3 kW", lat: 16.388414, lon: 80.535797 }
    ],
    petrol: [
        { name: "Sri Padmavathi Filling Station", location: "Autonagar, Agatha Varappadu" },
        { name: "P S Rao Fuel Products", location: "Autonagar, Guntur" },
        { name: "Jio-bp Gaddipadu", location: "Mangalagiri Road, Gaddipadu" },
        { name: "IndianOil Sitaram Nagar", location: "Kakani Road, Sitaram Nagar" },
        { name: "HP M Chadalavada Oil Corporation", location: "Agatha Varappadu, near Pedakakani" }
    ]
};

let map = null;
let mapInitialized = false;
let toastTimer = null;

const DEMO_VEHICLE = { lat: 16.3280, lon: 80.4839 };
let activeRoute = null;

function distanceKm(from, to) {
    const rad = degrees => degrees * Math.PI / 180;
    const dLat = rad(to.lat - from.lat);
    const dLon = rad(to.lon - from.lon);

    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(rad(from.lat)) *
        Math.cos(rad(to.lat)) *
        Math.sin(dLon / 2) ** 2;

    return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

async function showDrivingRoute(station) {
    showPage("map-page");

    setTimeout(async () => {
        initializeMap();
        if (!map) return;

        map.invalidateSize();

        if (activeRoute) {
            map.removeLayer(activeRoute);
            activeRoute = null;
        }

        const start = DEMO_VEHICLE;
        const end = { lat: station.lat, lon: station.lon };

        const straightKm = distanceKm(start, end);

        showToast(
            `${station.name}: ${straightKm.toFixed(2)} km straight-line distance. Finding road route...`
        );

        try {
            const url =
                "https://router.project-osrm.org/route/v1/driving/" +
                `${start.lon},${start.lat};${end.lon},${end.lat}` +
                "?overview=full&geometries=geojson";

            const response = await fetch(url);
            if (!response.ok) throw new Error("Routing service unavailable");

            const data = await response.json();
            if (data.code !== "Ok" || !data.routes?.length) {
                throw new Error("No road route found");
            }

            const route = data.routes[0];

            activeRoute = L.geoJSON(route.geometry, {
                style: {
                    color: "#55e0c0",
                    weight: 6,
                    opacity: 0.9
                }
            }).addTo(map);

            L.popup()
                .setLatLng([end.lat, end.lon])
                .setContent(
                    `<b>${station.name}</b><br>` +
                    `Straight-line distance: ${straightKm.toFixed(2)} km<br>` +
                    `Road-route distance: ${(route.distance / 1000).toFixed(2)} km<br>` +
                    `Estimated drive: ${Math.round(route.duration / 60)} min`
                )
                .openOn(map);

            map.fitBounds(activeRoute.getBounds(), { padding: [35, 35] });

            showToast(
                `Road route found: ${(route.distance / 1000).toFixed(2)} km.`
            );
        } catch (error) {
            map.setView([end.lat, end.lon], 14);
            showToast(
                "Road routing unavailable. Straight-line distance is " +
                straightKm.toFixed(2) + " km."
            );
        }
    }, 200);
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.display = "block";
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.style.display = "none";
    }, 3200);
}

function showPage(pageId) {
    const target = document.getElementById(pageId);
    if (!target) return;

    document.querySelectorAll(".page").forEach(page => {
        page.classList.toggle("active", page.id === pageId);
    });

    document.querySelectorAll(".nav").forEach(button => {
        button.classList.toggle("active", button.dataset.page === pageId);
    });

    const activeButton = document.querySelector(
        `.nav[data-page="${pageId}"]`
    );

    document.getElementById("page-title").textContent =
        activeButton ? activeButton.querySelector("span").textContent : "Overview";

    if (pageId === "map-page") {
        setTimeout(() => {
            initializeMap();
            if (map) map.invalidateSize();
        }, 100);
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll(".nav").forEach(button => {
    button.addEventListener("click", () => showPage(button.dataset.page));
});

document.querySelectorAll("[data-goto]").forEach(button => {
    button.addEventListener("click", () => showPage(button.dataset.goto));
});


// Build station cards from the prototype station records.
function renderStations() {
    const evContainer = document.getElementById("ev-stations");
    const petrolContainer = document.getElementById("petrol-stations");

    evContainer.innerHTML = stations.ev.map(station => `
        <article class="station-card">
            <div class="station-symbol">ϟ</div>
            <span class="station-tag">EV CHARGING</span>
            <h3>${station.name}</h3>
            <p>${station.location}</p>
            <p><strong>Connector:</strong> ${station.connector}<br>
               <strong>Listed power:</strong> ${station.power}</p>
            <button class="text-btn" data-station-map="${station.name}">
                View on map →
            </button>
        </article>
    `).join("");

    petrolContainer.innerHTML = stations.petrol.map(station => `
        <article class="station-card">
            <div class="station-symbol">⛽</div>
            <span class="station-tag">PETROL STATION</span>
            <h3>${station.name}</h3>
            <p>${station.location}</p>
            <p>Coordinates and verified distance are not available in the current dataset.</p>
        </article>
    `).join("");

    evContainer.querySelectorAll("[data-station-map]").forEach(button => {
        button.addEventListener("click", () => {
            showPage("map-page");

            setTimeout(() => {
                initializeMap();

                const station = stations.ev.find(
                    item => item.name === button.dataset.stationMap
                );

                if (station && map) {
                    map.setView([station.lat, station.lon], 15);
                }
            }, 150);
        });
    });
}


// Map uses approximate reference coordinates and sample station markers.
let currentLocationMarker = null;
let currentLocationCircle = null;
let evRouteLine = null;
let nearestEVControl = null;

function initializeMap() {
    if (mapInitialized) return;

    if (typeof L === "undefined") {
        showToast("Map library did not load. Check your internet connection.");
        return;
    }

    const mapElement = document.getElementById("safety-map");
    if (!mapElement) return;

    map = L.map("safety-map").setView([16.3280, 80.4839], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    const riskIcon = L.divIcon({
        className: "",
        html: '<div style="width:17px;height:17px;background:#ff6875;border:3px solid #fff;border-radius:50%;box-shadow:0 0 15px #ff6875;"></div>',
        iconSize: [17, 17],
        iconAnchor: [8, 8]
    });

    L.marker([16.3280, 80.4839], { icon: riskIcon })
        .addTo(map)
        .bindPopup("<b>Guntur Y-Junction · NH-16</b><br>Prototype caution point.<br>Risk label: HIGH (demo baseline).");

    L.circle([16.3280, 80.4839], {
        radius: 150,
        color: "#ff6875",
        fillColor: "#ff6875",
        fillOpacity: 0.12,
        weight: 1
    }).addTo(map).bindPopup(
        "Illustrative 150 m radius. Not an official surveyed boundary."
    );

    stations.ev.forEach(station => {
        L.marker([station.lat, station.lon])
            .addTo(map)
            .bindPopup(
                `<b>${station.name}</b><br>${station.location}<br>` +
                `${station.connector} · ${station.power}`
            );
    });

    mapInitialized = true;
}

function showCurrentLocation() {
    if (!navigator.geolocation) {
        showToast("Your browser does not support location access.");
        return;
    }

    showToast("Getting your current location...");

    navigator.geolocation.getCurrentPosition(
        async function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const currentLocation = [lat, lon];

            if (currentLocationMarker) map.removeLayer(currentLocationMarker);
            if (currentLocationCircle) map.removeLayer(currentLocationCircle);

            currentLocationMarker = L.marker(currentLocation)
                .addTo(map)
                .bindPopup("📍 Your current location")
                .openPopup();

            currentLocationCircle = L.circle(currentLocation, {
                radius: position.coords.accuracy,
                color: "#258cff",
                fillColor: "#258cff",
                fillOpacity: 0.12,
                weight: 2
            }).addTo(map);

            await routeToNearestEV(lat, lon);
        },
        function (error) {
            const messages = {
                1: "Location permission was denied. Allow location access in your browser and try again.",
                2: "Your current location is unavailable. Try again in a moment.",
                3: "Location request timed out. Please try again."
            };

            showToast(messages[error.code] || "Could not get your current location.");
            console.error("Geolocation error:", error.message);
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
}

async function routeToNearestEV(currentLat, currentLon) {
    if (!map) return;

    const current = { lat: currentLat, lon: currentLon };

    const nearestEV = stations.ev
        .filter(station =>
            Number.isFinite(station.lat) && Number.isFinite(station.lon)
        )
        .map(station => ({
            ...station,
            distance: distanceKm(current, station)
        }))
        .sort((a, b) => a.distance - b.distance)[0];

    if (!nearestEV) {
        showToast("No EV stations with coordinates were found.");
        return;
    }

    if (evRouteLine) {
        map.removeLayer(evRouteLine);
        evRouteLine = null;
    }

    const destination = [nearestEV.lat, nearestEV.lon];
    const start = [currentLat, currentLon];
    const straightKm = nearestEV.distance;

    try {
        const url =
            "https://router.project-osrm.org/route/v1/driving/" +
            `${currentLon},${currentLat};${nearestEV.lon},${nearestEV.lat}` +
            "?overview=full&geometries=geojson";

        const response = await fetch(url);
        if (!response.ok) throw new Error("Routing service unavailable");

        const data = await response.json();

        if (data.code !== "Ok" || !data.routes || !data.routes.length) {
            throw new Error("No road route found");
        }

        const route = data.routes[0];

        evRouteLine = L.geoJSON(route.geometry, {
            style: {
                color: "#258cff",
                weight: 6,
                opacity: 0.95
            }
        }).addTo(map);

        L.popup()
            .setLatLng(destination)
            .setContent(
                `<b>⚡ ${nearestEV.name}</b><br>` +
                `${nearestEV.location}<br>` +
                `Straight-line distance: ${straightKm.toFixed(2)} km<br>` +
                `Road-route distance: ${(route.distance / 1000).toFixed(2)} km<br>` +
                `Estimated drive: ${Math.round(route.duration / 60)} min<br>` +
                `<small>Demo station data; verify station availability before travel.</small>`
            )
            .openOn(map);

        map.fitBounds(evRouteLine.getBounds(), { padding: [40, 40] });

        showToast(
            `Nearest EV: ${nearestEV.name} · road route ${(route.distance / 1000).toFixed(2)} km`
        );
    } catch (error) {
        evRouteLine = L.polyline([start, destination], {
            color: "#258cff",
            weight: 5,
            opacity: 0.9,
            dashArray: "10, 8"
        }).addTo(map);

        L.popup()
            .setLatLng(destination)
            .setContent(
                `<b>⚡ ${nearestEV.name}</b><br>` +
                `${nearestEV.location}<br>` +
                `Straight-line distance: ${straightKm.toFixed(2)} km<br>` +
                `<small>Road routing unavailable. This is a direct line, not a driving route.</small>`
            )
            .openOn(map);

        map.fitBounds(evRouteLine.getBounds(), { padding: [40, 40] });

        showToast(
            `Nearest EV: ${nearestEV.name} · ${straightKm.toFixed(2)} km straight-line distance`
        );

        console.warn("OSRM road routing unavailable:", error);
    }
}


// Simple transparent guidance rules. These are not a validated safety model.
function analyzeConditions() {
    const speed = Number(document.getElementById("speed").value);
    const limit = Number(document.getElementById("speed-limit").value);
    const distance = Number(document.getElementById("distance").value);
    const night = document.getElementById("night").value === "true";
    const glare = document.getElementById("glare").value;
    const vehicles = Number(document.getElementById("vehicles").value);

    if (
        ![speed, limit, distance, vehicles].every(Number.isFinite) ||
        speed < 0 || limit <= 0 || distance < 0 || vehicles < 0
    ) {
        showToast("Enter valid non-negative values and a positive speed limit.");
        return null;
    }

    const advice = [];
    let score = 0;

    if (speed > limit) {
        score += 35;
        advice.push({
            title: "Speed exceeds the reference limit",
            detail: "Reduce speed safely and follow the actual posted speed limit."
        });
    } else {
        advice.push({
            title: "Keep monitoring your speed",
            detail: "Stay within the posted limit and adapt to traffic and weather."
        });
    }

    if (distance <= 300) {
        score += 25;
        advice.push({
            title: "Approaching the caution zone",
            detail: "Be alert and reduce speed safely as you approach the marked zone."
        });
    }

    if (night) {
        score += 15;
        advice.push({
            title: "Night driving conditions",
            detail: "Increase attention and maintain a safe following distance."
        });
    }

    if (glare === "HIGH") {
        score += 20;
        advice.push({
            title: "High glare reported",
            detail: "Avoid looking directly at bright lights and slow down if visibility is affected."
        });
    } else if (glare === "MEDIUM") {
        score += 10;
        advice.push({
            title: "Moderate glare reported",
            detail: "Watch visibility carefully and adjust your driving to conditions."
        });
    }

    if (vehicles >= 3) {
        score += 15;
        advice.push({
            title: "Multiple vehicles detected",
            detail: "Watch surrounding traffic and maintain sufficient distance."
        });
    } else if (vehicles > 0) {
        score += 5;
        advice.push({
            title: "Vehicles detected",
            detail: "Continue monitoring traffic around your vehicle."
        });
    }

    let risk = "LOW";

    if (score >= 50) {
        risk = "HIGH";
    } else if (score >= 25) {
        risk = "MEDIUM";
    }

    const riskElement = document.getElementById("safety-risk");
    const description = document.getElementById("result-description");
    const recommendations = document.getElementById("recommendations");

    if (riskElement) {
        riskElement.textContent = risk;
        riskElement.className = `risk-value ${risk.toLowerCase()}`;
    }

    if (description) {
        description.textContent =
            `Prototype risk score: ${score}. Risk level: ${risk}.`;
    }

    if (recommendations) {
        recommendations.innerHTML = advice.map(item => `
            <div class="recommendation-item">
                <strong>${item.title}</strong>
                <p>${item.detail}</p>
            </div>
        `).join("");
    }

    const result = document.getElementById("api-result");
    if (result) {
        result.textContent =
            `Rule-based result: ${risk} · score ${score} · ${advice.length} recommendations`;
    }

    return { speed, limit, distance, night, glare, vehicles };
}

document.getElementById("analyze-btn").addEventListener(
    "click",
    analyzeConditions
);

// Ask the backend for a machine-learning risk prediction.
document.getElementById("predict-btn").addEventListener("click", async () => {
    const values = analyzeConditions();
    if (!values) return;

    const resultBox = document.getElementById("api-result");
    resultBox.textContent = "Contacting RoadSense backend...";

    const payload = {
        speed: values.speed,
        speed_limit: values.limit,
        distance_to_risk_zone: values.distance,
        night: values.night,
        glare: values.glare,
        vehicles_detected: values.vehicles,
        latitude: 16.3280,
        longitude: 80.4839
    };

    try {
        const response = await fetch(`${API_BASE}/predict-risk`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        const predictedRisk =
            data.risk_level ||
            data.prediction ||
            data.risk ||
            data.predicted_risk;

        if (predictedRisk) {
            document.getElementById("safety-risk").textContent =
                String(predictedRisk).toUpperCase();
        }

        resultBox.textContent =
            "Backend response:\n" + JSON.stringify(data, null, 2);

        showToast("Backend prediction received.");
    } catch (error) {
        resultBox.textContent =
            "Could not get a prediction from the backend.\n" +
            error.message +
            "\nCheck that the backend is running and allows requests from this page.";

        showToast("Backend connection failed. Check the backend terminal.");
    }
});

// Initial setup.
renderStations();


const nearestEVButton = document.getElementById("nearest-ev-route-btn");

if (nearestEVButton) {
    nearestEVButton.addEventListener("click", () => {
        showPage("map-page");
        setTimeout(() => {
            initializeMap();
            showCurrentLocation();
        }, 150);
    });
}




/* RoadSense: update Overview with OpenCV brightness data */
(function updateOverviewVisibility() {
    const brightnessElement = document.getElementById("overview-brightness");
    const visibilityElement = document.getElementById("overview-visibility");
    const noteElement = document.getElementById("overview-visibility-note");

    if (!brightnessElement || !visibilityElement || !noteElement) {
        console.warn("RoadSense: Overview visibility elements not found.");
        return;
    }

    async function refreshVisibility() {
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/visibility",
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            brightnessElement.textContent =
                Number(data.brightness).toFixed(1);

            visibilityElement.textContent =
                data.visibility_estimate || "Unknown";

            const brightness = Number(data.brightness);

            if (Number.isFinite(brightness) && brightness < 60) {
                noteElement.textContent =
                    "Low frame brightness — check visibility conditions";
            } else {
                noteElement.textContent =
                    "Estimated from the processed video frame";
            }
        } catch (error) {
            visibilityElement.textContent = "Unavailable";
            noteElement.textContent =
                "Check that the RoadSense backend is running.";
            console.warn("Visibility update failed:", error);
        }
    }

    refreshVisibility();
    window.setInterval(refreshVisibility, 2000);
})();


async function loadReportHistory() {
    const status = document.getElementById("report-history-status");
    const list = document.getElementById("report-history-list");

    try {
        const response = await fetch("http://127.0.0.1:8000/report-history");

        if (!response.ok) {
            throw new Error("Could not load report history");
        }

        const data = await response.json();

        status.textContent = `Total saved reports: ${data.total_reports}`;
        list.replaceChildren();

        if (data.reports.length === 0) {
            list.textContent = "No saved reports yet.";
            return;
        }

        data.reports.forEach((item) => {
            const card = document.createElement("article");
            card.className = "report-history-card";

            const heading = document.createElement("h4");
            heading.textContent = `Risk Level: ${item.report.risk_level}`;

            const details = document.createElement("p");
            details.textContent =
                `Visibility: ${item.report.visibility_estimate} | ` +
                `Brightness: ${item.report.brightness} | ` +
                `Vehicles: ${item.report.vehicle_count}`;

            const date = document.createElement("small");
            date.textContent = new Date(item.created_at).toLocaleString();

            card.append(heading, details, date);
            list.appendChild(card);
        });
    } catch (error) {
        status.textContent = "Unable to load reports. Check that the backend is running.";
        console.error(error);
    }
}

document.getElementById("refresh-reports")?.addEventListener(
    "click",
    loadReportHistory
);

loadReportHistory();

