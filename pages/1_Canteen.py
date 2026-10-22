import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Canteen Surplus - EcoTrack", layout="wide")

css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
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

st.title("Canteen Surplus Management")
st.markdown("Log daily canteen surplus food, manage active inventory, track food donations, and analyze data.")

CANTEEN_CSV = "data/canteen_waste.csv"

# Load Data with Robust Error Handling
try:
    df_canteen = pd.read_csv(CANTEEN_CSV) if os.path.exists(CANTEEN_CSV) else pd.DataFrame()
except Exception as e:
    df_canteen = pd.DataFrame()
    st.error(f"Error loading canteen data: {e}")

# Direct CSV Column Mapping matching your exact schema
item_col = "food_type"
qty_col = "quantity_kg"
date_col = "date_added"
notes_col = "location"
status_col = "status"

if not df_canteen.empty:
    if status_col in df_canteen.columns:
        df_canteen[status_col] = df_canteen[status_col].astype(str).str.capitalize()
        df_canteen.loc[~df_canteen[status_col].isin(["Available", "Booked", "Donated"]), status_col] = "Available"
    else:
        df_canteen[status_col] = "Available"

st.subheader("Canteen Sector Overview")
if not df_canteen.empty:
    total_entries = len(df_canteen)
    total_quantity = pd.to_numeric(df_canteen[qty_col], errors='coerce').sum() if qty_col in df_canteen.columns else 0
    available_count = len(df_canteen[df_canteen[status_col] == "Available"])
    booked_count = len(df_canteen[df_canteen[status_col] == "Booked"])
    donated_count = len(df_canteen[df_canteen[status_col] == "Donated"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Logs", total_entries)
    col2.metric("Total Saved", f"{total_quantity:.1f} kg")
    col3.metric("Available", available_count)
    col4.metric("Booked", booked_count)
    col5.metric("Donated", donated_count)
else:
    st.info("No canteen data logged yet.")

st.divider()

# Log New Surplus Form
st.subheader("Log New Canteen Surplus")
with st.form("add_canteen_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        item_name = st.text_input("Food Item / Type", placeholder="e.g., Bakery & Bread, Cooked Meals")
        quantity = st.number_input("Quantity (in kg)", min_value=0.5, step=0.5, value=2.0)
        status = st.selectbox("Initial Status", ["Available", "Booked", "Donated"])
    with col_b:
        log_date = st.date_input("Log Date")
        notes = st.text_area("Location / Pickup Notes", placeholder="e.g., Central Dining Hall")

    if st.form_submit_button("Submit Canteen Entry"):
        if not item_name.strip():
            st.error("Please enter a valid food type.")
        else:
            try:
                new_entry = {
                    "id": f"CNT-{1000 + len(df_canteen) + 1}",
                    "donor_id": 1,
                    "source_type": "Canteen",
                    item_col: item_name,
                    qty_col: quantity,
                    date_col: str(log_date),
                    "expiry_date": str(log_date),
                    notes_col: notes,
                    status_col: status
                }
                new_df = pd.DataFrame([new_entry])
                new_df.to_csv(CANTEEN_CSV, mode='a', header=not os.path.exists(CANTEEN_CSV), index=False)
                st.success(f"Successfully logged **{item_name}** ({quantity} kg)!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save entry: {e}")

st.divider()

# Surplus Inventory & Booking Management (Includes Delete Feature)
st.subheader("Surplus Inventory, Booking & Deletion Management")
if not df_canteen.empty:
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        selected_statuses = st.multiselect("Filter by Status:", ["Available", "Booked", "Donated"], default=["Available", "Booked", "Donated"])
    with filter_col2:
        search_query = st.text_input("Search Food Item or Location:", placeholder="Search...")

    filtered_df = df_canteen[df_canteen[status_col].isin(selected_statuses)]
    if search_query.strip():
        filtered_df = filtered_df[filtered_df[item_col].astype(str).str.contains(search_query, case=False, na=False) | filtered_df[notes_col].astype(str).str.contains(search_query, case=False, na=False)]

    for index, row in filtered_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 3])
            with c1:
                item_val = str(row.get(item_col, 'Unnamed Item'))
                st.markdown(f"#### {item_val}")
                disp_date = str(row.get(date_col, 'N/A'))
                disp_notes = str(row.get(notes_col, 'None'))
                st.caption(f"Log Date: {disp_date} | Location: {disp_notes}")
            
            with c2:
                curr_status = str(row.get(status_col, "Available")).capitalize()
                qty_val = pd.to_numeric(row.get(qty_col, 0), errors='coerce') or 0
                st.markdown(f"**Quantity:** {qty_val} kg")
                st.markdown(f"**Status:** {curr_status}")
            
            with c3:
                btn1, btn2, btn_del = st.columns(3)
                if curr_status == "Available":
                    if btn1.button("Book", key=f"book_cant_{index}", use_container_width=True):
                        df_canteen.loc[index, status_col] = "Booked"
                        df_canteen.to_csv(CANTEEN_CSV, index=False)
                        st.rerun()
                elif curr_status == "Booked":
                    if btn1.button("Unbook", key=f"unbook_cant_{index}", use_container_width=True):
                        df_canteen.loc[index, status_col] = "Available"
                        df_canteen.to_csv(CANTEEN_CSV, index=False)
                        st.rerun()
                    if btn2.button("Donate", key=f"donate_cant_{index}", use_container_width=True):
                        df_canteen.loc[index, status_col] = "Donated"
                        df_canteen.to_csv(CANTEEN_CSV, index=False)
                        st.rerun()
                elif curr_status == "Donated":
                    st.caption("🔒 Completed")

                # Delete Feature with clear visible confirmation
                if btn_del.button("🗑️", key=f"del_cant_{index}", help="Delete Record"):
                    st.session_state[f"confirm_del_{index}"] = True

                if st.session_state.get(f"confirm_del_{index}", False):
                    st.markdown('<p style="color: #dc2626; font-weight: 700; font-size: 14px; margin: 4px 0;">⚠️ Confirm deletion?</p>', unsafe_allow_html=True)
                    if st.button("Yes, Delete", key=f"yes_del_index_{index}", use_container_width=True):
                        df_canteen = df_canteen.drop(index)
                        df_canteen.to_csv(CANTEEN_CSV, index=False)
                        del st.session_state[f"confirm_del_{index}"]
                        st.rerun()
            st.divider()

    # ==========================================================================
    # DATA VISUALIZATION SECTION (1 Compact Bar Chart + 1 Pie Chart)
    # ==========================================================================
    st.divider()
    st.subheader("📊 Canteen Data Visualizations")
    
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### Total Quantity by Food Item (kg)")
        if not filtered_df.empty and qty_col in filtered_df.columns:
            qty_data = filtered_df.groupby(item_col)[qty_col].sum().reset_index()
            qty_data = qty_data.set_index(item_col)
            st.bar_chart(qty_data, height=280)
        else:
            st.info("Not enough data for quantity chart.")

    with chart_col2:
        st.markdown("##### Status Breakdown Proportion")
        if not filtered_df.empty:
            status_counts = filtered_df[status_col].value_counts()
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['#4da6ff', '#ffad33', '#66cc66'])
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.info("Not enough data for pie chart.")

else:
    st.warning("No records found in canteen_waste.csv.")
