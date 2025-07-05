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
# OS-independent path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_FORMAT = "%d-%b-%y"  # dd-mmm-yy format

ROOM_TYPES = {
    "Deluxe Room": 15,
    "Family Suits": 8,
    "Superior Room": 2
}

FILE_PATHS = {
    'booking': os.path.join(BASE_DIR, "booking_data.csv"),
    'rooms': os.path.join(BASE_DIR, "booking_rooms.csv"),
    'advances': os.path.join(BASE_DIR, "booking_advances.csv"),
    'dropdown': os.path.join(BASE_DIR, "dropdown_data.xlsx")
}

PASSWORD = "admin123"  # Change this for production

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

# ==============================================
# DATA LOADING FUNCTIONS
# ==============================================
def load_dropdown_data():
    """Load agent and company dropdown data with error handling"""
    try:
        if not os.path.exists(FILE_PATHS['dropdown']):
            # Create default data if file doesn't exist
            default_agents = ["NHR", "Direct Booking"]
            default_companies = ["Individual", "Corporate"]
            
            with pd.ExcelWriter(FILE_PATHS['dropdown']) as writer:
                pd.DataFrame({"Agent_Name": default_agents}).to_excel(writer, sheet_name="Agents", index=False)
                pd.DataFrame({"Company_Name": default_companies}).to_excel(writer, sheet_name="Companies", index=False)
            
            return default_agents, default_companies
        
        xl = pd.ExcelFile(FILE_PATHS['dropdown'])
        agents = xl.parse("Agents")["Agent_Name"].dropna().unique().tolist()
        companies = xl.parse("Companies")["Company_Name"].dropna().unique().tolist()

        return ["NHR"] + [a for a in agents if a != "NHR"], companies

    except Exception as e:
        st.error(f"Error loading dropdown data: {e}")
        return ["NHR"], ["Individual"]

def load_booking_data():
    """Load all booking-related data with error handling"""
    try:
        # Initialize empty DataFrames with required columns
        booking_cols = [
            'Booking_ID', 'check_in', 'check_out', 'Guest_Name', 'Contact',
            'Plan', 'Agent', 'Company', 'Status', 'Remark'
        ]
        rooms_cols = ['Booking_ID', 'Room_Type', 'Qty', 'Rate']
        advances_cols = ['Booking_ID', 'Advance_Amount', 'Advance_Date', 'Advance_Mode']

        booking_df = pd.DataFrame(columns=booking_cols)
        rooms_df = pd.DataFrame(columns=rooms_cols)
        advances_df = pd.DataFrame(columns=advances_cols)

        # Load data if files exist
        if os.path.exists(FILE_PATHS['booking']):
            booking_df = pd.read_csv(FILE_PATHS['booking'])
            for col in booking_cols:
                if col not in booking_df.columns:
                    booking_df[col] = ""

        if os.path.exists(FILE_PATHS['rooms']):
            rooms_df = pd.read_csv(FILE_PATHS['rooms'])
            for col in rooms_cols:
                if col not in rooms_df.columns:
                    rooms_df[col] = ""

        if os.path.exists(FILE_PATHS['advances']):
            advances_df = pd.read_csv(FILE_PATHS['advances'])
            for col in advances_cols:
                if col not in advances_df.columns:
                    advances_df[col] = ""

        return booking_df, rooms_df, advances_df

    except Exception as e:
        st.error(f"Error loading booking data: {e}")
        return pd.DataFrame(columns=booking_cols), pd.DataFrame(columns=rooms_cols), pd.DataFrame(columns=advances_cols)

# ==============================================
# STREAMLIT APP SETUP
# ==============================================
st.set_page_config(layout="wide", page_title="Resort Booking System")
st.title("Nature Heritage Resort - Booking Management")

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > input, .stSelectbox > div > div, 
    .stNumberInput > div > input, .stDateInput > div > input {
        font-size: 16px !important;
    }
    .stDataFrame {
        font-size: 14px;
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
tabs = st.tabs(["📅 Booking Calendar", "📝 New Booking", "📂 Manage Bookings"])

# ==============================================
# TAB 1: BOOKING CALENDAR
# ==============================================
with tabs[0]:
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = datetime.today().month
        st.session_state.calendar_year = datetime.today().year

    # Navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous Month", key="prev_month"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()

    with col2:
        month_name = calendar.month_name[st.session_state.calendar_month]
        st.markdown(f"<h3 style='text-align:center'>{month_name} {st.session_state.calendar_year}</h3>", 
                   unsafe_allow_html=True)

    with col3:
        if st.button("Next Month ➡️", key="next_month"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()

    # Calendar display logic would go here...

# ==============================================
# TAB 2: NEW BOOKING
# ==============================================
with tabs[1]:
    st.subheader("Create New Booking")
    
    with st.form("new_booking_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            guest_name = st.text_input("Guest Name*").upper()
            contact = st.text_input("Contact Number*")
            check_in = st.date_input("Check-in Date*")
            check_out = st.date_input("Check-out Date*")
            nights = (check_out - check_in).days if check_out and check_in else 0
            st.text_input("Nights", value=nights, disabled=True)
            
        with col2:
            agent = st.selectbox("Agent", agent_list)
            company = st.selectbox("Company", company_list)
            plan = st.selectbox("Meal Plan", ["AP", "CP", "MAP", "EP"])
            status = st.selectbox("Status", ["CONFIRMED", "TENTATIVE"])
            remark = st.text_area("Special Requests")

        # Room selection would go here...

        submitted = st.form_submit_button("💾 Save Booking")
        if submitted:
            try:
                # Generate new booking ID
                new_id = booking_df["Booking_ID"].max() + 1 if not booking_df.empty else 1
                
                # Create booking record
                new_booking = {
                    "Booking_ID": new_id,
                    "Guest_Name": guest_name,
                    "Contact": contact,
                    "check_in": format_date(check_in),
                    "check_out": format_date(check_out),
                    "Plan": plan,
                    "Agent": agent,
                    "Company": company,
                    "Status": status,
                    "Remark": remark
                }
                
                # Save logic would go here...
                
                st.success("Booking created successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving booking: {e}")

# ==============================================
# TAB 3: MANAGE BOOKINGS
# ==============================================
with tabs[2]:
    st.subheader("Manage Existing Bookings")
    
    if 'edit_auth' not in st.session_state:
        st.session_state.edit_auth = False
    
    # Display all bookings
    if not booking_df.empty:
        st.dataframe(
            booking_df[["Booking_ID", "Guest_Name", "check_in", "check_out", "Status"]],
            use_container_width=True,
            height=400
        )
        
        # Booking selection
        selected_id = st.selectbox(
            "Select Booking to Edit",
            booking_df["Booking_ID"].unique()
        )
        
        if selected_id:
            selected_booking = booking_df[booking_df["Booking_ID"] == selected_id].iloc[0]
            
            # Password protection
            if not st.session_state.edit_auth:
                with st.form("auth_form"):
                    password = st.text_input("Enter admin password", type="password")
                    if st.form_submit_button("Authenticate"):
                        if password == PASSWORD:
                            st.session_state.edit_auth = True
                            st.rerun()
                        else:
                            st.error("Incorrect password")
            
            # Edit mode
            if st.session_state.edit_auth:
                if st.button("🔒 Lock Editing"):
                    st.session_state.edit_auth = False
                    st.rerun()
                
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        guest_name = st.text_input("Guest Name", value=selected_booking["Guest_Name"])
                        contact = st.text_input("Contact", value=selected_booking["Contact"])
                        check_in = st.date_input("Check-in", value=parse_date(selected_booking["check_in"]))
                        
                    with col2:
                        agent = st.selectbox("Agent", agent_list, index=agent_list.index(selected_booking["Agent"]) if selected_booking["Agent"] in agent_list else 0)
                        status = st.selectbox("Status", ["CONFIRMED", "TENTATIVE", "CANCELLED"], index=["CONFIRMED", "TENTATIVE", "CANCELLED"].index(selected_booking["Status"]) if selected_booking["Status"] in ["CONFIRMED", "TENTATIVE", "CANCELLED"] else 0)
                        check_out = st.date_input("Check-out", value=parse_date(selected_booking["check_out"]))
                    
                    remark = st.text_area("Remarks", value=selected_booking.get("Remark", ""))
                    
                    if st.form_submit_button("💾 Save Changes"):
                        try:
                            # Update booking
                            booking_df.loc[booking_df["Booking_ID"] == selected_id, [
                                "Guest_Name", "Contact", "check_in", "check_out",
                                "Agent", "Status", "Remark"
                            ]] = [
                                guest_name, contact, format_date(check_in), format_date(check_out),
                                agent, status, remark
                            ]
                            
                            # Save to CSV
                            booking_df.to_csv(FILE_PATHS['booking'], index=False)
                            
                            st.success("Changes saved successfully!")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error saving changes: {e}")
    else:
        st.warning("No bookings found in the system")

# ==============================================
# FILE BACKUP FUNCTIONALITY
# ==============================================
def backup_data():
    """Create timestamped backups of all data files"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for file_type, file_path in FILE_PATHS.items():
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{timestamp}"
                shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        st.error(f"Backup failed: {e}")
        return False