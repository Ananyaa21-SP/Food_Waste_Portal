from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="EcoTrack - Food Waste Analytics & Donation Portal",
    layout="wide",
)

# Load global CSS if it exists
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
  with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Navigation Bar
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

# Header Banner
st.markdown(
    """
    <div style="background-color: #0e9565; padding: 25px; border-radius: 10px; color: white; margin-bottom: 25px;">
        <h2 style="margin: 0; color: white;">🌱 Food Waste Analytics & Donation Portal</h2>
        <p style="margin: 5px 0 0 0; font-size: 16px;">A unified, multi-sector system monitoring surplus food across campus canteens, local restaurants, supermarkets, and catering events to reduce environmental footprint and streamline distribution.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load all sector CSVs to calculate global metrics
data_dir = "data"
canteen_csv = os.path.join(data_dir, "canteen_waste.csv")
restaurant_csv = os.path.join(data_dir, "restaurant_waste.csv")
supermarket_csv = os.path.join(data_dir, "supermarket_waste.csv")
event_csv = os.path.join(data_dir, "event_waste.csv")

dfs = []
for path in [canteen_csv, restaurant_csv, supermarket_csv, event_csv]:
  if os.path.exists(path):
    dfs.append(pd.read_csv(path))

if dfs:
  combined_df = pd.concat(dfs, ignore_index=True)
  total_logs = len(combined_df)
  total_qty = (
      pd.to_numeric(combined_df["quantity_kg"], errors="coerce").sum()
      if "quantity_kg" in combined_df.columns
      else 0
  )
  available_df = (
      combined_df[
          combined_df["status"].astype(str).str.capitalize() == "Available"
      ]
      if "status" in combined_df.columns
      else pd.DataFrame()
  )
  available_count = len(available_df)
  co2_reduction = round(
      total_qty * 2.5, 1
  )  # 2.5x multiplier for CO2 reduction
else:
  total_logs = 0
  total_qty = 0
  available_count = 0
  co2_reduction = 0.0

# Global Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "TOTAL RECORDS LOGGED", total_logs, delta="Across 4 sector CSVs", delta_color="off"
)
m2.metric(
    "TOTAL VOLUME TRACKED",
    f"{total_qty:.1f} kg",
    delta="Active surplus inventory",
    delta_color="off",
)
m3.metric(
    "AVAILABLE FOR DONATION",
    available_count,
    delta="Ready for NGO claim",
    delta_color="off",
)
m4.metric(
    "EST. CO2 REDUCTION",
    f"{co2_reduction:.1f} kg",
    delta="Based on 2.5x multiplier",
    delta_color="off",
)

st.divider()

# ==========================================
# MEMBER DATA PORTALS (Bottom Navigation Cards)
# ==========================================
st.subheader("Member Data Portals")
st.markdown("Select a sector portal to manage logs, view inventories, and coordinate donations.")

portal_col1, portal_col2, portal_col3, portal_col4 = st.columns(4)

with portal_col1:
  with st.container():
    st.markdown("### 🏫 Campus Canteen")
    st.caption("Managed by Member 1")
    st.page_link(
        "pages/1_Canteen.py", label="Open Canteen Portal", use_container_width=True
    )

with portal_col2:
  with st.container():
    st.markdown("### 🍽️ Restaurants")
    st.caption("Managed by Member 2")
    st.page_link(
        "pages/2_Restaurant.py",
        label="Open Restaurant Portal",
        use_container_width=True,
    )

with portal_col3:
  with st.container():
    st.markdown("### 🛒 Supermarkets")
    st.caption("Managed by Member 3")
    st.page_link(
        "pages/3_Supermarket.py",
        label="Open Supermarket Portal",
        use_container_width=True,
    )

with portal_col4:
  with st.container():
    st.markdown("### 🎉 Event Catering")
    st.caption("Managed by Member 4")
    st.page_link(
        "pages/4_Event.py", label="Open Event Portal", use_container_width=True
    )
