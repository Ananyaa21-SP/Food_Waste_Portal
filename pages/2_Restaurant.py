from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import pandas as pd
import random
import streamlit as st

st.set_page_config(
    page_title="Restaurant Surplus - EcoTrack", layout="wide"
)

css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
  with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class SectorManager:

  def __init__(self, csv_path, donor_id, source_type, sample_locations):
    self.csv_path = csv_path
    self.donor_id = donor_id
    self.source_type = source_type
    self.sample_locations = sample_locations
    os.makedirs("data", exist_ok=True)
    self.auto_seed()

  def auto_seed(self):
    if not os.path.exists(self.csv_path):
      today = datetime.now()
      data = []
      prefix = self.source_type[:3].upper()
      for i in range(1, 51):
        added = today - timedelta(days=random.randint(0, 30))
        data.append({
            "id": f"{prefix}-{1000+i}",
            "donor_id": self.donor_id,
            "source_type": self.source_type,
            "food_type": random.choice(["Cooked Meals", "Dairy Products"]),
            "quantity_kg": round(random.uniform(3.0, 30.0), 1),
            "date_added": added.strftime("%Y-%m-%d"),
            "expiry_date": (
                added + timedelta(days=random.randint(1, 2))
            ).strftime("%Y-%m-%d"),
            "location": random.choice(self.sample_locations),
            "status": random.choice(["Available", "Donated", "Discarded"]),
        })
      pd.DataFrame(data).to_csv(self.csv_path, index=False)

  def load_data(self):
    if os.path.exists(self.csv_path):
      df = pd.read_csv(self.csv_path)
      if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.capitalize()
        df.loc[
            ~df["status"].isin(["Available", "Booked", "Donated"]), "status"
        ] = "Available"
      else:
        df["status"] = "Available"
      return df
    return pd.DataFrame()

  def save_data(self, df):
    df.to_csv(self.csv_path, index=False)

  def add_entry(self, item_name, quantity, status, log_date, location):
    df = self.load_data()
    prefix = self.source_type[:3].upper()
    new_id = f"{prefix}-{1000 + len(df) + 1}"
    new_entry = {
        "id": new_id,
        "donor_id": self.donor_id,
        "source_type": self.source_type,
        "food_type": item_name,
        "quantity_kg": quantity,
        "date_added": str(log_date),
        "expiry_date": str(log_date),
        "location": location,
        "status": status,
    }
    pd.DataFrame([new_entry]).to_csv(
        self.csv_path,
        mode="a",
        header=not os.path.exists(self.csv_path),
        index=False,
    )

  def update_status(self, row_id, new_status):
    df = self.load_data()
    df.loc[df["id"] == row_id, "status"] = new_status
    self.save_data(df)

  def delete_entry(self, row_id):
    df = self.load_data()
    df = df[df["id"] != row_id].reset_index(drop=True)
    self.save_data(df)


manager = SectorManager(
    csv_path="data/restaurant_waste.csv",
    donor_id=2,
    source_type="Restaurant",
    sample_locations=[
        "Bistro Bites",
        "Royal Spice Hotel",
        "Urban Cafe",
        "Grand Buffet",
    ],
)

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

st.title("Restaurant Surplus Management")
st.markdown(
    "Log leftover prepared meals, track active inventory, and manage restaurant"
    " food surplus."
)

df_restaurant = manager.load_data()
item_col, qty_col, date_col, notes_col, status_col = (
    "food_type",
    "quantity_kg",
    "date_added",
    "location",
    "status",
)

st.subheader("Restaurant Sector Overview")
if not df_restaurant.empty:
  total_entries = len(df_restaurant)
  total_quantity = pd.to_numeric(df_restaurant[qty_col], errors="coerce").sum()
  available_count = len(df_restaurant[df_restaurant[status_col] == "Available"])
  booked_count = len(df_restaurant[df_restaurant[status_col] == "Booked"])
  donated_count = len(df_restaurant[df_restaurant[status_col] == "Donated"])

  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("Total Logs", total_entries)
  col2.metric("Total Saved", f"{total_quantity:.1f} kg")
  col3.metric("Available", available_count)
  col4.metric("Booked", booked_count)
  col5.metric("Donated", donated_count)
else:
  st.info("No restaurant data logged yet.")

st.divider()

st.subheader("Log New Restaurant Surplus")
with st.form("add_restaurant_form", clear_on_submit=True):
  col_a, col_b = st.columns(2)
  with col_a:
    item_name = st.text_input(
        "Food Item / Type", placeholder="e.g., Cooked Meals, Dairy Products"
    )
    quantity = st.number_input(
        "Quantity (in kg)", min_value=0.5, step=0.5, value=5.0
    )
    status = st.selectbox("Initial Status", ["Available", "Booked", "Donated"])
  with col_b:
    log_date = st.date_input("Log Date")
    notes = st.text_input(
        "Restaurant Name / Location", placeholder="e.g., Royal Spice Hotel"
    )

  if st.form_submit_button("Submit Restaurant Entry"):
    if not item_name.strip():
      st.error("Please enter a valid food type.")
    else:
      manager.add_entry(item_name, quantity, status, log_date, notes)
      st.success(f"Successfully logged **{item_name}** ({quantity} kg)!")
      st.rerun()

st.divider()

st.subheader("Surplus Inventory, Booking & Deletion Management")
if not df_restaurant.empty:
  filter_col1, filter_col2 = st.columns([2, 2])
  with filter_col1:
    selected_statuses = st.multiselect(
        "Filter by Status:",
        ["Available", "Booked", "Donated"],
        default=["Available", "Booked", "Donated"],
        key="res_status_filter",
    )
  with filter_col2:
    search_query = st.text_input(
        "Search Food Item or Restaurant:",
        placeholder="Search...",
        key="res_search",
    )

  filtered_df = df_restaurant[df_restaurant[status_col].isin(selected_statuses)]
  if search_query.strip():
    filtered_df = filtered_df[
        filtered_df[item_col]
        .astype(str)
        .str.contains(search_query, case=False, na=False)
        | filtered_df[notes_col]
        .astype(str)
        .str.contains(search_query, case=False, na=False)
    ]

  for index, row in filtered_df.iterrows():
    row_id = row.get("id", f"RST-{index}")
    with st.container():
      c1, c2, c3 = st.columns([3, 2, 3])

      with c1:
        item_val = str(row.get(item_col, "Unnamed Item"))
        st.markdown(f"#### {item_val}")
        disp_date = str(row.get(date_col, "N/A"))
        disp_notes = str(row.get(notes_col, "None"))
        st.caption(
            f"ID: {row_id} | Log Date: {disp_date} | Location: {disp_notes}"
        )

      with c2:
        curr_status = str(row.get(status_col, "Available")).capitalize()
        badge_class = f"status-badge-{curr_status.lower()}"
        qty_val = pd.to_numeric(row.get(qty_col, 0), errors="coerce") or 0
        st.markdown(f"**Quantity:** {qty_val} kg")
        st.markdown(
            f"**Status:** <span"
            f" class='{badge_class}'>{curr_status}</span>",
            unsafe_allow_html=True,
        )

      with c3:
        act_col, del_col = st.columns([3, 1])

        with act_col:
          if curr_status == "Available":
            if st.button(
                "Book", key=f"book_res_{row_id}", use_container_width=True
            ):
              manager.update_status(row_id, "Booked")
              st.rerun()
          elif curr_status == "Booked":
            b1, b2 = st.columns(2)
            if b1.button(
                "Unbook", key=f"unbook_res_{row_id}", use_container_width=True
            ):
              manager.update_status(row_id, "Available")
              st.rerun()
            if b2.button(
                "Donate", key=f"donate_res_{row_id}", use_container_width=True
            ):
              manager.update_status(row_id, "Donated")
              st.rerun()
          elif curr_status == "Donated":
            st.caption("🔒 Completed")

        with del_col:
          del_confirm_key = f"del_confirm_{row_id}"
          if del_confirm_key not in st.session_state:
            st.session_state[del_confirm_key] = False

          if not st.session_state[del_confirm_key]:
            if st.button(
                "🗑️",
                key=f"del_btn_{row_id}",
                use_container_width=True,
                help="Delete record",
            ):
              st.session_state[del_confirm_key] = True
              st.rerun()
          else:
            if st.button(
                "🗑️", key=f"del_active_{row_id}", use_container_width=True
            ):
              st.session_state[del_confirm_key] = False
              st.rerun()

        if st.session_state.get(del_confirm_key, False):
          st.warning("⚠️ Confirm deletion?")
          if st.button(
              "Yes, Delete", key=f"yes_del_{row_id}", use_container_width=True
          ):
            manager.delete_entry(row_id)
            del st.session_state[del_confirm_key]
            st.rerun()

      st.divider()
else:
  st.warning("No records found in restaurant_waste.csv.")

if not df_restaurant.empty:
  st.subheader("📊 Restaurant Data Visualizations")
  chart_col1, chart_col2 = st.columns(2)

  with chart_col1:
    st.markdown("**Total Quantity by Food Item (kg)**")
    chart_data = df_restaurant.groupby(item_col)[qty_col].sum().reset_index()
    st.bar_chart(chart_data.set_index(item_col))

  with chart_col2:
    st.markdown("**Status Breakdown Proportion**")
    status_counts = df_restaurant[status_col].value_counts()
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        status_counts,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#3b82f6", "#fbbf24", "#10b981", "#ef4444"][
            : len(status_counts)
        ],
    )
    ax.axis("equal")
    st.pyplot(fig)
