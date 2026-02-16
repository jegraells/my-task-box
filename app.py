import streamlit as st
import sqlite3

# 1. Database Setup (v4)
conn = sqlite3.connect('tasks_v4.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT)')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (id INTEGER PRIMARY KEY, name TEXT, lead TEXT, description TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY, title TEXT, employee TEXT, 
              project_id INTEGER, duration TEXT, progress INTEGER, details TEXT)''')
conn.commit()

# --- GITHUB STYLE FONT CSS ---
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 13px; /* Smaller base font like GitHub */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    h1 { font-size: 16px !important; font-weight: 600 !important; } /* Titles slightly bigger */
    h2 { font-size: 14px !important; font-weight: 600 !important; }
    h3 { font-size: 13px !important; font-weight: 600 !important; }
    .stButton>button { font-size: 12px; padding: 0px 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    page = st.radio("Menu", ["Projects", "Tasks", "Employees", "Reports", "Chats"])

# --- EMPLOYEES PAGE ---
if page == "Employees":
    st.title("👥 Employee Directory")
    with st.expander("➕ Add New Employee"):
        new_emp = st.text_input("Name")
        if st.button("Add"):
            c.execute('INSERT INTO employees (name) VALUES (?)', (new_emp,))
            conn.commit()
            st.rerun()
    
    emps = c.execute('SELECT * FROM employees').fetchall()
    for emp in emps:
        st.write(f"• {emp[1]}")

# --- PROJECTS PAGE ---
elif page == "Projects":
    st.title("🏗️ Projects")
    with st.expander("➕ Create New Project"):
        p_name = st.text_input("Project Name")
        # Pull names from Employees table for the dropdown
        emp_list = [row[1] for row in c.execute('SELECT name FROM employees').fetchall()]
        p_lead = st.selectbox("Assign Project Lead", ["Select Lead"] + emp_list)
        p_desc = st.text_area("Project Goal")
        
        if st.button("Launch Project"):
            c.execute('INSERT INTO projects (name, lead, description) VALUES (?,?,?)', (p_name, p_lead, p_desc))
            conn.commit()
            st.rerun()

    projs = c.execute('SELECT * FROM projects').fetchall()
    for p in projs:
        with st.container(border=True):
            st.write(f"**{p[1]}** (Lead: {p[2]})")
            st.caption(p[3])

# --- TASKS PAGE (Updated for Projects) ---
elif page == "Tasks":
    st.title("✅ Tasks")
    # State management for detail view
    if 'selected_task' not in st.session_state: st.session_state.selected_task = None
    
    if st.session_state.selected_task:
        # (Detail view code remains same as before...)
        if st.button("⬅️ Back"): st.session_state.selected_task = None; st.rerun()
    else:
        with st.expander("➕ Create Task"):
            t_title = st.text_input("Task Title")
            proj_list = {row[1]: row[0] for row in c.execute('SELECT name, id FROM projects').fetchall()}
            t_proj = st.selectbox("Link to Project", list(proj_list.keys()))
            t_emp = st.selectbox("Assign Employee", emp_list if 'emp_list' in locals() else [])
            # (Other inputs...)
            if st.button("Save Task"):
                c.execute('INSERT INTO tasks (title, employee, project_id) VALUES (?,?,?)', 
                          (t_title, t_emp, proj_list[t_proj]))
                conn.commit()
                st.rerun()
        # (Grid view code same as before...)

# (Other placeholders for Reports and Chats...)
