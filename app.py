import streamlit as st
import sqlite3

# 1. Setup SQL Database (v3 to ensure new columns exist)
conn = sqlite3.connect('tasks_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              title TEXT, 
              employee TEXT, 
              duration TEXT, 
              progress INTEGER, 
              details TEXT)''')
conn.commit()

st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# Session State: This remembers which task you clicked on
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None

# --- PAGE 1: THE DETAIL VIEW ---
if st.session_state.selected_task:
    task_id = st.session_state.selected_task
    task = c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.selected_task = None
        st.rerun()

    st.title(f"Task: {task[1]}") # Title
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated Duration", task[3])
        st.write(f"**Assigned to:** {task[2]}")
    with col2:
        st.write(f"**Progress:** {task[4]}%")
        st.progress(task[4] / 100)
    
    st.write("### Notes/Details")
    st.write(task[5])
    
    # Simple Delete button inside the detail page
    if st.button("🗑️ Delete Task", type="primary"):
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        st.session_state.selected_task = None
        st.rerun()

# --- PAGE 2: THE MAIN DASHBOARD ---
else:
    st.title("🚀 My-Task-Box Dashboard")

    with st.expander("➕ Create New Task"):
        t_title = st.text_input("Task Name")
        t_emp = st.text_input("Employee Name")
        t_dur = st.text_input("Duration (e.g. 3 days)")
        t_prog = st.slider("Progress %", 0, 100, 0)
        t_desc = st.text_area("Detailed Description")
        
        if st.button("Create Task"):
            c.execute('INSERT INTO tasks (title, employee, duration, progress, details) VALUES (?,?,?,?,?)', 
                      (t_title, t_emp, t_dur, t_prog, t_desc))
            conn.commit()
            st.rerun()

    st.divider()

    # Show Tasks in a Grid
    data = c.execute('SELECT id, title, employee FROM tasks').fetchall()
    
    # Create 3 columns for the "Square Boxes"
    cols = st.columns(3)
    for index, row in enumerate(data):
        with cols[index % 3]: # This puts cards in a 3-column grid
            st.write(f"**{row[1]}**") # Task Title on top
            # The "Square Box"
            with st.container(border=True):
                st.write(f"👤 {row[2]}")
                if st.button("View Details", key=f"btn_{row[0]}"):
                    st.session_state.selected_task = row[0]
                    st.rerun()
