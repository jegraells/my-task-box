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

# --- 2. PAGE CONFIG & DESIGN ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    /* 1. Global Background (Beige) */
    .stApp {
        background-color: #F5F5DC;
    }
    
    /* 2. Global Text Color (Charcoal Navy Blend) */
    html, body, [class*="st-"], p, div, label {
        color: #1e293b !important; 
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        font-size: 14px;
        line-height: 1.8;
    }

    /* 3. Titles */
    h1, h2, h3 {
        color: #0f172a !important; 
        font-weight: 600 !important;
        margin-bottom: 1.5rem !important;
    }

    /* 4. Sidebar Styling - Ensuring visibility */
    [data-testid="stSidebar"] {
        background-color: #EFEFDB !important;
        border-right: 1px solid #cbd5e1;
    }

    /* HIDE RADIO BUTTON CIRCLES ONLY - KEEP TEXT VISIBLE */
    [data-testid="stWidgetLabel"] { display: none; }
    
    div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
        display: none !important; 
    }

    /* 5. MENU INTERACTION (Hover & Click) */
    div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: transparent;
        padding: 12px 20px !important;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s ease;
        cursor: pointer;
        border: none;
        display: block !important;
    }

    /* Ensure the text inside the label is dark navy and visible */
    div[role="radiogroup"] > label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
        color: #0f172a !important; 
        font-weight: 500 !important;
        font-size: 14px !important;
    }

    /* Mouse Hover Reaction */
    div[role="radiogroup"] > label[data-baseweb="radio"]:hover {
        background-color: rgba(30, 41, 59, 0.08) !important;
        padding-left: 25px !important; 
    }

    /* Pink Highlight when Selected */
    div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #FFC0CB !important; 
    }
    
    div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) p {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 6. Spacing Fix for Columns */
    div[data-testid="stColumn"] {
        padding: 2rem !important;
        background-color: rgba(255, 255, 255, 0.4); 
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("📂 My-Task-Box")
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
        cols = st.columns(3)
        for i, p in enumerate(projs):
            with cols[i % 3]:
                with st.container(border=True):
                    st.write(f"### {p[1]}")
                    st.write(f"**Phase:** {p[2]}")
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
            
            chat_input = st.text_input("Message", placeholder="Type here...", key="msg_input")
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
    st.write(f"Section for {page} is under construction.")
