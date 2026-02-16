import streamlit as st
import sqlite3

# 1. Setup SQL Database
conn = sqlite3.connect('tasks_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              title TEXT, employee TEXT, duration TEXT, 
              progress INTEGER, details TEXT)''')
conn.commit()

st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📂 My-Task-Box")
    # This creates the menu you requested
    page = st.radio("Menu", ["Projects", "Tasks", "Reports", "Chats/Discussions"])
    st.divider()
    st.caption("Logged in as: Admin")

# Session State for task clicking (kept from previous version)
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None

# --- NAVIGATION LOGIC ---

if page == "Tasks":
    # --- IF A TASK IS CLICKED (DETAIL VIEW) ---
    if st.session_state.selected_task:
        task_id = st.session_state.selected_task
        task = c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        
        if st.button("⬅️ Back to Task Board"):
            st.session_state.selected_task = None
            st.rerun()

        st.title(f"📌 {task[1]}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duration", task[3])
            st.write(f"**Assigned to:** {task[2]}")
        with col2:
            st.write(f"**Progress:** {task[4]}%")
            st.progress(task[4] / 100)
        
        st.write("### Notes")
        st.info(task[5])

    # --- MAIN TASKS DASHBOARD ---
    else:
        st.title("✅ Tasks")
        with st.expander("➕ Create New Task"):
            t_title = st.text_input("Task Name")
            t_emp = st.text_input("Employee Name")
            t_dur = st.text_input("Duration")
            t_prog = st.slider("Progress %", 0, 100, 0)
            t_desc = st.text_area("Details")
            
            if st.button("Create Task"):
                c.execute('INSERT INTO tasks (title, employee, duration, progress, details) VALUES (?,?,?,?,?)', 
                          (t_title, t_emp, t_dur, t_prog, t_desc))
                conn.commit()
                st.rerun()

        data = c.execute('SELECT id, title, employee FROM tasks').fetchall()
        cols = st.columns(3)
        for index, row in enumerate(data):
            with cols[index % 3]:
                st.write(f"**{row[1]}**")
                with st.container(border=True):
                    st.write(f"👤 {row[2]}")
                    if st.button("View Details", key=f"btn_{row[0]}"):
                        st.session_state.selected_task = row[0]
                        st.rerun()

elif page == "Projects":
    st.title("🏗️ Projects")
    st.write("This area will show your high-level project goals.")
    st.info("Coming Soon: Group your tasks into specific projects.")

elif page == "Reports":
    st.title("📊 Reports")
    st.write("Analytics and progress charts for the team.")
    # Quick example of a report:
    st.bar_chart({"Tasks": [len(data)]}) 

elif page == "Chats/Discussions":
    st.title("💬 Chats")
    st.write("Team discussion board.")
    st.text_input("Type a message to the team...")
