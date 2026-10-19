import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Event Catering - EcoTrack", layout="wide")

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

st.title("Event Catering Surplus Management")
st.markdown("Log surplus catering food from events, manage records, and track environmental savings.")

EVENT_CSV = "data/event_waste.csv"
df_event = pd.read_csv(EVENT_CSV) if os.path.exists(EVENT_CSV) else pd.DataFrame()

if not df_event.empty:
    col_map = {c.lower().strip(): c for c in df_event.columns}
    
    possible_item_keys = ["item name", "item", "food item", "name", "food", "description", "dish", "meal"]
    item_col = next((col_map[k] for k in possible_item_keys if k in col_map), None)
    
    if not item_col:
        non_id_cols = [c for c in df_event.columns if not any(w in c.lower() for w in ["id", "code", "status", "qty", "quantity", "date", "note"])]
        item_col = non_id_cols[0] if non_id_cols else (df_event.columns[1] if len(df_event.columns) > 1 else df_event.columns[0])

    qty_col = next((col_map[k] for k in ["quantity", "quantity (kg)", "qty", "weight"] if k in col_map), None)
    status_col = next((col_map[k] for k in ["status", "state", "claim status"] if k in col_map), "Status")
    notes_col = next((col_map[k] for k in ["notes", "note", "pickup notes"] if k in col_map), "Notes")
    date_col = next((col_map[k] for k in ["log date", "date", "timestamp"] if k in col_map), "Log Date")
    
    if status_col not in df_event.columns:
        df_event[status_col] = "Available"
    else:
        df_event[status_col] = df_event[status_col].astype(str).str.capitalize()
        df_event.loc[~df_event[status_col].isin(["Available", "Booked", "Donated"]), status_col] = "Available"

    if not qty_col:
        numeric_cols = df_event.select_dtypes(include=['number']).columns
        qty_col = numeric_cols[0] if len(numeric_cols) > 0 else None
else:
    item_col, qty_col, status_col, notes_col, date_col = "Item Name", "Quantity", "Status", "Notes", "Log Date"

st.subheader("Event Sector Overview")
if not df_event.empty:
    total_entries = len(df_event)
    total_quantity = pd.to_numeric(df_event[qty_col], errors='coerce').sum() if qty_col else 0
    available_count = len(df_event[df_event[status_col] == "Available"])
    booked_count = len(df_event[df_event[status_col] == "Booked"])
    donated_count = len(df_event[df_event[status_col] == "Donated"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Logs", total_entries)
    col2.metric("Total Saved", f"{total_quantity:.1f} kg")
    col3.metric("Available", available_count)
    col4.metric("Booked", booked_count)
    col5.metric("Donated", donated_count)
else:
    st.info("No event data logged yet.")

st.divider()

st.subheader("Log New Event Surplus")
with st.form("add_event_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        item_name = st.text_input("Food Item Name", placeholder="e.g., Buffet Rice, Mixed Salad")
        quantity = st.number_input("Quantity (in kg)", min_value=0.5, step=0.5, value=5.0)
        status = st.selectbox("Initial Status", ["Available", "Booked", "Donated"])
    with col_b:
        log_date = st.date_input("Log Date")
        notes = st.text_area("Event Location / Notes", placeholder="e.g., Grand Hall, Pickup at Gate 2")

    if st.form_submit_button("Submit Event Entry"):
        if not item_name.strip():
            st.error("Please enter a valid food item name.")
        else:
            new_entry = {item_col: item_name, "Sector": "Event", qty_col: quantity, date_col: str(log_date), status_col: status, notes_col: notes}
            pd.DataFrame([new_entry]).to_csv(EVENT_CSV, mode='a', header=not os.path.exists(EVENT_CSV), index=False)
            st.success(f"Successfully logged **{item_name}** ({quantity} kg)!")
            st.rerun()

st.divider()

st.subheader("Surplus Inventory & Booking Management")
if not df_event.empty:
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        selected_statuses = st.multiselect("Filter by Status:", ["Available", "Booked", "Donated"], default=["Available", "Booked", "Donated"])
    with filter_col2:
        search_query = st.text_input("Search Food Item or Notes:", placeholder="Search...")

    filtered_df = df_event[df_event[status_col].isin(selected_statuses)]
    if search_query.strip():
        filtered_df = filtered_df[filtered_df[item_col].astype(str).str.contains(search_query, case=False, na=False)]

    for index, row in filtered_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 3])
            with c1:
                st.markdown(f"#### {row.get(item_col, 'Unnamed Item')}")
                st.caption(f"Log Date: {row.get(date_col, 'N/A')} | Notes: {row.get(notes_col, 'None')}")
            with c2:
                curr_status = str(row.get(status_col, "Available")).capitalize()
                badge_class = f"status-badge-{curr_status.lower()}"
                qty_val = pd.to_numeric(row.get(qty_col, 0), errors='coerce') or 0
                st.markdown(f"**Quantity:** {qty_val} kg")
                st.markdown(f"**Status:** <span class='{badge_class}'>{curr_status}</span>", unsafe_allow_html=True)
            with c3:
                btn1, btn2 = st.columns(2)
                if curr_status == "Available":
                    if btn1.button("Book Now", key=f"book_evt_{index}", use_container_width=True):
                        df_event.loc[index, status_col] = "Booked"
                        df_event.to_csv(EVENT_CSV, index=False)
                        st.rerun()
                elif curr_status == "Booked":
                    if btn1.button("Cancel Booking", key=f"unbook_evt_{index}", use_container_width=True):
                        df_event.loc[index, status_col] = "Available"
                        df_event.to_csv(EVENT_CSV, index=False)
                        st.rerun()
                    if btn2.button("Mark Donated", key=f"donate_evt_{index}", use_container_width=True):
                        df_event.loc[index, status_col] = "Donated"
                        df_event.to_csv(EVENT_CSV, index=False)
                        st.rerun()
                elif curr_status == "Donated":
                    st.caption("🔒 Completed / Donated")
            st.divider()
else:
    st.warning("No records found in event_waste.csv.")