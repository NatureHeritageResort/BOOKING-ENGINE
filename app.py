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

# Set up app layout
st.set_page_config(layout="wide")
st.title("Nature Heritage Resort - Bandhavgarh Booking System")

# Tabs
tabs = st.tabs(["Booking Calendar", "New Booking", "Manage All Booking"])

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
# ROOM BOOKING TAB#
# ROOM BOOKING TAB#
import streamlit as st
import pandas as pd
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
DROPDOWN_XLSX = "dropdown_data.xlsx"

# Load agent and company data from Excel
def load_dropdown_data():
    try:
        xl = pd.ExcelFile(DROPDOWN_XLSX)
        agents_df = xl.parse("Agents")
        companies_df = xl.parse("Companies")
        agent_list = agents_df["Agent_Name"].dropna().unique().tolist()
        company_list = companies_df["Company_Name"].dropna().unique().tolist()
    except Exception as e:
        st.error(f"Dropdown Excel Error: {e}")
        agent_list = []
        company_list = []
    return agent_list, company_list

agent_list, company_list = load_dropdown_data()

# Initialize session state for room entries
if "room_entries" not in st.session_state:
    st.session_state.room_entries = [{"room_type": "", "qty": 1, "rate": 0.0}]

def add_room_entry():
    st.session_state.room_entries.append({"room_type": "", "qty": 1, "rate": 0.0})

def remove_room_entry(index):
    st.session_state.room_entries.pop(index)

# --- Start of New Booking Tab ---
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
        adv_mode = st.selectbox("Advance Mode", ["CASH", "CARD", "SBI BANK", "HDFC BANK"])

        # Room availability checker
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
        plan = st.text_input("Meal Plan").upper()
        adv_amount = st.number_input("Advance Amount", min_value=0.0)
        safari = st.text_input("Safari Details").upper()

    with c4:
        contact = st.text_input("Guest Contact").upper()
        company = st.selectbox("Company", company_list)
        status = st.selectbox("Booking Status", ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"])
        remark = st.text_area("Remark").upper()

    confirm = st.checkbox("Confirm booking submission")
    submitted = st.form_submit_button("💾 Save Booking", type="primary")

    # Save booking
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
                    "Booking_id": next_id,
                    "Check_in": check_in,
                    "Check_out": check_out,
                    "Guest_Name": guest_name,
                    "Room_Type": room["room_type"],
                    "Qty": room["qty"],
                    "Rate": room["rate"]
                })

            pd.DataFrame(room_rows).to_csv(ROOMS_CSV, mode='a', header=not os.path.exists(ROOMS_CSV), index=False)

            st.success("Booking saved successfully!")
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
with tabs[2]:
    st.subheader("All Bookings")
    if os.path.exists(BOOKING_CSV):
        df = pd.read_csv(BOOKING_CSV)
        st.dataframe(df)
    else:
        st.warning("No booking data found.")