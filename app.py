import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Food Waste Analytics Portal", layout="wide")

css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns(6)
with nav_col1:
    st.page_link("app.py", label="📊 Dashboard")
with nav_col2:
    st.page_link("pages/1_Canteen.py", label="🏫 Canteen")
with nav_col3:
    st.page_link("pages/2_Restaurant.py", label="🍽️ Restaurant")
with nav_col4:
    st.page_link("pages/3_Supermarket.py", label="🛒 Supermarket")
with nav_col5:
    st.page_link("pages/4_Event.py", label="🎉 Event Catering")

st.divider()

st.markdown("""
    <div class="hero-box">
        <div class="hero-title" style="color: #ffffff !important;">🌱 Food Waste Analytics & Donation Portal</div>
        <div class="hero-desc" style="color: #dcfce7 !important;">A unified, multi-sector system monitoring surplus food across campus canteens, local restaurants, supermarkets, and catering events to reduce environmental footprint and streamline distribution.</div>
    </div>
""", unsafe_allow_html=True)

def load_sector_csv(file_path, sector_name):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if not df.empty:
            df["Sector"] = sector_name
            col_map = {str(c).lower().strip(): c for c in df.columns}
            
            qty_col = col_map.get("quantity_kg") or next((col_map[k] for k in col_map if any(w in k for w in ["qty", "quantity", "weight", "kg"])), None)
            status_col = col_map.get("status") or "Status"
            
            if status_col in df.columns:
                df["Normalized_Status"] = df[status_col].astype(str).str.capitalize()
            else:
                df["Normalized_Status"] = "Available"
                
            if qty_col and qty_col in df.columns:
                df["Normalized_Qty"] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
            else:
                df["Normalized_Qty"] = 0
            return df
    return pd.DataFrame()

canteen_df = load_sector_csv("data/canteen_waste.csv", "Canteen")
restaurant_df = load_sector_csv("data/restaurant_waste.csv", "Restaurant")
supermarket_df = load_sector_csv("data/supermarket_waste.csv", "Supermarket")
event_df = load_sector_csv("data/event_waste.csv", "Event")

all_dfs = [canteen_df, restaurant_df, supermarket_df, event_df]
combined_df = pd.concat([df for df in all_dfs if not df.empty], ignore_index=True) if any(not df.empty for df in all_dfs) else pd.DataFrame()

if not combined_df.empty:
    total_records = len(combined_df)
    total_quantity = combined_df["Normalized_Qty"].sum()
    available_items = len(combined_df[combined_df["Normalized_Status"] == "Available"])
    co2_reduction = round(total_quantity * 2.5, 1)
else:
    total_records, total_quantity, available_items, co2_reduction = 0, 0.0, 0, 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TOTAL RECORDS LOGGED", f"{total_records}", "Across 4 sector CSVs")
col2.metric("TOTAL VOLUME TRACKED", f"{total_quantity:.1f} kg", "Active surplus inventory")
col3.metric("AVAILABLE FOR DONATION", f"{available_items}", "Ready for NGO claim")
col4.metric("EST. CO₂ REDUCTION", f"{co2_reduction:.1f} kg", "Based on 2.5× multiplier")

st.divider()
st.markdown("### Member Data Portals")

card_col1, card_col2, card_col3, card_col4 = st.columns(4)

with card_col1:
    st.markdown('<div class="sector-card"><h4>🏫 Campus Canteen</h4><p style="color: #64748b; font-size: 13px;">Managed by Member 1</p></div>', unsafe_allow_html=True)
    if st.button("Open Canteen Portal", key="portal_canteen", use_container_width=True):
        st.switch_page("pages/1_Canteen.py")

with card_col2:
    st.markdown('<div class="sector-card"><h4>🍽️ Restaurants</h4><p style="color: #64748b; font-size: 13px;">Managed by Member 2</p></div>', unsafe_allow_html=True)
    if st.button("Open Restaurant Portal", key="portal_rest", use_container_width=True):
        st.switch_page("pages/2_Restaurant.py")

with card_col3:
    st.markdown('<div class="sector-card"><h4>🛒 Supermarkets</h4><p style="color: #64748b; font-size: 13px;">Managed by Member 3</p></div>', unsafe_allow_html=True)
    if st.button("Open Supermarket Portal", key="portal_super", use_container_width=True):
        st.switch_page("pages/3_Supermarket.py")

with card_col4:
    st.markdown('<div class="sector-card"><h4>🎉 Event Catering</h4><p style="color: #64748b; font-size: 13px;">Managed by Member 4</p></div>', unsafe_allow_html=True)
    if st.button("Open Event Portal", key="portal_event", use_container_width=True):
        st.switch_page("pages/4_Event.py")