import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Restaurant Surplus - EcoTrack", layout="wide")

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

st.title("Restaurant Surplus & NGO Booking Management")
st.markdown("Log restaurant surplus food, manage active inventory, and track NGO food donations.")

RESTAURANT_CSV = "data/restaurant_waste.csv"
df_restaurant = pd.read_csv(RESTAURANT_CSV) if os.path.exists(RESTAURANT_CSV) else pd.DataFrame()

if not df_restaurant.empty:
    col_map = {str(c).lower().strip(): c for c in df_restaurant.columns}
    
    item_col = col_map.get("food_type") or col_map.get("item name") or col_map.get("item") or next((col_map[k] for k in col_map if any(w in k for w in ["food", "item", "dish", "meal", "description"])), df_restaurant.columns[1] if len(df_restaurant.columns) > 1 else df_restaurant.columns[0])
    qty_col = col_map.get("quantity_kg") or col_map.get("quantity") or col_map.get("qty") or next((col_map[k] for k in col_map if any(w in k for w in ["qty", "quantity", "weight", "kg"])), None)
    date_col = col_map.get("date_added") or col_map.get("date") or next((col_map[k] for k in col_map if any(w in k for w in ["date", "time", "log"])), None)
    notes_col = col_map.get("location") or col_map.get("notes") or next((col_map[k] for k in col_map if any(w in k for w in ["note", "location", "detail"])), None)
    status_col = col_map.get("status") or "Status"

    if status_col in df_restaurant.columns:
        df_restaurant[status_col] = df_restaurant[status_col].astype(str).str.capitalize()
        df_restaurant.loc[~df_restaurant[status_col].isin(["Available", "Booked", "Donated"]), status_col] = "Available"
    else:
        df_restaurant[status_col] = "Available"
else:
    item_col, qty_col, date_col, notes_col, status_col = "food_type", "quantity_kg", "date_added", "location", "status"

st.subheader("Restaurant Sector Overview")
if not df_restaurant.empty:
    total_entries = len(df_restaurant)
    total_quantity = pd.to_numeric(df_restaurant[qty_col], errors='coerce').sum() if qty_col and qty_col in df_restaurant.columns else 0
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
        item_name = st.text_input("Food Item / Type", placeholder="e.g., Pasta Alfredo, Grilled Chicken")
        quantity = st.number_input("Quantity (in kg)", min_value=0.5, step=0.5, value=3.0)
        status = st.selectbox("Initial Status", ["Available", "Booked", "Donated"])
    with col_b:
        log_date = st.date_input("Log Date")
        notes = st.text_area("Location / Pickup Notes", placeholder="e.g., Back Entrance")

    if st.form_submit_button("Submit Restaurant Entry"):
        if not item_name.strip():
            st.error("Please enter a valid food type.")
        else:
            new_entry = {
                "id": f"RES-{1000 + len(df_restaurant) + 1}",
                "donor_id": 2,
                "source_type": "Restaurant",
                item_col: item_name,
                qty_col: quantity,
                date_col: str(log_date),
                "expiry_date": str(log_date),
                notes_col: notes,
                status_col: status
            }
            pd.DataFrame([new_entry]).to_csv(RESTAURANT_CSV, mode='a', header=not os.path.exists(RESTAURANT_CSV), index=False)
            st.success(f"Successfully logged **{item_name}** ({quantity} kg)!")
            st.rerun()

st.divider()

st.subheader("Surplus Inventory & Booking Management")
if not df_restaurant.empty:
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        selected_statuses = st.multiselect("Filter by Status:", ["Available", "Booked", "Donated"], default=["Available", "Booked", "Donated"])
    with filter_col2:
        search_query = st.text_input("Search Food Item or Location:", placeholder="Search...")

    filtered_df = df_restaurant[df_restaurant[status_col].isin(selected_statuses)]
    if search_query.strip():
        filtered_df = filtered_df[filtered_df[item_col].astype(str).str.contains(search_query, case=False, na=False) | filtered_df[notes_col].astype(str).str.contains(search_query, case=False, na=False)]

    for index, row in filtered_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 3])
            with c1:
                item_val = str(row.get(item_col, 'Unnamed Item'))
                st.markdown(f"#### {item_val}")
                
                disp_date = str(row.get(date_col, 'N/A')) if date_col else 'N/A'
                disp_notes = str(row.get(notes_col, 'None')) if notes_col else 'None'
                st.caption(f"Log Date: {disp_date} | Location: {disp_notes}")
            
            with c2:
                curr_status = str(row.get(status_col, "Available")).capitalize()
                badge_class = f"status-badge-{curr_status.lower()}"
                qty_val = pd.to_numeric(row.get(qty_col, 0), errors='coerce') or 0
                st.markdown(f"**Quantity:** {qty_val} kg")
                st.markdown(f"**Status:** <span class='{badge_class}'>{curr_status}</span>", unsafe_allow_html=True)
            
            with c3:
                btn1, btn2 = st.columns(2)
                if curr_status == "Available":
                    if btn1.button("Book Now", key=f"book_rest_{index}", use_container_width=True):
                        df_restaurant.loc[index, status_col] = "Booked"
                        df_restaurant.to_csv(RESTAURANT_CSV, index=False)
                        st.rerun()
                elif curr_status == "Booked":
                    if btn1.button("Cancel Booking", key=f"unbook_rest_{index}", use_container_width=True):
                        df_restaurant.loc[index, status_col] = "Available"
                        df_restaurant.to_csv(RESTAURANT_CSV, index=False)
                        st.rerun()
                    if btn2.button("Mark Donated", key=f"donate_rest_{index}", use_container_width=True):
                        df_restaurant.loc[index, status_col] = "Donated"
                        df_restaurant.to_csv(RESTAURANT_CSV, index=False)
                        st.rerun()
                elif curr_status == "Donated":
                    st.caption("🔒 Completed / Donated")
            st.divider()
else:
    st.warning("No records found in restaurant_waste.csv.")