import streamlit as st
import sqlite3
import datetime
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Our Love Hub 💕",
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Database Setup ---
DB_NAME = "love_grievances.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            title TEXT NOT NULL,
            details TEXT,
            category TEXT,
            severity TEXT,
            status TEXT DEFAULT '💖 Open',
            resolution_notes TEXT,
            submitted_by TEXT DEFAULT 'My Love ❤️',
            target_resolution_date DATE
        )
    """)
    conn.commit()
    conn.close()

# Initialize database and tables
create_tables()

# --- Helper Functions ---
def add_grievance(title, details, category, severity, target_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO grievances (title, details, category, severity, target_resolution_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, details, category, severity, target_date, '💖 Open'))
    conn.commit()
    conn.close()

def get_all_grievances():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, strftime('%Y-%m-%d %H:%M', timestamp) as submitted_on, title, details, category, severity, status, resolution_notes, target_resolution_date FROM grievances ORDER BY timestamp DESC")
    grievances = cursor.fetchall()
    conn.close()
    return grievances

def update_grievance_status(grievance_id, new_status, resolution_notes=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE grievances
        SET status = ?, resolution_notes = ?
        WHERE id = ?
    """, (new_status, resolution_notes, grievance_id))
    conn.commit()
    conn.close()

def delete_grievance(grievance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grievances WHERE id = ?", (grievance_id,))
    conn.commit()
    conn.close()

# --- App Styling (CSS focused on selectbox and chart visibility) ---
st.markdown("""
<style>
    :root {
        --bg-main: #FFF0F5; 
        --bg-sidebar: #FFE4E1; 
        --bg-widget: #FFFFFF; 
        --bg-widget-hover: #FFF8FA; 
        --bg-table-header: #FFF0F5; 
        
        --text-dark: #331E22; /* Main dark text for high contrast */
        --text-medium: #4A271E; /* Slightly lighter dark, but still high contrast */
        --text-light: #FFFFFF; 
        --text-placeholder: #A09094; 

        --accent-pink-strong: #D63384; 
        --accent-pink-medium: #FF69B4; /* Hot Pink */
        --accent-pink-light: #FFC0CB; /* Pink */
        
        --border-color: var(--accent-pink-medium); 
        --border-color-focus: var(--accent-pink-strong); 

        --success-bg: #E6FFFA;
        --success-text: #004D40; 
        --success-border: #198754;
        
        --warning-bg: #FFF3CD;
        --warning-text: #664D03; 
        --warning-border: #FFC107;

        --error-bg: #F8D7DA;
        --error-text: #58151C; 
        --error-border: #DC3545;
    }

    body, .stApp {
        background-color: var(--bg-main) !important; 
        color: var(--text-dark) !important; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }

    /* Main Page Title (e.g., "Our Love Stats Dashboard") */
    .stApp > div > .main .block-container h1 { 
        color: var(--accent-pink-strong) !important; 
        font-weight: 600;
        font-size: 2.0rem; 
    }
    /* All other headers (h2-h6), including st.subheader like "Status Breakdown:" */
    .stApp .main .block-container h2,
    .stApp .main .block-container h3, 
    .stApp .main .block-container h4,
    .stApp .main .block-container h5,
    .stApp .main .block-container h6 {
        color: var(--text-dark) !important; /* Ensure subheaders are dark */
        font-weight: 600;
    }

    /* --- SIDEBAR STYLES --- */
    div[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important; 
        border-right: 2px solid var(--accent-pink-light) !important;
        padding: 1rem !important;
    }
    /* Sidebar main title */
    div[data-testid="stSidebar"] h1 { 
        color: var(--accent-pink-strong) !important; 
    }
    /* ALL other text in sidebar: radio labels, captions, markdown paragraphs */
    div[data-testid="stSidebar"] p, /* Catches markdown <p> tags like "Made with heaps..." and the emoji <p> */
    div[data-testid="stSidebar"] li,
    div[data-testid="stSidebar"] label, /* General labels */
    div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p, /* More specific for markdown paragraphs */
    div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li, 
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label span, /* Radio button option text */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label small /* Radio captions */
    {
        color: var(--text-dark) !important; 
        background-color: transparent !important; 
    }
    /* Selected radio button option text (make it pop with accent color) */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] input:checked + div span { 
        color: var(--accent-pink-strong) !important;
        font-weight: 600 !important;
    }
    /* Hover effect for radio button text */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover > div > span {
        color: var(--accent-pink-medium) !important; 
    }


    /* --- FORM WIDGET LABEL STYLES (Main Content) --- */
    .main .stTextInput label,
    .main .stTextArea label,
    .main .stDateInput label,
    .main .stSelectbox label, 
    .main .stForm label { 
        color: var(--text-dark) !important; 
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.2rem !important; 
        display: block !important;
    }

    /* --- INPUT WIDGET STYLES (Text, Text Area, Date) --- */
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input {
        background-color: var(--bg-widget) !important; 
        color: var(--text-dark) !important; 
        border: 1px solid var(--border-color) !important; 
        border-radius: 6px !important; 
        padding: 10px !important; 
        line-height: 1.5; 
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus {
        border-color: var(--border-color-focus) !important; 
        box-shadow: 0 0 0 2px var(--accent-pink-light) !important; 
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--text-placeholder) !important;
        opacity: 1; 
    }

    /* --- SELECTBOX STYLES --- */
    .stSelectbox div[data-baseweb="select"] > div:first-child {
        background-color: var(--bg-widget) !important; 
        border: 1px solid var(--border-color) !important; 
        border-radius: 6px !important; 
        padding: 10px !important; 
        line-height: 1.5; 
        display: flex; 
        align-items: center; 
    }
    .stSelectbox div[data-baseweb="select"] div[class*="placeholder"] {
        color: var(--text-placeholder) !important; 
        margin: 0 !important; 
        padding: 0 !important; 
        width: 100%; 
    }
    .stSelectbox div[data-baseweb="select"] > div:first-child > div:first-child {
        color: var(--text-dark) !important; 
        margin: 0 !important; 
        padding: 0 !important; 
        width: 100%; 
        background-color: transparent !important; 
    }
    .stSelectbox div[data-baseweb="select"] > div:first-child > div:first-child span,
    .stSelectbox div[data-baseweb="select"] > div:first-child > div:first-child p {
        color: var(--text-dark) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div:first-child:focus-within {
        border-color: var(--border-color-focus) !important; 
        box-shadow: 0 0 0 2px var(--accent-pink-light) !important; 
    }
    div[data-baseweb="popover"][id^="streamlit-select-"] { 
        background-color: var(--bg-widget) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
    }
    div[data-baseweb="popover"][id^="streamlit-select-"] ul[role="listbox"] {
        background-color: var(--bg-widget) !important;
        padding: 4px 0 !important;
    }
    div[data-baseweb="popover"][id^="streamlit-select-"] ul[role="listbox"] li[role="option"] {
        background-color: transparent !important;
        padding: 8px 12px !important;
        color: var(--text-dark) !important; 
    }
    div[data-baseweb="popover"][id^="streamlit-select-"] ul[role="listbox"] li[role="option"][aria-selected="true"] {
        background-color: var(--accent-pink-light) !important;
        color: var(--text-dark) !important; 
    }
    div[data-baseweb="popover"][id^="streamlit-select-"] ul[role="listbox"] li[role="option"]:hover {
        background-color: var(--bg-widget-hover) !important;
        color: var(--text-dark) !important;
    }

    /* --- METRIC WIDGET STYLING --- */
    .stApp div[data-testid="stMetric"] { 
        background-color: transparent !important; 
        padding: 0.5rem; 
        border: none !important; 
    }
    .stApp div[data-testid="stMetric"] label[data-testid="stMetricLabel"] { 
        color: var(--text-dark) !important; 
        font-weight: 500 !important; 
        margin-bottom: 0.2rem !important; 
        font-size: 1rem !important; 
        display: block; 
        line-height: 1.3;
    }
    .stApp div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
        color: var(--text-dark) !important; 
        font-size: 2.5rem !important; 
        font-weight: 700 !important; 
        line-height: 1.1 !important; 
        padding-top: 0.1rem; 
    }
    .stApp div[data-testid="stMetric"] div[data-testid="stMetricDelta"] { 
        color: var(--text-medium) !important; 
        font-weight: 500 !important;
        font-size: 0.85rem; 
    }


    /* --- BUTTONS --- */
    .stButton>button { background-color: var(--accent-pink-strong) !important; color: var(--text-light) !important; border: 1px solid var(--accent-pink-strong) !important; border-radius: 8px !important; padding: 10px 20px !important; font-weight: 500 !important; transition: background-color 0.2s ease, transform 0.2s ease, border-color 0.2s ease; }
    .stButton>button:hover { background-color: #C02A72 !important; border-color: #A3205F !important; transform: scale(1.02); }
    .stButton>button:active { background-color: #A3205F !important; transform: scale(0.98); }
    .stButton>button[kind="secondary"] { background-color: var(--bg-widget) !important; color: var(--accent-pink-strong) !important; border: 1px solid var(--accent-pink-medium) !important; }
    .stButton>button[kind="secondary"]:hover { background-color: var(--bg-widget-hover) !important; border-color: var(--accent-pink-strong) !important; }

    /* --- CHART STYLING --- */
    div[data-testid="stVegaLiteChart"], 
    .stVegaLiteChart { 
        background-color: var(--bg-widget) !important; 
        border-radius: 8px !important;
        padding: 1rem !important; 
        border: 1px solid var(--border-color) !important; 
    }
    /* Text within stInfo inside chart area */
    div[data-testid="stVegaLiteChart"] div[data-testid="stInfo"],
    .stVegaLiteChart div[data-testid="stInfo"] {
        background-color: var(--bg-widget-hover) !important; 
        border-radius: 6px; 
        padding: 0.75rem 1rem !important; 
    }
    div[data-testid="stVegaLiteChart"] div[data-testid="stInfo"] p, 
    .stVegaLiteChart div[data-testid="stInfo"] p {
        color: var(--text-dark) !important; 
        margin: 0 !important; 
    }
    .vega-embed summary, .vega-embed details {
        color: var(--text-dark) !important;
    }


    /* --- OTHER ELEMENTS (DataFrames, Expanders, Alerts, Footer) --- */
    .stDataFrame, .stTable { border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--bg-widget); }
    .stDataFrame th, .stTable th { background-color: var(--bg-table-header) !important; color: var(--text-dark) !important; font-weight: 600; border-bottom: 2px solid var(--accent-pink-medium); padding: 10px 8px; }
    .stDataFrame td, .stTable td { color: var(--text-dark); border-bottom: 1px solid var(--accent-pink-light); padding: 8px; }
    .stExpander { border: 1px solid var(--border-color) !important; border-radius: 8px !important; background-color: var(--bg-widget) !important; margin-bottom: 1rem; }
    .stExpander header { background-color: var(--bg-sidebar) !important; color: var(--text-dark) !important; border-radius: 7px 7px 0 0 !important; padding: 0.75rem 1rem !important; font-weight: 500; }
    .stExpander header:hover { background-color: var(--accent-pink-light) !important; color: var(--text-dark) !important; }
    .stExpander div[role="button"] p { color: var(--text-dark) !important; }
    .stExpander div[data-testid="stExpanderDetails"] { color: var(--text-dark); padding: 1rem; border-top: 1px solid var(--border-color); }
    div[data-testid="stAlert"] { border-radius: 6px; padding: 0.8rem 1rem; margin-bottom: 1rem; border-width: 1px; border-style: solid; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-1uvn9cz"] { background-color: var(--success-bg) !important; color: var(--success-text) !important; border-color: var(--success-border) !important; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-1uvn9cz"] p { color: var(--success-text) !important; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-j6nsw4"] { background-color: var(--warning-bg) !important; color: var(--warning-text) !important; border-color: var(--warning-border) !important; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-j6nsw4"] p { color: var(--warning-text) !important; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-1wmy9hl"] { background-color: var(--error-bg) !important; color: var(--error-text) !important; border-color: var(--error-border) !important; }
    div[data-testid="stAlert"][data-baseweb="alert"][role="alert"][class*="st-emotion-cache-1wmy9hl"] p { color: var(--error-text) !important; }
    .footer-text p { text-align: center; color: var(--text-medium) !important; font-size: 0.9rem; padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# --- Sidebar for Navigation and Info ---
st.sidebar.title("💖 Love Hub Navigation 💖") 
st.sidebar.markdown("---")
app_mode = st.sidebar.radio(
    "Sweetheart, what shall we do?", 
    ["💌 Submit New Grievance", "📝 View & Manage Grievances", "📊 Our Love Stats"],
    captions=["Share your heart's whispers.", "See what we're working on.", "A peek at our love's journey." , "Miss. V Sai Keerthi."] # Extra caption added by user
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with heaps of love, for my one and only! 🥰") 
st.sidebar.markdown("<p style='text-align: center; font-size: 50px;'>💕</p>", unsafe_allow_html=True)


# --- Main App Logic ---

if app_mode == "💌 Submit New Grievance":
    st.header("💌 Share Your Heart's Whispers...")
    st.markdown("It's always okay to share what's on your mind, my love. I'm here to listen and make things even more wonderful between us. 💕")

    with st.form("grievance_form", clear_on_submit=True):
        title = st.text_input("💖 What's the little (or big) thing, darling?", placeholder="E.g., Missing our daily good morning texts")
        details = st.text_area("💬 Tell me more about it...", placeholder="E.g., It makes my day start a little brighter when I hear from you first thing!", height=150)
        category_options = ["Quality Time 🕰️", "Communication 🗣️", "Chores & Responsibilities 🧹", "Appreciation & Affection 🥰", "Future Plans 🌟", "Little Annoyances 🤏", "Date Night Ideas ✨", "Other Sweet Nothings 🤔"]
        category = st.selectbox("🏷️ What's it related to?", category_options, placeholder="Choose a category...", index=None) 
        severity_options = ["🥺 Mild Heartache", "😥 Needs Prompt Attention", "😭 Emergency Snuggle Protocol!"]
        severity = st.selectbox("💔 How much does it tug at your heartstrings?", severity_options, placeholder="Select severity...", index=None) 
        
        today = datetime.date.today()
        target_date = st.date_input("🗓️ When would you ideally like us to resolve this by, precious?", min_value=today, value=today + datetime.timedelta(days=7))

        submitted = st.form_submit_button("Send with All My Love 💌")

        if submitted:
            if not title:
                st.error("Oops! Please add a title for your whisper, my love. ❤️")
            elif not category: 
                st.error("Please choose a category for your whisper, sweetheart. 🏷️")
            elif not severity: 
                st.error("Please select how much this tugs at your heartstrings, my love. 💔")
            else:
                add_grievance(title, details, category, severity, target_date)
                st.success(f"'{title}' has been lovingly noted. I'll look into it right away, sweetheart! ✨")
                st.balloons()

elif app_mode == "📝 View & Manage Grievances":
    st.header("📝 Our Heart's Ledger") 
    st.markdown("Here's everything we're nurturing together, to make our love story even more beautiful. 💪💖")

    grievances = get_all_grievances()

    if not grievances:
        st.info("No love notes (grievances) yet! Our hearts are in perfect sync. 🥰 Or, feel free to share if something comes up, my dear!")
    else:
        df = pd.DataFrame(grievances, columns=['ID', 'Submitted On', 'Title', 'Details', 'Category', 'Severity', 'Status', 'Resolution Notes', 'Target Date'])
        
        st.subheader("All Our Love Notes:") 

        for index, row in df.iterrows():
            expander_title = f"{row['Status']} - **{row['Title']}** (Severity: {row['Severity']}) - Submitted: {row['Submitted On']}"
            with st.expander(expander_title): 
                st.markdown(f"**Category:** {row['Category']}")
                st.markdown(f"**Details:**\n\n{row['Details']}")
                st.markdown(f"**Target Resolution Date:** {row['Target Date']}")
                st.markdown(f"**Current Status:** {row['Status']}")
                current_resolution_notes = row['Resolution Notes'] if row['Resolution Notes'] else ""
                
                st.markdown("---")
                st.markdown("#### Update This Note, My Love:") 
                
                col1, col2 = st.columns([3,1]) 
                with col1:
                    status_options = ["💖 Open", "💬 We're Talking", "🛠️ Working on it", "✅ Resolved with Love!", "⏳ Pending Apology Cuddles"]
                    try:
                        current_status_index = status_options.index(row['Status'])
                    except ValueError:
                        current_status_index = 0 

                    new_status = st.selectbox(
                        "Update Status:", 
                        status_options,
                        index=current_status_index,
                        key=f"status_{row['ID']}"
                    )
                    resolution_notes_update = st.text_area(
                        "My Thoughts/Our Resolution:", 
                        value=current_resolution_notes,
                        key=f"notes_{row['ID']}",
                        placeholder="How I'm making it better / Our beautiful resolution...",
                        height=100
                    )
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True) 
                    if st.button("Save Update 💖", key=f"update_{row['ID']}", use_container_width=True):
                        update_grievance_status(row['ID'], new_status, resolution_notes_update)
                        st.success(f"Note '{row['Title']}' updated! We're amazing together! 🎉")
                        st.rerun() 

                    st.markdown("<br>", unsafe_allow_html=True) 
                    if st.button("Delete Note 🗑️", key=f"delete_{row['ID']}", type="secondary", use_container_width=True):
                        delete_grievance(row['ID'])
                        st.warning(f"Note '{row['Title']}' deleted. Hope it was resolved with oceans of love! ❤️")
                        st.rerun()

elif app_mode == "📊 Our Love Stats":
    st.header("📊 Our Love Stats Dashboard") 
    st.markdown("A little peek at how wonderfully we're growing, together. Every step forward is a testament to our love! 💑")

    grievances = get_all_grievances()
    if not grievances: 
        st.info("No grievances submitted yet to show any stats. Our love story is just beginning! 🕊️")
    else:
        df = pd.DataFrame(grievances, columns=['ID', 'Submitted On', 'Title', 'Details', 'Category', 'Severity', 'Status', 'Resolution Notes', 'Target Date'])

        total_grievances = len(df)
        all_statuses = ["💖 Open", "💬 We're Talking", "🛠️ Working on it", "✅ Resolved with Love!", "⏳ Pending Apology Cuddles"]
        status_counts = df['Status'].value_counts().reindex(all_statuses, fill_value=0)
        
        resolved_grievances = status_counts.get("✅ Resolved with Love!", 0)
        ongoing_conversations = status_counts.loc[status_counts.index != "✅ Resolved with Love!"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Love Notes 💌", total_grievances)
        col2.metric("Resolved with Love ✅", resolved_grievances)
        col3.metric("Ongoing Conversations 💬", ongoing_conversations)


        st.markdown("---")
        st.subheader("Status Breakdown:") 
        if not status_counts.empty and status_counts.sum() > 0: 
            st.bar_chart(status_counts, color="#FF69B4") # Direct Hex for --accent-pink-medium
        else:
            st.info("No status data to display in the chart yet, my love! Let's fill our hub with more notes. 📝")

        st.markdown("---")
        st.subheader("Category Insights:") 
        if 'Category' in df.columns and not df['Category'].dropna().empty:
            category_counts = df['Category'].value_counts()
            if not category_counts.empty:
                 st.bar_chart(category_counts, color="#FFC0CB") # Direct Hex for --accent-pink-light
            else: 
                st.info("No category data to display in the chart yet, darling! What are our love notes about? 🤔")
        else:
            st.info("No category data to display in the chart yet, darling! What are our love notes about? 🤔")

# --- Footer ---
st.markdown("---")
st.markdown("<div class='footer-text'><p>Remember Sai Keerthi, communication is the melody of our happy hearts. I love you more each day! ❤️, Made By Rahul B Only for Sai Kee</p></div>", unsafe_allow_html=True)
