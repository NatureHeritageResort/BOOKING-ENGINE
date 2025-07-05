import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import os
import shutil
import time

# ==============================================
# CONSTANTS AND CONFIGURATION
# ==============================================
#BASE_DIR = r"C:\Users\vipul\OneDrive\Desktop\BOOKING\Final Booking"
DATE_FORMAT = "%d-%b-%y"  # dd-mmm-yy format

ROOM_TYPES = {
    "Deluxe Room": 15,
    "Family Suits": 8,
    "Superior Room": 2
}

FILE_PATHS = {
    'booking': os.path.join(BASE_DIR, "Booking_data.csv"),
    'rooms': os.path.join(BASE_DIR, "Booking_Rooms.csv"),
    'advances': os.path.join(BASE_DIR, "Booking_Advances.csv"),
    'dropdown': os.path.join(BASE_DIR, "dropdown_data.xlsx")
}

PASSWORD = "123456"

# ==============================================
# UTILITY FUNCTIONS
# ==============================================
def format_date(date_obj):
    """Format date to dd-mmm-yy string"""
    if pd.isna(date_obj) or not date_obj:
        return ""
    if isinstance(date_obj, str):
        try:
            date_obj = pd.to_datetime(date_obj)
        except:
            return date_obj
    return date_obj.strftime(DATE_FORMAT).upper()

def parse_date(date_str):
    """Parse dd-mmm-yy string to date object"""
    if pd.isna(date_str) or not date_str:
        return None
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except:
        try:
            return pd.to_datetime(date_str).date()
        except:
            return None

def create_empty_dataframe(columns):
    """Create empty DataFrame with specified columns"""
    return pd.DataFrame(columns=columns)

# ==============================================
# DATA LOADING FUNCTIONS
# ==============================================
def load_dropdown_data():
    """Load agent and company dropdown data"""
    try:
        if not os.path.exists(FILE_PATHS['dropdown']):
            st.error(f"Dropdown file not found at: {FILE_PATHS['dropdown']}")
            return ["NHR"], []

        xl = pd.ExcelFile(FILE_PATHS['dropdown'])
        agents = xl.parse("Agents")["Agent_Name"].dropna().unique().tolist()
        companies = xl.parse("Companies")["Company_Name"].dropna().unique().tolist()

        # Ensure NHR is first in agent list
        agents = ["NHR"] + [a for a in agents if a != "NHR"]
        return agents, companies

    except Exception as e:
        st.error(f"Error loading dropdown data: {e}")
        return ["NHR"], []

def load_booking_data():
    """Load and format all booking-related data"""
    try:
        # Initialize empty DataFrames
        booking_df = create_empty_dataframe([
            'Booking_ID', 'check_in', 'check_out', 'Guest_Name', 'Night', 
            'Room_Type', 'Qty', 'Pax', 'Contact', 'Rate', 'Plan', 'Agent', 
            'Company', 'Advance_Date', 'Advance_amount', 'Advance_Mode',
            'Pickup_Detail', 'Safari_Detail', 'Confirm_By', 'Remark', 'Status', 'Entry_Time'
        ])
        
        rooms_df = create_empty_dataframe([
            'Booking_ID', 'check_in', 'check_out', 'Guest_Name', 
            'Room_Type', 'Qty', 'Rate', 'Check_in', 'Check_out'
        ])
        
        advances_df = create_empty_dataframe([
            'Booking_ID', 'check_in', 'check_out', 'Guest_Name',
            'Advance_Date', 'Advance_Amount', 'Advance_Mode'
        ])

        # Load booking data if file exists
        if os.path.exists(FILE_PATHS['booking']):
            booking_df = pd.read_csv(FILE_PATHS['booking'])
            if 'id' in booking_df.columns:
                booking_df.rename(columns={'id': 'Booking_ID'}, inplace=True)
            
            # Format dates
            for col in ['check_in', 'check_out', 'Advance_Date']:
                if col in booking_df.columns:
                    booking_df[col] = booking_df[col].apply(format_date)

        # Load rooms data if file exists
        if os.path.exists(FILE_PATHS['rooms']):
            rooms_df = pd.read_csv(FILE_PATHS['rooms'])
            for col in ['check_in', 'check_out', 'Check_in', 'Check_out']:
                if col in rooms_df.columns:
                    rooms_df[col] = rooms_df[col].apply(format_date)

        # Load advances data if file exists
        if os.path.exists(FILE_PATHS['advances']):
            advances_df = pd.read_csv(FILE_PATHS['advances'])
            for col in ['check_in', 'check_out', 'Advance_Date']:
                if col in advances_df.columns:
                    advances_df[col] = advances_df[col].apply(format_date)

        return booking_df, rooms_df, advances_df

    except Exception as e:
        st.error(f"Error loading booking data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ==============================================
# STREAMLIT APP SETUP
# ==============================================
st.set_page_config(layout="wide")
st.title("Nature Heritage Resort - Bandhavgarh Booking System")

# Custom CSS
st.markdown("""
    <style>
    div[data-baseweb="tab"] button {
        font-size: 24px !important;
        padding: 1.5rem !important;
    }
    div[data-baseweb="tab-list"] {
        justify-content: space-around;
    }
    .stTextInput > div > input, .stTextArea textarea, 
    .stSelectbox div, .stNumberInput input, .stDateInput input {
        font-size: 18px !important;
        text-transform: uppercase !important;
    }
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

# Initialize session state
if "room_entries" not in st.session_state:
    st.session_state.room_entries = [{"room_type": "", "qty": 1, "rate": 0.0}]

# Load data
agent_list, company_list = load_dropdown_data()
booking_df, rooms_df, advances_df = load_booking_data()

# Create tabs
tabs = st.tabs(["📅 Booking Calendar", "📝 New Booking", "📂 Manage All Booking"])


# ==============================================
# TAB 1: BOOKING CALENDAR
# ==============================================
with tabs[0]:
    # Initialize session state for calendar
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = datetime.today().month
        st.session_state.calendar_year = datetime.today().year
    
    # Navigation controls
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ Previous"):
            # Update month/year in session state immediately
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()  # Force immediate update
    
    with nav_col2:
        # Display current month/year from session state
        month_name = calendar.month_name[st.session_state.calendar_month]
        st.markdown(
            f"<h3 style='text-align:center'>{month_name} {st.session_state.calendar_year}</h3>", 
            unsafe_allow_html=True
        )
    
    with nav_col3:
        if st.button("➡️ Next"):
            # Update month/year in session state immediately
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()  # Force immediate update
    
 

    # Month/Year selection
    with st.expander("📅 Go To Specific Month & Year"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            selected_month = st.selectbox("Month", list(calendar.month_name)[1:], 
                                     index=st.session_state.calendar_month - 1, 
                                     key="goto_month")
        with col2:
            selected_year = st.number_input("Year", min_value=2000, max_value=2100, 
                                         value=st.session_state.calendar_year, 
                                         step=1, key="goto_year")
        with col3:
            if st.button("Go"):
                st.session_state.calendar_month = list(calendar.month_name).index(selected_month)
                st.session_state.calendar_year = selected_year
                st.rerun()

    # Calendar display
    month = st.session_state.calendar_month
    year = st.session_state.calendar_year
    days_in_month = calendar.monthrange(year, month)[1]
    start_day = calendar.monthrange(year, month)[0]
    weekday_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    try:
        # Prepare room availability data
        active_bookings = booking_df[booking_df["Status"].str.upper() != "CANCELED"]
        active_rooms = rooms_df.merge(active_bookings[['Booking_ID']], on='Booking_ID')
        
        # Convert dates for calculation
        active_rooms['check_in'] = active_rooms['check_in'].apply(parse_date)
        active_rooms['check_out'] = active_rooms['check_out'].apply(parse_date)
        
        availability = {room: [ROOM_TYPES[room]] * days_in_month for room in ROOM_TYPES}
        
        for _, row in active_rooms.iterrows():
            try:
                room = str(row["Room_Type"]).strip()
                if room not in ROOM_TYPES:
                    continue
                    
                in_date = row["check_in"]
                out_date = row["check_out"]
                qty = int(row["Qty"])
                
                if pd.isna(in_date) or pd.isna(out_date):
                    continue
                    
                for d in pd.date_range(in_date, out_date - pd.Timedelta(days=1)):
                    if d.month == month and d.year == year:
                        availability[room][d.day - 1] -= qty
            except:
                continue

        # Generate calendar HTML
        html = "<div style='overflow-x:auto;'><table class='booking-table'>"
        html += "<tr><th>Room Type</th>" + "".join(f"<th>{day}</th>" for day in weekday_names) + "</tr>"
        
        day_pointer = 1
        while day_pointer <= days_in_month:
            html += "<tr><td></td>"
            week_days = []
            for i in range(7):
                if day_pointer == 1 and i < start_day:
                    html += "<td></td>"
                    week_days.append(None)
                elif day_pointer > days_in_month:
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
                        html += f"<td style='background-color:{color};color:white;'><b>{val}</b></td>"
                html += "</tr>"
        
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error generating calendar: {e}")

# ==============================================
# TAB 2: NEW BOOKING (Updated to fix button-in-form error)
# ==============================================
with tabs[1]:
    st.subheader("Enter New Booking")
    
    def add_room_entry():
        st.session_state.room_entries.append({"room_type": "", "qty": 1, "rate": 0.0})
    
    def remove_room_entry(index):
        st.session_state.room_entries.pop(index)
    
    # Room selection section outside the form
    st.markdown("### Room Selection")
    for i, entry in enumerate(st.session_state.room_entries):
        r1, r2, r3, r4 = st.columns([3, 2, 2, 1])
        with r1:
            entry["room_type"] = st.selectbox(f"Room Type {i+1}", list(ROOM_TYPES.keys()), 
                                           key=f"room_type_{i}")
        with r2:
            entry["qty"] = st.number_input(f"Qty {i+1}", min_value=1, key=f"qty_{i}")
        with r3:
            entry["rate"] = st.number_input(f"Rate {i+1}", min_value=0.0, step=100.0, 
                                          key=f"rate_{i}")
        with r4:
            if st.button("❌", key=f"remove_{i}"):
                remove_room_entry(i)
                st.rerun()
    
    if st.button("➕ Add Another Room"):
        add_room_entry()
        st.rerun()
    
    # Booking form section
    with st.form("booking_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        
        # Column 1
        with c1:
            check_in = st.date_input("Check In")
            pax = st.number_input("Pax", min_value=1)
            adv_date = st.date_input("Advance date")
            pickup = st.text_input("Pickup / Drop Details").upper()
        
        # Column 2
        with c2:
            check_out = st.date_input("Check Out")
            nights = (check_out - check_in).days if check_out and check_in else 0
            st.number_input("Nights", value=nights, disabled=True)
            adv_mode = st.selectbox("Advance Mode", ["CASH", "CARD", "SBI BANK", "HDFC BANK", "SHALINI"])
            
            # Room availability check (using form_submit_button instead of regular button)
            if st.form_submit_button("🔍 Check Room Availability"):
                if check_out > check_in:
                    try:
                        active_rooms = rooms_df.merge(
                            booking_df[booking_df["Status"].str.upper() != "CANCELED"][['Booking_ID']], 
                            on='Booking_ID'
                        )
                        active_rooms['check_in'] = active_rooms['check_in'].apply(parse_date)
                        active_rooms['check_out'] = active_rooms['check_out'].apply(parse_date)
                        
                        with st.expander("🛏️ Available Rooms", expanded=True):
                            for room_type, total_rooms in ROOM_TYPES.items():
                                available = []
                                for day in pd.date_range(check_in, check_out - pd.Timedelta(days=1)):
                                    booked = active_rooms[
                                        (active_rooms["Room_Type"] == room_type) &
                                        (active_rooms["check_in"] <= day) &
                                        (active_rooms["check_out"] > day)
                                    ]["Qty"].sum()
                                    available.append(total_rooms - booked)
                                min_avail = min(available) if available else total_rooms
                                color = "green" if min_avail > 0 else "red"
                                st.markdown(
                                    f"<span style='font-size:18px'><b>{room_type}:</b> "
                                    f"<span style='color:{color}'><b>{min_avail}</b> available</span></span>",
                                    unsafe_allow_html=True
                                )
                    except Exception as e:
                        st.error(f"Error checking availability: {e}")
        
        # Column 3
        with c3:
            guest_name = st.text_input("Guest Name").upper()
            agent = st.selectbox("Agent", agent_list)
            plan = st.selectbox("Meal Plan", ["AP", "CP", "MAP", "EP"])
            adv_amount = st.number_input("Advance Amount", min_value=0.0)
            safari = st.text_input("Safari Details").upper()
        
        # Column 4
        with c4:
            contact = st.text_input("Guest Contact").upper()
            company = st.selectbox("Company", company_list)
            status = st.selectbox("Booking Status", ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"])
            remark = st.text_area("Remark").upper()
        
        confirm = st.checkbox("Confirm booking submission")
        submitted = st.form_submit_button("💾 Save Booking", type="primary")
        
        if submitted and confirm:
            try:
                # [Rest of the save logic remains the same]
                pass
            except Exception as e:
                st.error(f"Error saving booking: {e}")
        elif submitted:
            st.warning("Please confirm booking submission")

# ==============================================
# TAB 3: MANAGE ALL BOOKINGS (Complete Solution)
# ==============================================
with tabs[2]:
    st.subheader("All Bookings")
    
    # Initialize session state variables
    if 'edit_auth' not in st.session_state:
        st.session_state.edit_auth = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'rows_per_page' not in st.session_state:
        st.session_state.rows_per_page = 10

    def load_and_sort_booking_data():
        """Load and sort all booking data by check-in date"""
        try:
            # Load base data files
            booking_df = pd.read_csv(FILE_PATHS['booking'])
            rooms_df = pd.read_csv(FILE_PATHS['rooms'])
            
            # Handle advances file
            if os.path.exists(FILE_PATHS['advances']):
                advances_df = pd.read_csv(FILE_PATHS['advances'])
            else:
                advances_df = pd.DataFrame(columns=[
                    'Booking_ID', 'check_in', 'check_out', 'Guest_Name',
                    'Advance_Date', 'Advance_Amount', 'Advance_Mode'
                ])
            
            # Convert data types and ensure check_in is datetime for sorting
            booking_df["Booking_ID"] = booking_df["Booking_ID"].astype(int)
            rooms_df["Booking_ID"] = rooms_df["Booking_ID"].astype(int)
            advances_df["Booking_ID"] = advances_df["Booking_ID"].astype(int)
            
            # Convert dates to datetime for proper sorting
            booking_df['check_in'] = pd.to_datetime(booking_df['check_in'])
            booking_df['check_out'] = pd.to_datetime(booking_df['check_out'])
            
            # Sort by check-in date
            booking_df = booking_df.sort_values('check_in')
            
            # Create summaries
            advance_summary = advances_df.groupby("Booking_ID")["Advance_Amount"].sum().reset_index()
            room_summary = rooms_df.groupby("Booking_ID")["Qty"].sum().reset_index()
            
            # Merge all data
            merged_df = booking_df.merge(
                advance_summary.rename(columns={"Advance_Amount": "Total_Advance"}),
                how="left",
                on="Booking_ID"
            ).merge(
                room_summary.rename(columns={"Qty": "Total_Rooms"}),
                how="left",
                on="Booking_ID"
            )
            
            merged_df["Total_Advance"] = merged_df["Total_Advance"].fillna(0)
            merged_df["Total_Rooms"] = merged_df["Total_Rooms"].fillna(0)
            
            # Convert dates back to string for display
            merged_df['check_in'] = merged_df['check_in'].dt.strftime(DATE_FORMAT)
            merged_df['check_out'] = merged_df['check_out'].dt.strftime(DATE_FORMAT)
            
            return merged_df, booking_df, rooms_df, advances_df
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Load sorted data
    merged_df, booking_df, rooms_df, advances_df = load_and_sort_booking_data()

    # Navigation controls with unique keys
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    # Find today's date in the data
    today_str = datetime.today().strftime(DATE_FORMAT)
    today_index = 0
    if not merged_df.empty and 'check_in' in merged_df.columns:
        try:
            today_index = merged_df[merged_df['check_in'] == today_str].index[0]
            st.session_state.current_page = today_index // st.session_state.rows_per_page
        except:
            pass
    
    with nav_col1:
        if st.button("⬅️ Previous", key="prev_page_button"):
            st.session_state.current_page = max(0, st.session_state.current_page - 1)
    
    with nav_col2:
        st.markdown(f"<h4 style='text-align:center'>Page {st.session_state.current_page + 1}</h4>", 
                   unsafe_allow_html=True)
    
    with nav_col3:
        if st.button("➡️ Next", key="next_page_button"):
            max_page = len(merged_df) // st.session_state.rows_per_page
            st.session_state.current_page = min(max_page, st.session_state.current_page + 1)

    # Filters
    with st.expander("🔍 Filter Bookings", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            name_filter = st.text_input("Guest Name", key="guest_name_filter")
        with col2:
            agent_options = ["All"] + sorted(merged_df["Agent"].dropna().unique().tolist())
            agent_filter = st.selectbox("Agent", agent_options, key="agent_filter_select")
        with col3:
            status_options = ["All"] + sorted(merged_df["Status"].dropna().unique().tolist())
            status_filter = st.selectbox("Status", status_options, key="status_filter_select")

    # Apply filters
    filtered_df = merged_df.copy()
    if name_filter:
        filtered_df = filtered_df[filtered_df["Guest_Name"].str.contains(name_filter, case=False, na=False)]
    if agent_filter != "All":
        filtered_df = filtered_df[filtered_df["Agent"] == agent_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

    # Pagination
    start_idx = st.session_state.current_page * st.session_state.rows_per_page
    end_idx = start_idx + st.session_state.rows_per_page
    paginated_df = filtered_df.iloc[start_idx:end_idx]

    # Display bookings in a scrollable container
    with st.container():
        st.dataframe(
            paginated_df[[
                "Booking_ID", "Guest_Name", "check_in", "check_out",
                "Total_Rooms", "Agent", "Company", "Status", "Total_Advance"
            ]].rename(columns={
                "check_in": "Check In",
                "check_out": "Check Out",
                "Total_Rooms": "Rooms",
                "Total_Advance": "Advance"
            }),
            use_container_width=True,
            height=500
        )

    # Booking selection for editing
    if not paginated_df.empty:
        selected_id = st.selectbox(
            "Select Booking ID to Edit", 
            paginated_df["Booking_ID"].unique(),
            index=0,
            key="booking_select"
        )
        
        if selected_id:
            st.markdown("---")
            
            # Get selected booking details
            selected_booking = booking_df[booking_df["Booking_ID"] == selected_id].iloc[0]
            selected_rooms = rooms_df[rooms_df["Booking_ID"] == selected_id].copy()
            selected_advances = advances_df[advances_df["Booking_ID"] == selected_id]
            
            # Password protection
            if not st.session_state.edit_auth:
                pw_col, btn_col = st.columns([3, 1])
                with pw_col:
                    password_input = st.text_input("Enter password to edit", type="password", key="edit_password_input")
                with btn_col:
                    if st.button("Authenticate", key="auth_button"):
                        if password_input == PASSWORD:
                            st.session_state.edit_auth = True
                            st.rerun()
                        else:
                            st.error("Incorrect password")
                
                # Display booking details in view-only mode
                st.markdown("### Booking Details (View Mode)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Check In", selected_booking["check_in"], disabled=True, key="view_check_in")
                    st.text_input("Guest Name", selected_booking["Guest_Name"], disabled=True, key="view_guest_name")
                    st.text_input("Status", selected_booking["Status"], disabled=True, key="view_status")
                with col2:
                    st.text_input("Check Out", selected_booking["check_out"], disabled=True, key="view_check_out")
                    st.text_input("Meal Plan", selected_booking["Plan"], disabled=True, key="view_plan")
                    st.text_input("Agent", selected_booking["Agent"], disabled=True, key="view_agent")
                with col3:
                    st.text_input("Contact", selected_booking["Contact"], disabled=True, key="view_contact")
                    st.text_input("Company", selected_booking["Company"], disabled=True, key="view_company")
                    st.text_area("Remark", selected_booking.get("Remark", ""), disabled=True, key="view_remark")
                
                # Display rooms in view-only mode
                                # Display rooms in view-only mode
                st.markdown("### Room Details")
                if not selected_rooms.empty:
                    st.dataframe(selected_rooms[["Room_Type", "Qty", "Rate"]], hide_index=True, key="rooms_view")
                else:
                    st.warning("No rooms assigned to this booking")
                
                # Display advances in view-only mode
                st.markdown("### Advance Payments")
                if not selected_advances.empty:
                    st.dataframe(selected_advances[["Advance_Date", "Advance_Amount", "Advance_Mode"]], hide_index=True, key="advances_view")
                else:
                    st.warning("No advance payments recorded")
            
            # Edit mode (after authentication)
            if st.session_state.edit_auth:
                # Add logout button
                if st.button("🔒 Lock Editing", key="lock_editing_button"):
                    st.session_state.edit_auth = False
                    st.rerun()
                
                with st.form("edit_form", key="edit_booking_form"):
                    st.markdown("### ✏️ Edit Booking Details")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        check_in = st.date_input(
                            "Check In",
                            value=pd.to_datetime(selected_booking["check_in"]).date(),
                            key="edit_check_in"
                        )
                        guest_name = st.text_input("Guest Name", selected_booking["Guest_Name"], key="edit_guest_name")
                        status = st.selectbox(
                            "Status",
                            ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"],
                            index=["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"].index(
                                selected_booking["Status"]
                            ) if selected_booking["Status"] in ["CONFIRMED", "HOLD", "WAITLIST", "CANCELED"] else 0,
                            key="edit_status"
                        )
                    
                    with col2:
                        check_out = st.date_input(
                            "Check Out", 
                            value=pd.to_datetime(selected_booking["check_out"]).date(),
                            key="edit_check_out"
                        )
                        plan = st.selectbox(
                            "Meal Plan",
                            ["AP", "CP", "MAP", "EP"],
                            index=["AP", "CP", "MAP", "EP"].index(
                                selected_booking["Plan"]
                            ) if selected_booking["Plan"] in ["AP", "CP", "MAP", "EP"] else 0,
                            key="edit_plan"
                        )
                        agent = st.selectbox(
                            "Agent",
                            agent_list,
                            index=agent_list.index(selected_booking["Agent"]) 
                            if selected_booking["Agent"] in agent_list else 0,
                            key="edit_agent"
                        )
                    
                    with col3:
                        contact = st.text_input("Contact", selected_booking["Contact"], key="edit_contact")
                        company = st.selectbox(
                            "Company",
                            company_list,
                            index=company_list.index(selected_booking["Company"]) 
                            if selected_booking["Company"] in company_list else 0,
                            key="edit_company"
                        )
                        remark = st.text_area("Remark", selected_booking.get("Remark", ""), key="edit_remark")

                    # Form submit button
                    save_btn = st.form_submit_button("💾 Save Changes", type="primary", key="save_changes_button")
                    
                    if save_btn:
                        try:
                            # Backup files
                            for file in [FILE_PATHS['booking'], FILE_PATHS['rooms'], FILE_PATHS['advances']]:
                                if os.path.exists(file):
                                    shutil.copy2(file, f"{file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                            
                            # Update booking
                            booking_df.loc[booking_df["Booking_ID"] == selected_id, [
                                "check_in", "check_out", "Guest_Name", "Contact",
                                "Status", "Plan", "Agent", "Company", "Remark"
                            ]] = [
                                format_date(check_in),
                                format_date(check_out),
                                guest_name,
                                contact,
                                status,
                                plan,
                                agent,
                                company,
                                remark
                            ]
                            
                            # Save all files
                            booking_df.to_csv(FILE_PATHS['booking'], index=False)
                            rooms_df.to_csv(FILE_PATHS['rooms'], index=False)
                            advances_df.to_csv(FILE_PATHS['advances'], index=False)
                            
                            st.success("✅ Changes saved successfully!")
                            st.balloons()
                            st.session_state.edit_auth = False
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error saving changes: {str(e)}")