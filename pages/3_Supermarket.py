import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Supermarket Surplus - EcoTrack", layout="wide")

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

st.title("Supermarket Surplus Management")
st.markdown("Log near-expiry goods, manage supermarket inventory, and track food donations.")

SUPERMARKET_CSV = "data/supermarket_waste.csv"
df_supermarket = pd.read_csv(SUPERMARKET_CSV) if os.path.exists(SUPERMARKET_CSV) else pd.DataFrame()

if not df_supermarket.empty:
    col_map = {str(c).lower().strip(): c for c in df_supermarket.columns}
    
    item_col = col_map.get("food_type") or col_map.get("item name") or col_map.get("item") or next((col_map[k] for k in col_map if any(w in k for w in ["food", "item", "dish", "meal", "description"])), df_supermarket.columns[1] if len(df_supermarket.columns) > 1 else df_supermarket.columns[0])
    qty_col = col_map.get("quantity_kg") or col_map.get("quantity") or col_map.get("qty") or next((col_map[k] for k in col_map if any(w in k for w in ["qty", "quantity", "weight", "kg"])), None)
    date_col = col_map.get("date_added") or col_map.get("date") or next((col_map[k] for k in col_map if any(w in k for w in ["date", "time", "log"])), None)
    notes_col = col_map.get("location") or col_map.get("notes") or next((col_map[k] for k in col_map if any(w in k for w in ["note", "location", "detail"])), None)
    status_col = col_map.get("status") or "Status"

    if status_col in df_supermarket.columns:
        df_supermarket[status_col] = df_supermarket[status_col].astype(str).str.capitalize()
        df_supermarket.loc[~df_supermarket[status_col].isin(["Available", "Booked", "Donated"]), status_col] = "Available"
    else:
        df_supermarket[status_col] = "Available"
else:
    item_col, qty_col, date_col, notes_col, status_col = "food_type", "quantity_kg", "date_added", "location", "status"

st.subheader("Supermarket Sector Overview")
if not df_supermarket.empty:
    total_entries = len(df_supermarket)
    total_quantity = pd.to_numeric(df_supermarket[qty_col], errors='coerce').sum() if qty_col and qty_col in df_supermarket.columns else 0
    available_count = len(df_supermarket[df_supermarket[status_col] == "Available"])
    booked_count = len(df_supermarket[df_supermarket[status_col] == "Booked"])
    donated_count = len(df_supermarket[df_supermarket[status_col] == "Donated"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Logs", total_entries)
    col2.metric("Total Saved", f"{total_quantity:.1f} kg")
    col3.metric("Available", available_count)
    col4.metric("Booked", booked_count)
    col5.metric("Donated", donated_count)
else:
    st.info("No supermarket data logged yet.")

st.divider()

st.subheader("Log New Supermarket Surplus")
with st.form("add_supermarket_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        item_name = st.text_input("Food Item / Type", placeholder="e.g., Fresh Milk, Packaged Bread")
        quantity = st.number_input("Quantity (in kg)", min_value=0.5, step=0.5, value=4.0)
        status = st.selectbox("Initial Status", ["Available", "Booked", "Donated"])
    with col_b:
        log_date = st.date_input("Log Date")
        notes = st.text_area("Location / Storage Notes", placeholder="e.g., Aisle 4")

    if st.form_submit_button("Submit Supermarket Entry"):
        if not item_name.strip():
            st.error("Please enter a valid food type.")
        else:
            new_entry = {
                "id": f"SUP-{1000 + len(df_supermarket) + 1}",
                "donor_id": 3,
                "source_type": "Supermarket",
                item_col: item_name,
                qty_col: quantity,
                date_col: str(log_date),
                "expiry_date": str(log_date),
                notes_col: notes,
                status_col: status
            }
            pd.DataFrame([new_entry]).to_csv(SUPERMARKET_CSV, mode='a', header=not os.path.exists(SUPERMARKET_CSV), index=False)
            st.success(f"Successfully logged **{item_name}** ({quantity} kg)!")
            st.rerun()

st.divider()

st.subheader("Surplus Inventory & Booking Management")
if not df_supermarket.empty:
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        selected_statuses = st.multiselect("Filter by Status:", ["Available", "Booked", "Donated"], default=["Available", "Booked", "Donated"])
    with filter_col2:
        search_query = st.text_input("Search Food Item or Location:", placeholder="Search...")

    filtered_df = df_supermarket[df_supermarket[status_col].isin(selected_statuses)]
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
                    if btn1.button("Book Now", key=f"book_sup_{index}", use_container_width=True):
                        df_supermarket.loc[index, status_col] = "Booked"
                        df_supermarket.to_csv(SUPERMARKET_CSV, index=False)
                        st.rerun()
                elif curr_status == "Booked":
                    if btn1.button("Cancel Booking", key=f"unbook_sup_{index}", use_container_width=True):
                        df_supermarket.loc[index, status_col] = "Available"
                        df_supermarket.to_csv(SUPERMARKET_CSV, index=False)
                        st.rerun()
                    if btn2.button("Mark Donated", key=f"donate_sup_{index}", use_container_width=True):
                        df_supermarket.loc[index, status_col] = "Donated"
                        df_supermarket.to_csv(SUPERMARKET_CSV, index=False)
                        st.rerun()
                elif curr_status == "Donated":
                    st.caption("🔒 Completed / Donated")
            st.divider()
else:
    st.warning("No records found in supermarket_waste.csv.")