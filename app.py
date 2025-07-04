import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# Constants
ROOM_TYPES = {
    "Deluxe Room": 15,
    "Family Suits": 8,
    "Superior Room": 2
}
BOOKING_CSV = "C:/Users/vipul/OneDrive/Desktop/BOOKING/Booking_data.csv"
ROOMS_CSV = "C:/Users/vipul/OneDrive/Desktop/BOOKING/Booking_rooms.csv"
BOOKING_ADVANCES_CSV = "C:/Users/vipul/OneDrive/Desktop/BOOKING/Bookin_Advances.csv"
DROPDOWN_XLSX = "dropdown_data.xlsx"

# Load agent and company dropdown data
def load_dropdown_data():
    try:
        xl = pd.ExcelFile(DROPDOWN_XLSX)
        agents_df = xl.parse("Agents")
        companies_df = xl.parse("Companies")
        agent_list = agents_df["Agent_Name"].dropna().unique().tolist()
        company_list = companies_df["Company_Name"].dropna().unique().tolist()

        if "NHR" not in agent_list:
            agent_list.insert(0, "NHR")
        else:
            agent_list.remove("NHR")
            agent_list.insert(0, "NHR")

    except Exception as e:
        st.error(f"Dropdown Excel Error: {e}")
        agent_list = ["NHR"]
        company_list = []
    return agent_list, company_list

agent_list, company_list = load_dropdown_data()

# Setup page
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    div[data-baseweb="tab"] button {
        font-size: 24px !important;
        padding: 1.5rem !important;
    }
    div[data-baseweb="tab-list"] {
        justify-content: space-around;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Nature Heritage Resort - Bandhavgarh Booking System")
tabs = st.tabs([
    "📅 Booking Calendar",
    "📝 New Booking",
    "📂 Manage All Booking"
])
# Initialize session state
if "room_entries" not in st.session_state:
    st.session_state.room_entries = [{"room_type": "", "qty": 1, "rate": 0.0}]

def add_room_entry():
    st.session_state.room_entries.append({"room_type": "", "qty": 1, "rate": 0.0})

def remove_room_entry(index):
    st.session_state.room_entries.pop(index)



# Data Defination
@st.cache_data
def load_data():
    booking_df = pd.read_csv("Booking_data.csv")
    booking_df.rename(columns={"id": "Booking_ID"}, inplace=True)
    rooms_df = pd.read_csv("Booking_Rooms.csv")
    advance_df = pd.read_csv("Bookin_Advances.csv")
    return booking_df, rooms_df, advance_df

def load_dropdown_data():
    xl = pd.ExcelFile("dropdown_data.xlsx")
    agent_list = xl.parse("Agents")["Agent_Name"].dropna().unique().tolist()
    company_list = xl.parse("Companies")["Company_Name"].dropna().unique().tolist()
    return agent_list, company_list



# TAB 2: New Booking
# TAB 2: New Booking
# TAB 2: New Booking
# TAB 2: New Booking
# TAB 2: New Booking

with tabs[1]:
    st.subheader("Enter New Booking")

    st.markdown("""
        <style>
        .stTextInput > div > input, .stTextArea textarea, .stSelectbox div, .stNumberInput input, .stDateInput input {
            font-size: 18px !important;
            text-transform: uppercase !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("booking_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            check_in = st.date_input("Check In")
            pax = st.number_input("Pax", min_value=1)
            adv_date = st.date_input("Advance date")
            pickup = st.text_input("Pickup / Drop Details").upper()

        with c2:
            check_out = st.date_input("Check Out")
            nights = (check_out - check_in).days
            st.number_input("Nights", value=nights, disabled=True)
            adv_mode = st.selectbox("Advance Mode", ["CASH", "CARD", "SBI BANK", "HDFC BANK", "SHALINI"])

            check_avail = st.form_submit_button("🔍 Check Room Availability")
            if check_avail and check_out > check_in:
                try:
                    room_bookings = pd.read_csv(ROOMS_CSV)
                    room_bookings["check_in"] = pd.to_datetime(room_bookings["check_in"])
                    room_bookings["check_out"] = pd.to_datetime(room_bookings["check_out"])
                except:
                    room_bookings = pd.DataFrame(columns=["Room_Type", "Qty", "check_in", "check_out"])

                with st.expander("🛏️ Available Rooms for Selected Dates", expanded=True):
                    for room_type, total_rooms in ROOM_TYPES.items():
                        available = []
                        for single_date in pd.date_range(start=check_in, end=check_out - pd.Timedelta(days=1)):
                            overlapping = room_bookings[
                                (room_bookings["Room_Type"] == room_type) &
                                (room_bookings["check_in"] <= single_date) &
                                (room_bookings["check_out"] > single_date)
                            ]
                            booked = overlapping["Qty"].sum() if not overlapping.empty else 0
                            available.append(total_rooms - booked)
                        min_available = min(available) if available else total_rooms
                        color = "green" if min_available > 0 else "red"
                        st.markdown(
                            f"<span style='font-size:18px'><b>{room_type}:</b> <span style='color:{color}'><b>{min_available}</b> available</span></span>",
                            unsafe_allow_html=True
                        )

        with c3:
            guest_name = st.text_input("Guest Name").upper()
            agent = st.selectbox("Agent", agent_list)
            plan = st.selectbox("Meal Plan", ["AP", "CP", "MAP", "EP"])
            adv_amount = st.number_input("Advance Amount", min_value=0.0)
            safari = st.text_input("Safari Details").upper()

        with c4:
            contact = st.text_input("Guest Contact").upper()
            company = st.selectbox("Company", company_list)
            status = st.selectbox("Booking Status", ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"])
            remark = st.text_area("Remark").upper()

        confirm = st.checkbox("Confirm booking submission")
        submitted = st.form_submit_button("💾 Save Booking", type="primary")

        if submitted:
            if not confirm:
                st.warning("Please confirm booking submission before saving.")
            else:
                df = pd.read_csv(BOOKING_CSV) if os.path.exists(BOOKING_CSV) else pd.DataFrame()
                next_id = int(df["id"].max()) + 1 if not df.empty else 1

                booking_row = {
                    'id': next_id,
                    'check_in': check_in,
                    'check_out': check_out,
                    'Guest_Name': guest_name,
                    'Night': nights,
                    'Room_Type': "",
                    'Qty': "",
                    'Pax': pax,
                    'Contact': contact,
                    'Rate': "",
                    'Plan': plan,
                    'Agent': agent,
                    'Company': company,
                    'Advance_Date': adv_date,
                    'Advance_amount': adv_amount,
                    'Advance_Mode': adv_mode,
                    'Pickup_Detail': pickup,
                    'Safari Detail': safari,
                    'Confirm_By': "",
                    'Remark': remark,
                    'Status': status,
                    'Entry_Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                pd.DataFrame([booking_row]).to_csv(BOOKING_CSV, mode='a', header=not os.path.exists(BOOKING_CSV), index=False)

                room_rows = []
                for room in st.session_state.room_entries:
                    room_rows.append({
                        "Booking_ID": next_id,
                        "Check_in": check_in,
                        "Check_out": check_out,
                        "Guest_Name": guest_name,
                        "Room_Type": room["room_type"],
                        "Qty": room["qty"],
                        "Rate": room["rate"]
                    })

                pd.DataFrame(room_rows).to_csv(ROOMS_CSV, mode='a', header=not os.path.exists(ROOMS_CSV), index=False)

                advance_row = {
                    "Booking_ID": next_id,
                    "check_in": check_in,
                    "check_out": check_out,
                    "Guest_Name": guest_name,
                    "Advance_Date": adv_date,
                    "Advance_Amount": adv_amount,
                    "Advance_Mode": adv_mode
                }

                pd.DataFrame([advance_row]).to_csv(BOOKING_ADVANCES_CSV, mode='a', header=not os.path.exists(BOOKING_ADVANCES_CSV), index=False)

                st.success("Booking and advance saved successfully!")
                st.session_state.room_entries = []
                st.rerun()

    # Room Selection Section
    st.markdown("### Room Selection")
    for i, entry in enumerate(st.session_state.room_entries):
        r1, r2, r3, r4 = st.columns([3, 2, 2, 1])
        with r1:
            entry["room_type"] = st.selectbox(f"Room Type {i+1}", list(ROOM_TYPES.keys()), key=f"room_type_{i}")
        with r2:
            entry["qty"] = st.number_input(f"Qty {i+1}", min_value=1, key=f"qty_{i}")
        with r3:
            entry["rate"] = st.number_input(f"Rate {i+1}", min_value=0.0, step=100.0, key=f"rate_{i}")
        with r4:
            if st.button("❌", key=f"remove_{i}"):
                remove_room_entry(i)
                st.rerun()

    if st.button("➕ Add Another Room"):
        add_room_entry()
        st.rerun()

# TAB 3: Manage All Bookings
# TAB 3: Manage All Bookings
# TAB 3: Manage All Bookings
# TAB 3: Manage All Bookings
# TAB 3: Manage All Bookings

# TAB 3: Manage All Bookings
with tabs[2]:
    st.subheader("All Bookings")

    PASSWORD = "123456"

    try:
        # Load and prepare data
        booking_df = pd.read_csv(BOOKING_CSV)
        advances_df = pd.read_csv(BOOKING_ADVANCES_CSV)
        rooms_df = pd.read_csv(ROOMS_CSV)

        booking_df["id"] = booking_df["id"].astype(int)
        advances_df["Booking_ID"] = advances_df["Booking_ID"].astype(int)
        advances_df["Advance_Amount"] = pd.to_numeric(advances_df["Advance_Amount"], errors="coerce").fillna(0)
        rooms_df["Booking_ID"] = rooms_df["Booking_ID"].astype(int)
        rooms_df["Qty"] = pd.to_numeric(rooms_df["Qty"], errors="coerce").fillna(0)

        # Summaries
        advance_summary = advances_df.groupby("Booking_ID")["Advance_Amount"].sum().reset_index().rename(columns={"Advance_Amount": "Total_Advance"})
        room_summary = rooms_df.groupby("Booking_ID")["Qty"].sum().reset_index().rename(columns={"Qty": "Total_Room_Nos"})

        merged_df = booking_df.merge(advance_summary, how="left", left_on="id", right_on="Booking_ID")
        merged_df = merged_df.merge(room_summary, how="left", left_on="id", right_on="Booking_ID")
        merged_df.drop(columns=["Booking_ID_x", "Booking_ID_y"], inplace=True, errors="ignore")
        merged_df["Total_Advance"] = merged_df["Total_Advance"].fillna(0)
        merged_df["Total_Room_Nos"] = merged_df["Total_Room_Nos"].fillna(0).astype(int)

        # Filters
        with st.expander("🔍 Filter Bookings"):
            f1, f2, f3 = st.columns(3)
            with f1:
                checkin_filter = st.date_input("Check-in From", value=None, key="filter_checkin")
                checkout_filter = st.date_input("Check-out To", value=None, key="filter_checkout")
            with f2:
                name_filter = st.text_input("Guest Name Contains").strip().upper()
                agent_filter = st.selectbox("Agent", ["All"] + sorted(merged_df["Agent"].dropna().unique().tolist()))
            with f3:
                company_filter = st.selectbox("Company", ["All"] + sorted(merged_df["Company"].dropna().unique().tolist()))
                status_filter = st.selectbox("Status", ["All"] + sorted(merged_df["Status"].dropna().unique().tolist()))

        # Apply filters
        df_filtered = merged_df.copy()
        if checkin_filter:
            df_filtered = df_filtered[pd.to_datetime(df_filtered["check_in"], errors="coerce") >= pd.to_datetime(checkin_filter)]
        if checkout_filter:
            df_filtered = df_filtered[pd.to_datetime(df_filtered["check_out"], errors="coerce") <= pd.to_datetime(checkout_filter)]
        if name_filter:
            df_filtered = df_filtered[df_filtered["Guest_Name"].str.contains(name_filter, na=False)]
        if agent_filter != "All":
            df_filtered = df_filtered[df_filtered["Agent"] == agent_filter]
        if company_filter != "All":
            df_filtered = df_filtered[df_filtered["Company"] == company_filter]
        if status_filter != "All":
            df_filtered = df_filtered[df_filtered["Status"] == status_filter]

        # Display main table
        display_columns = [
            "id", "Guest_Name", "check_in", "check_out", "Total_Room_Nos",
            "Agent", "Company", "Status", "Total_Advance"
        ]
        st.dataframe(df_filtered[display_columns], use_container_width=True)

        # Booking ID selection
        selected_id = st.selectbox("Select Booking ID to Edit", df_filtered["id"].tolist())

        if selected_id:
            selected_booking = booking_df[booking_df["id"] == selected_id].iloc[0]
            selected_rooms = rooms_df[rooms_df["Booking_ID"] == selected_id].copy()
            selected_advances = advances_df[advances_df["Booking_ID"] == selected_id]

            st.markdown("---")
            if "edit_auth" not in st.session_state:
                st.session_state.edit_auth = False

            if not st.session_state.edit_auth:
                pw = st.text_input("Enter password to edit booking", type="password")
                if pw == PASSWORD:
                    st.success("Access granted.")
                    st.session_state.edit_auth = True
                elif pw:
                    st.error("Incorrect password.")

            if st.session_state.edit_auth:
                with st.form("edit_form"):
                    st.markdown("### ✏️ Edit Booking Details")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        check_in = st.date_input("Check In", pd.to_datetime(selected_booking["check_in"], errors="coerce"))
                        guest_name = st.text_input("Guest Name", selected_booking["Guest_Name"])
                        status = st.selectbox("Booking Status", ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"],
                            index=["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"].index(selected_booking["Status"]) if pd.notna(selected_booking["Status"]) and selected_booking["Status"] in ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"] else 0)
                    with c2:
                        check_out = st.date_input("Check Out", pd.to_datetime(selected_booking["check_out"], errors="coerce"))
                        plan = st.selectbox("Meal Plan", ["AP", "CP", "MAP", "EP"],
                            index=["AP", "CP", "MAP", "EP"].index(selected_booking["Plan"]) if pd.notna(selected_booking["Plan"]) and selected_booking["Plan"] in ["AP", "CP", "MAP", "EP"] else 0)
                        agent = st.selectbox("Agent", agent_list,
                            index=agent_list.index(selected_booking["Agent"]) if pd.notna(selected_booking["Agent"]) and selected_booking["Agent"] in agent_list else 0)
                    with c3:
                        contact = st.text_input("Contact", selected_booking["Contact"])
                        company = st.selectbox("Company", company_list,
                            index=company_list.index(selected_booking["Company"]) if pd.notna(selected_booking["Company"]) and selected_booking["Company"] in company_list else 0)
                        remark = st.text_area("Remark", selected_booking["Remark"])

                    st.markdown("### 🛏️ Existing Room Details (Editable)")
                    for idx in selected_rooms.index:
                        e1, e2, e3 = st.columns(3)
                        selected_rooms.at[idx, "Room_Type"] = e1.selectbox(f"Room Type {idx}", list(ROOM_TYPES.keys()), index=list(ROOM_TYPES.keys()).index(selected_rooms.at[idx, "Room_Type"]) if selected_rooms.at[idx, "Room_Type"] in ROOM_TYPES else 0, key=f"edit_room_type_{idx}")
                        selected_rooms.at[idx, "Qty"] = e2.number_input(f"Qty {idx}", min_value=1, value=int(selected_rooms.at[idx, "Qty"]), key=f"edit_qty_{idx}")
                        selected_rooms.at[idx, "Rate"] = e3.number_input(f"Rate {idx}", min_value=0.0, step=100.0, value=float(selected_rooms.at[idx, "Rate"]), key=f"edit_rate_{idx}")

                    st.markdown("### 💰 Existing Advance Details")
                    st.dataframe(selected_advances, use_container_width=True)

                    st.markdown("#### ➕ Add Room Entry")
                    r1, r2, r3 = st.columns(3)
                    new_room_type = r1.text_input("Room Type")
                    new_room_qty = r2.number_input("Qty", min_value=1)
                    new_room_rate = r3.number_input("Rate", min_value=0.0, step=100.0)

                    st.markdown("#### ➕ Add Advance Entry")
                    a1, a2, a3 = st.columns(3)
                    new_adv_amt = a1.number_input("Advance Amount", min_value=0.0)
                    new_adv_mode = a2.selectbox("Advance Mode", ["CASH", "CARD", "SBI BANK", "HDFC BANK", "SHALINI"])
                    new_adv_date = a3.date_input("Advance Date", datetime.today())

                    save_btn = st.form_submit_button("💾 Save Changes")

                    if save_btn:
                        booking_df.loc[booking_df["id"] == selected_id, [
                            "check_in", "check_out", "Guest_Name", "Contact",
                            "Status", "Plan", "Agent", "Company", "Remark"
                        ]] = [
                            check_in, check_out, guest_name, contact,
                            status, plan, agent, company, remark
                        ]
                        booking_df.to_csv(BOOKING_CSV, index=False)

                        rooms_df = rooms_df[rooms_df["Booking_ID"] != selected_id]
                        updated_rooms = selected_rooms.copy()
                        updated_rooms["Booking_ID"] = selected_id
                        updated_rooms["Check_in"] = check_in
                        updated_rooms["Check_out"] = check_out
                        updated_rooms["Guest_Name"] = guest_name
                        rooms_df = pd.concat([rooms_df, updated_rooms], ignore_index=True)
                        rooms_df.to_csv(ROOMS_CSV, index=False)

                        if new_room_type:
                            new_room = pd.DataFrame([{
                                "Booking_ID": selected_id,
                                "Check_in": check_in,
                                "Check_out": check_out,
                                "Guest_Name": guest_name,
                                "Room_Type": new_room_type,
                                "Qty": new_room_qty,
                                "Rate": new_room_rate
                            }])
                            new_room.to_csv(ROOMS_CSV, mode='a', header=False, index=False)

                        if new_adv_amt > 0:
                            new_adv = pd.DataFrame([{
                                "Booking_ID": selected_id,
                                "check_in": check_in,
                                "check_out": check_out,
                                "Guest_Name": guest_name,
                                "Advance_Date": new_adv_date,
                                "Advance_Amount": new_adv_amt,
                                "Advance_Mode": new_adv_mode
                            }])
                            new_adv.to_csv(BOOKING_ADVANCES_CSV, mode='a', header=False, index=False)

                        st.success("✅ Changes saved successfully.")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading bookings: {e}")


# Tab: Booking Calendar
# Tab: Booking Calendar
# Tab: Booking Calendar
# Tab: Booking Calendar
# Tab: Booking Calendar
# Tab: Booking Calendar
with tabs[0]:
    today = datetime.today()
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = today.month
        st.session_state.calendar_year = today.year

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ Previous"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1

    with nav_col2:
        current_month = st.session_state.calendar_month
        current_year = st.session_state.calendar_year
        month_name = calendar.month_name[current_month]
        st.markdown(f"<h3 style='text-align:center'>{month_name} {current_year}</h3>", unsafe_allow_html=True)

    with nav_col3:
        if st.button("➡️ Next"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1

    with st.expander("📅 Go To Specific Month & Year"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            selected_month = st.selectbox("Month", list(calendar.month_name)[1:], index=st.session_state.calendar_month - 1, key="goto_month")
        with col2:
            selected_year = st.number_input("Year", min_value=2000, max_value=2100, value=st.session_state.calendar_year, step=1, key="goto_year")
        with col3:
            if st.button("Go"):
                st.session_state.calendar_month = list(calendar.month_name).index(st.session_state.goto_month)
                st.session_state.calendar_year = st.session_state.goto_year
                st.rerun()

    month = st.session_state.calendar_month
    year = st.session_state.calendar_year
    days_in_month = calendar.monthrange(year, month)[1]
    start_day = calendar.monthrange(year, month)[0]
    weekday_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    try:
        room_bookings = pd.read_csv(ROOMS_CSV)
        room_bookings = room_bookings.dropna(subset=["Booking_ID", "check_in", "check_out"])
        room_bookings["Booking_ID"] = room_bookings["Booking_ID"].astype(int)
        room_bookings["check_in"] = pd.to_datetime(room_bookings["check_in"])
        room_bookings["check_out"] = pd.to_datetime(room_bookings["check_out"])
    except:
        room_bookings = pd.DataFrame()

    availability = {room: [ROOM_TYPES[room]] * days_in_month for room in ROOM_TYPES}
    for _, row in room_bookings.iterrows():
        try:
            in_date = pd.to_datetime(row["check_in"])
            out_date = pd.to_datetime(row["check_out"])
            qty = int(row["Qty"])
            room = str(row["Room_Type"]).strip()

            if room not in ROOM_TYPES:
                continue

            for d in pd.date_range(in_date, out_date - pd.Timedelta(days=1)):
                if d.month == month and d.year == year:
                    availability[room][d.day - 1] -= qty
        except Exception as e:
            print("Booking parse error:", e)
            continue

    st.markdown("""
    <style>
    table.booking-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 15px;
        font-family: Arial, sans-serif;
    }
    table.booking-table th, table.booking-table td {
        border: 1px solid #999;
        padding: 6px;
        text-align: center;
        min-width: 38px;
    }
    table.booking-table th {
        background-color: #003366;
        color: white;
    }
    table.booking-table td.room {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    html = "<div style='overflow-x:auto;'><table class='booking-table'>"
    html += "<tr><th>Room Type</th>" + "".join(f"<th>{day}</th>" for day in weekday_names) + "</tr>"

    day_pointer = 1
    while day_pointer <= days_in_month:
        html += "<tr><td></td>"
        week_days = []
        for i in range(7):
            if day_pointer == 1:
                day_of_week = (start_day + 1) % 7
            else:
                day_of_week = None

            if (day_pointer == 1 and i < day_of_week) or day_pointer > days_in_month:
                html += "<td></td>"
                week_days.append(None)
            else:
                html += f"<td><strong>{day_pointer}</strong></td>"
                week_days.append(day_pointer)
                day_pointer += 1
        html += "</tr>"

        for room in ROOM_TYPES:
            html += f"<tr><td class='room'>{room}</td>"
            for d in week_days:
                if d is None:
                    html += "<td></td>"
                else:
                    val = availability[room][d - 1]
                    color = "#4caf50" if val > 0 else ("#f44336" if val == 0 else "#ff9800")
                    html += f"<td style='background-color:{color}; color:white;'><b>{val}</b></td>"
            html += "</tr>"

    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)
