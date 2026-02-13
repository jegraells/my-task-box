import streamlit as st
import sqlite3

# 1. Setup SQL Database
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tasks (employee TEXT, update_text TEXT)')
conn.commit()

# 2. Design the App for Phone/Desktop
st.set_page_config(page_title="Team Progress", layout="centered")
st.title("🚀 Project Management App")

# 3. Employee Input Section
with st.expander("➕ Add New Progress Update"):
    name = st.text_input("Your Name")
    progress = st.text_area("What did you work on today?")
    if st.button("Share with Team"):
        if name and progress:
            c.execute('INSERT INTO tasks (employee, update_text) VALUES (?, ?)', (name, progress))
            conn.commit()
            st.success("Shared!")
        else:
            st.error("Please fill in both fields.")

# 4. Show the Task Board (SQL Data)
st.header("📋 Recent Team Progress")
data = c.execute('SELECT * FROM tasks ORDER BY rowid DESC').fetchall()

for row in data:
    st.info(f"**{row[0]}**: {row[1]}")
