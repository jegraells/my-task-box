import streamlit as st
import sqlite3

# 1. Setup SQL Database
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, employee TEXT, update_text TEXT)')
conn.commit()

st.set_page_config(page_title="My-Task-Box", layout="centered")
st.title("🚀 My-Task-Box")

# 2. Add New Progress
with st.expander("➕ Add New Progress Update"):
    name = st.text_input("Your Name")
    progress = st.text_area("What did you work on?")
    if st.button("Share with Team"):
        if name and progress:
            c.execute('INSERT INTO tasks (employee, update_text) VALUES (?, ?)', (name, progress))
            conn.commit()
            st.rerun() # Refresh the app to show the new task

# 3. Show Task Board with Delete Buttons
st.header("📋 Team Progress")
data = c.execute('SELECT id, employee, update_text FROM tasks ORDER BY id DESC').fetchall()

for row in data:
    task_id = row[0]
    employee_name = row[1]
    task_content = row[2]
    
    # Create a nice box for each task
    with st.container(border=True):
        st.write(f"**{employee_name}**: {task_content}")
        
        # This button uses the unique SQL 'id' to delete the right task
        if st.button(f"🗑️ Delete", key=f"delete_{task_id}"):
            c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            st.rerun() # Refresh the app to show it's gone
