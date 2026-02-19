import streamlit as st
import sqlite3

# --- 1. DATABASE SETUP (v6) ---
conn = sqlite3.connect('tasks_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (id INTEGER PRIMARY KEY, name TEXT, duration TEXT, 
              phase TEXT, progress INTEGER, details TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS project_chat 
             (id INTEGER PRIMARY KEY, project_id INTEGER, user TEXT, msg TEXT)''')
conn.commit()

# --- 2. PAGE CONFIG & BEIGE/NAVY/PINK THEME ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    /* 1. Main Background and Text Color */
    .stApp {
        background-color: #F5F5DC; /* Beige */
    }
    
    /* 2. Global Text Color (Navy Blue) */
    html, body, [class*="st-"], p, div, label {
        color: #000080 !important; /* Navy Blue */
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.8 !important; /* Extra space to prevent overlap */
    }

    /* 3. Titles (Navy Blue & Spaced) */
    h1, h2, h3 {
        color: #000080 !important;
        margin-bottom: 20px !important;
        margin-top: 10px !important;
    }

    /* 4. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #EFEFDB !important; /* Slightly darker beige */
        border-right: 1px solid #000080;
    }

    /* 5. Pink Highlight for Selected Menu Item */
    /* This targets the radio button container to look like a list */
    div[data-testid="stSidebarNav"] {
        padding-top: 20px;
    }
    
    /* Removing the radio circles and making it a list */
    div[data-testid="stWidgetLabel"] { display: none; }
    
    .st-emotion-cache-1647ite { 
        background-color: transparent !important; 
    }

    /* Custom Pink Highlight for the active selection */
    div.st-ae [data-testid="stMarkdownContainer"] {
        color: #000080;
    }
    
    /* Target the selected radio option */
    div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: transparent;
        padding: 10px;
        border-radius: 5px;
        width: 100%;
    }

    div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #FFC0CB !important; /* Pink Highlight */
        color: white !important;
        font-weight: bold;
    }

    /* 6. Fix for Overlapping Columns */
    div[data-testid="stColumn"] {
        padding: 25px !important;
        background-color: rgba(255, 255, 255, 0.3); /* Soft white overlay */
        border-radius: 10px;
        margin: 10px;
    }

    /* 7. Chat Box Portrait Style */
    .chat-box {
        background-color: white;
        border: 2px solid #000080;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    # Using a radio but CSS hides the circles to make it look like a menu list
    page = st.radio("Navigation", [
        "🏗️ Projects", "👥 Employees", "✅ Tasks", "📄 Licenses & Permits",
        "🏦 Bonds", "💰 Payroll", "👔 HR", "🔍 Exploration",
        "🏢 Commercial", "🏠 Residential"
    ])
    st.divider()

# Session State
if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

# --- 4. NAVIGATION LOGIC ---

if page == "🏗️ Projects":
    if st.session_state.active_project_id is None:
        st.title("Projects Dashboard")
        
        with st.expander("➕ Create New Project"):
            p_name = st.text_input("Project Name")
            p_dur = st.text_input("Estimated Duration")
            p_phase = st.text_input("Current Phase")
            p_prog = st.slider("Phase Progress %", 0, 100, 0)
            if st.button("Launch Project"):
                if p_name:
                    c.execute('INSERT INTO projects (name, duration, phase, progress) VALUES (?,?,?,?)', 
                              (p_name, p_dur, p_phase, p_prog))
                    conn.commit()
                    st.rerun()

        st.divider()
        
        projs = c.execute('SELECT id, name, phase, progress FROM projects').fetchall()
        cols = st.columns(3) # Wider columns to prevent overlap
        for i, p in enumerate(projs):
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {p[1]}")
                    st.write(f"Phase: {p[2]}")
                    st.progress(p[3]/100)
                    if st.button("Open Details", key=f"p_{p[0]}"):
                        st.session_state.active_project_id = p[0]
                        st.rerun()
    else:
        # PROJECT DETAIL VIEW
        p_id = st.session_state.active_project_id
        p_data = c.execute('SELECT * FROM projects WHERE id = ?', (p_id,)).fetchone()
        
        st.title(f"📍 {p_data[1]}")
        
        col_left, col_right = st.columns([1, 1])

        with col_left:
            if st.button("⬅️ Back to Dashboard"):
                st.session_state.active_project_id = None
                st.rerun()
            
            st.subheader("📋 Job Details")
            st.write(f"⏱️ **Est. Duration:** {p_data[2]}")
            st.write(f"🏗️ **Current Phase:** {p_data[3]}")
            st.write(f"📈 **Phase Progress:** {p_data[4]}%")
            st.progress(p_data[4]/100)
            
            st.divider()
            st.write("**Next Phases:** TBD")
            st.write("**Employees Involved:** Admin")

        with col_right:
            st.subheader("💬 Project Chat")
            chat_box = st.container(height=450, border=True)
            msgs = c.execute('SELECT user, msg FROM project_chat WHERE project_id = ?', (p_id,)).fetchall()
            for m in msgs:
                chat_box.write(f"**{m[0]}**: {m[1]}")
            
            chat_input = st.text_input("Message", key="msg_input")
            if st.button("Send"):
                if chat_input:
                    c.execute('INSERT INTO project_chat (project_id, user, msg) VALUES (?,?,?)', (p_id, "Admin", chat_input))
                    conn.commit()
                    st.rerun()

elif page == "👥 Employees":
    st.title("Employee Directory")
    new_emp = st.text_input("Name")
    if st.button("Add"):
        c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
        conn.commit()
        st.rerun()
    emps = c.execute('SELECT name FROM employees').fetchall()
    for e in emps:
        st.write(f"• {e[0]}")

else:
    st.title(page)
    st.write(f"Welcome to the {page} section.")
