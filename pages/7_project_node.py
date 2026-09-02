# pages/7_project_node.py
"""
Project Node — geographic POI scanner (native to Project Echo, MAP VIEW).

Scans a coordinate + radius via the Overpass API for OpenStreetMap points of
interest across category presets, plots them on an in-page Leaflet (folium)
map, lists the matched assets, and exports KML.

Native to the app: uses require_login(), the shared sidebar/theme, DB client,
and the app's stone/navy design tokens. The scan controls live INSIDE the page
(left panel), not in the global sidebar.
"""
import json

import requests
import streamlit as st

from utils.auth import require_login
from components.sidebar import setup_page_layout
from utils.db import get_supabase_client

st.set_page_config(page_title="Project Node", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------
# AUTH GATE + shared shell (native look)
# ------------------------------------------------------------
require_login()
setup_page_layout()

# ------------------------------------------------------------
# State
# ------------------------------------------------------------
DEFAULT_COORDS = "14.5995, 120.9842"
DEFAULT_RADIUS = 1000

if "geo_coords" not in st.session_state:
    st.session_state.geo_coords = DEFAULT_COORDS
if "geo_radius" not in st.session_state:
    st.session_state.geo_radius = DEFAULT_RADIUS
if "scanned_records" not in st.session_state:
    st.session_state.scanned_records = []
if "last_scan_lat" not in st.session_state:
    st.session_state.last_scan_lat = 14.5995
if "last_scan_lon" not in st.session_state:
    st.session_state.last_scan_lon = 120.9842

# ------------------------------------------------------------
# POI category presets (from Open Node spec)
# ------------------------------------------------------------
POI_CONFIG = {
    "COMMERCIAL & OFFICES": [
        ["Corporate Office", '"building"~"office|commercial",i'],
        ["IT/Tech Center", '"office"~"it|telecommunication",i'],
        ["Business Center", '"building"="commercial"'],
        ["Bank", '"amenity"="bank"'],
        ["ATM", '"amenity"="atm"'],
        ["Office", '"office"="yes"'],
    ],
    "RETAIL": [
        ["Mall/Department Store", '"shop"~"mall|department_store",i'],
        ["Supermarket", '"shop"~"market|grocery",i'],
        ["Convenience Store", '"shop"="convenience"'],
        ["Pharmacy", '"amenity"="pharmacy"'],
        ["Hardware", '"shop"~"hardware|doityourself",i'],
        ["General Shops", '"shop"~"boutique|clothes|shoes",i'],
        ["Beauty", '"shop"="beauty"'],
        ["Bicycle", '"shop"="bicycle"'],
        ["Books/Stationary", '"shop"~"books|stationary",i'],
        ["Car", '"shop"="car"'],
        ["Clothes", '"shop"="clothes"'],
        ["Department store", '"shop"="department_store"'],
        ["Hairdresser", '"shop"="hairdresser"'],
        ["Jewelry", '"shop"="jewelry"'],
        ["Kiosk", '"shop"="kiosk"'],
        ["Marketplace", '"amenity"="marketplace"'],
        ["Optician", '"shop"="optician"'],
        ["Pets", '"shop"="pets"'],
        ["Phone", '"shop"="mobile_phone"'],
        ["Photo", '"shop"="photo"'],
        ["Shoes", '"shop"="shoes"'],
        ["Shopping centre", '"shop"="mall"'],
        ["Toys", '"shop"="toys"'],
        ["Travel agency", '"shop"="travel_agency"'],
    ],
    "FOOD, BEVERAGE & HOSPITALITY": [
        ["Restaurant", '"amenity"="restaurant"'],
        ["Cafe/Coffee Shop", '"amenity"~"cafe|coffee",i'],
        ["Fast Food", '"amenity"="fast_food"'],
        ["Bar/Pub/Nightclub", '"amenity"~"bar|pub|nightclub",i'],
        ["Bakery/Pastry", '"shop"="bakery"'],
        ["Food court", '"amenity"="food_court"'],
        ["Ice cream", '"amenity"="ice_cream"'],
        ["Hotel", '"tourism"="hotel"'],
        ["Motel", '"tourism"="motel"'],
        ["Guest House", '"tourism"="guest_house"'],
        ["Hostel", '"tourism"="hostel"'],
        ["Casino", '"amenity"="casino"'],
    ],
    "RESIDENTIAL": [
        ["Apartments", '"building"="apartments"'],
        ["House", '"building"="house"'],
        ["Residential Area", '"landuse"="residential"'],
        ["Condominium", '"building"="residential"'],
        ["City", '"place"="city"'],
        ["Town", '"place"="town"'],
        ["Village", '"place"="village"'],
        ["Hamlet", '"place"="hamlet"'],
        ["Suburb", '"place"="suburb"'],
        ["Construction", '"landuse"="construction"'],
    ],
    "INDUSTRIAL & LOGISTICS": [
        ["Expressway Exits", '"highway"~"motorway_junction|toll_gantry",i'],
        ["Ports & Terminals", '"industrial"="port"'],
        ["Manufacturing Plants", '"industrial"~"factory|manufacturing|processing",i'],
        ["Cold Storage Facilities", '"warehouse"~"cold_store|cold_storage",i'],
        ["Industrial Parks/Estates", '"landuse"~"industrial|industrial_estate",i'],
        ["Warehouses & Depots", '"building"~"warehouse|depot",i'],
        ["Storage Facilities", '"building"="storage"'],
        ["Truck Access Routes (HGV)", '"hgv"~"designated|yes",i'],
    ],
    "HEALTH & EMERGENCY SERVICES": [
        ["Hospital", '"amenity"~"hospital|clinic",i'],
        ["Clinic", '"amenity"="clinic"'],
        ["Pharmacy", '"amenity"="pharmacy"'],
        ["Police Station", '"amenity"="police"'],
        ["Fire Station", '"amenity"="fire_station"'],
        ["Defibrillator - AED", '"emergency"="defibrillator"'],
    ],
    "GOVERNMENT, EDUCATION & INFRASTRUCTURE": [
        ["City Hall", '"amenity"="townhall"'],
        ["Airport Terminal", '"aeroway"~"terminal|aerodrome",i'],
        ["University/College", '"amenity"~"university|college",i'],
        ["K-12 School", '"amenity"="school"'],
        ["Embassy", '"amenity"="embassy"'],
        ["Library", '"amenity"="library"'],
        ["Post Office", '"amenity"="post_office"'],
        ["Kindergarten", '"amenity"="kindergarten"'],
        ["Public camera", '"man_made"="surveillance"'],
    ],
    "LEISURE, SPORTS & PUBLIC SPACES": [
        ["Church", '"religion"="christian"'],
        ["Mosque", '"religion"="muslim"'],
        ["Buddhist Temple", '"religion"="buddhist"'],
        ["Cemetery", '"landuse"="cemetery"'],
        ["Bicycle Parking", '"amenity"="bicycle_parking"'],
        ["Bicycle Rental", '"amenity"="bicycle_rental"'],
        ["Cinema", '"amenity"="cinema"'],
        ["Fuel", '"amenity"="fuel"'],
        ["Parking", '"amenity"="parking"'],
        ["Taxi", '"amenity"="taxi"'],
        ["Theatre", '"amenity"="theatre"'],
        ["Toilets", '"amenity"="toilets"'],
        ["Basketball", '"sport"="basketball"'],
        ["Sports centre", '"leisure"="sports_centre"'],
        ["Swimming", '"sport"="swimming"'],
        ["Tennis", '"sport"="tennis"'],
        ["Busstop", '"highway"="bus_stop"'],
        ["Recycling", '"amenity"="recycling"'],
        ["Image", '"image"~".",i'],
    ],
}


def _fetch_pois(lat: float, lon: float, radius: int, tags: list, timeout: int = 90) -> list:
    """Query Overpass for POIs matching the given tag filters. Mirrors Atlas stub."""
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.openstreetmap.fr/api/interpreter",
    ]
    if tags:
        query = "[out:json][timeout:25];(" + "".join(
            f'nwr[{q}](around:{radius},{lat},{lon});' for q in tags
        ) + ");out center;"
    else:
        query = "[out:json][timeout:25];nwr(around:%d,%f,%f);out center;" % (radius, lat, lon)
    hdr = {"User-Agent": "Project-Echo/1.0"}
    for ep in endpoints:
        try:
            r = requests.post(ep, data={"data": query}, headers=hdr, timeout=timeout)
            if r.status_code == 200:
                js = r.json()
                return [
                    {
                        "name": (e.get("tags") or {}).get("name", f"{e.get('type', 'node')} {e.get('id')}"),
                        "type": e.get("type", "node"),
                        "lat": float((e.get("center") or e).get("lat", 0)),
                        "lon": float((e.get("center") or e).get("lon", 0)),
                        "tags": e.get("tags") or {},
                    }
                    for e in js.get("elements", [])
                ]
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Overpass endpoint {ep} failed: {exc}")
    return []


def compile_features_kml(features):
    kml = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Scanned POIs</name>'
    for f in features:
        if not f.get("visible", True):
            continue
        name = str(f.get("name", "Asset")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        kml += f"<Placemark><name>{name}</name><Point><coordinates>{f['lon']},{f['lat']},0</coordinates></Point></Placemark>"
    return kml + "</Document></kml>"


def _render_map(records, center_lat, center_lon, radius):
    """Build an in-page folium map with POI markers + scan-radius circle."""
    import folium
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="CartoDB Positron")
    folium.Circle(
        radius=radius,
        location=[center_lat, center_lon],
        color="#D7D3BF",
        weight=1.5,
        fill=True,
        fill_color="#A59D84",
        fill_opacity=0.10,
    ).add_to(m)
    for rec in records:
        popup = folium.Popup(str(rec.get("name", "")), max_width=220)
        folium.CircleMarker(
            location=[rec["lat"], rec["lon"]],
            radius=6,
            color="#0D1B3E",
            weight=1.5,
            fill=True,
            fill_color="#D7D3BF",
            fill_opacity=0.95,
            popup=popup,
        ).add_to(m)
    return m


# ------------------------------------------------------------
# PAGE CONTENT — controls live INSIDE the page (left panel)
# ------------------------------------------------------------
st.markdown('<p class="page-eyebrow">Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="section-title">Project Node</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="section-caption">Scan a coordinate radius for OpenStreetMap points of interest (POIs) and explore them on the map.</p>',
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1, 2.6])

# ---- In-page control panel ----
with left_col:
    with st.container(border=True):
        st.markdown("#### Scan Controls")
        location_input = st.text_input("Coordinates (lat, lon)", value=st.session_state.geo_coords, key="geo_coords_input")
        radius_val = st.number_input(
            "Radius (meters)", min_value=100, max_value=50000,
            value=int(st.session_state.geo_radius), key="geo_radius_input", step=100,
        )

        selected_tags = []
        with st.expander("Categories", expanded=True):
            for category, items in POI_CONFIG.items():
                labels = [i[0] for i in items]
                chosen = st.multiselect(category, labels, default=[], key=f"cat_{category}")
                for label, tag in items:
                    if label in chosen:
                        selected_tags.append(tag)

        scan_ready = bool(location_input.strip()) and radius_val >= 100
        if st.button("Scan Area", type="primary", key="scan_btn"):
            if not scan_ready:
                st.error("Provide valid coordinates and radius.")
            else:
                try:
                    lat_s, lon_s = [float(x.strip()) for x in location_input.split(",")[:2]]
                except Exception:  # noqa: BLE001
                    lat_s, lon_s = 0.0, 0.0
                    st.error("Coordinates must be 'lat, lon' (e.g. 14.5995, 120.9842).")
                if lat_s or lon_s:
                    st.session_state.geo_coords = location_input
                    st.session_state.geo_radius = int(radius_val)
                    st.session_state.last_scan_lat = lat_s
                    st.session_state.last_scan_lon = lon_s
                    with st.spinner("Scanning OpenStreetMap..."):
                        recs = _fetch_pois(lat_s, lon_s, int(radius_val), selected_tags)
                        st.session_state.scanned_records = recs
                    st.rerun()

        recs = st.session_state.scanned_records
        st.metric("POIs Found", len(recs))
        st.caption(
            f"Center: {st.session_state.get('last_scan_lat', 0):.4f}, {st.session_state.get('last_scan_lon', 0):.4f} · "
            f"Radius: {st.session_state.get('geo_radius', 0)}m"
        )

        if recs:
            kml = compile_features_kml(recs)
            st.download_button(
                "Download KML", data=kml, file_name="project_node_scan.kml",
                mime="application/vnd.google-earth.kml+xml", type="primary",
            )

# ---- Map view ----
with right_col:
    try:
        import folium

        map_obj = _render_map(
            st.session_state.scanned_records,
            st.session_state.get("last_scan_lat", 14.5995),
            st.session_state.get("last_scan_lon", 120.9842),
            int(st.session_state.get("geo_radius", 1000)),
        )
        st.components.v1.html(map_obj._repr_html_(), height=520, scrolling=False)
    except Exception as exc:  # noqa: BLE001
        st.info("Map preview unavailable; scanning results are still accessible below.")

# ---- Results ----
st.markdown("---")
if st.session_state.scanned_records:
    recs = st.session_state.scanned_records
    rows = [
        {
            "Name": str(r.get("name", ""))[:60],
            "Type": r.get("type", "node"),
            "Lat": round(r.get("lat", 0), 5),
            "Lon": round(r.get("lon", 0), 5),
        }
        for r in recs
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("No results yet. Choose categories (or leave empty to scan everything), then press **Scan Area**.")


# ------------------------------------------------------------
# Optional DB hook (mirrors other project pages; not required)
# ------------------------------------------------------------
def _node_db():
    client = get_supabase_client()
    if not client:
        return None
    return client
