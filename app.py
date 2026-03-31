import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import hashlib
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stDecoration"]   { display: none !important; }
footer                          { display: none !important; }
#MainMenu                       { display: none !important; }
[data-testid="stSidebarCollapseButton"] { visibility: hidden !important; height: 0 !important; }
[data-testid="collapsedControl"]        { visibility: hidden !important; pointer-events: none !important; }
[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important; transform: none !important;
    width: 240px !important; min-width: 240px !important;
}
[data-testid="stSidebar"] { transform: none !important; margin-left: 0 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #010409 !important;
    border-right: 1px solid #21262d !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

.welcome-block {
    padding: 20px 16px 16px 16px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 8px;
}
.welcome-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #484f58; margin-bottom: 4px;
}
.welcome-name { font-size: 16px; font-weight: 700; color: #e6edf3; }

.nav-section {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #484f58; padding: 12px 16px 4px 16px;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    border-radius: 6px !important; font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 400 !important;
    color: #8b949e !important; text-align: left !important;
    width: 100% !important; padding: 6px 16px !important;
    height: 34px !important; box-shadow: none !important;
    margin: 1px 0 !important; transition: background 0.12s, color 0.12s !important;
}
[data-testid="stSidebar"] .stButton > button p {
    text-align: left !important; width: 100% !important;
    margin: 0 !important; color: inherit !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #161b22 !important; color: #e6edf3 !important;
}
[data-testid="nav_feed"] > button,
[data-testid="nav_feed"] > button p { color: #FA8072 !important; font-weight: 700 !important; }
[data-testid="nav_new_task"] > button,
[data-testid="nav_new_task"] > button p { color: #3fb950 !important; font-weight: 700 !important; }
[data-testid="nav_new_proj"] > button,
[data-testid="nav_new_proj"] > button p { color: #3fb950 !important; font-weight: 700 !important; }

[data-testid="stSidebar"] hr { border-color: #21262d !important; margin: 6px 0 !important; }

/* ── Main content ── */
[data-testid="stMainBlockContainer"] {
    background-color: #0d1117 !important; padding: 32px 40px !important;
}
.page-title {
    font-size: 24px; font-weight: 700; color: #e6edf3;
    margin-bottom: 4px; font-family: 'Inter', sans-serif;
}
.page-subtitle {
    font-size: 13px; color: #484f58;
    margin-bottom: 28px; font-family: 'Inter', sans-serif;
}

/* ── Activity card ── */
.a-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 8px; padding: 14px 18px;
    margin-bottom: 8px; font-family: 'Inter', sans-serif;
}
.a-card-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.a-card-name { font-size: 14px; font-weight: 600; color: #e6edf3; }
.a-card-meta { font-size: 12px; color: #484f58; }
.a-card-avatars { display: flex; gap: 4px; margin-top: 6px; }
.badge {
    display: inline-block; font-size: 10px; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase;
    padding: 2px 8px; border-radius: 20px;
}
.badge-task    { background: #0d1a10; color: #3fb950; border: 1px solid #1f4a24; }
.badge-project { background: #0c1929; color: #58a6ff; border: 1px solid #1a3a5c; }

/* ── Avatar circle ── */
.avatar {
    width: 28px; height: 28px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff;
    font-family: 'Inter', sans-serif; flex-shrink: 0;
}
.avatar-lg {
    width: 56px; height: 56px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 700; color: #fff;
    font-family: 'Inter', sans-serif;
}
.avatar-sm {
    width: 22px; height: 22px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 700; color: #fff;
    font-family: 'Inter', sans-serif;
}

/* ── Project card (square) ── */
.proj-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 16px;
    width: 160px; height: 160px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: space-between;
    cursor: pointer; transition: border-color 0.15s, background 0.15s;
    font-family: 'Inter', sans-serif;
}
.proj-card:hover { border-color: #58a6ff; background: #1c2128; }
.proj-card-name {
    font-size: 13px; font-weight: 600; color: #e6edf3;
    text-align: center; word-break: break-word;
}
.proj-card-participants { display: flex; gap: 3px; flex-wrap: wrap; justify-content: center; }

/* ── Project detail ── */
.detail-box {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 8px; padding: 20px;
    font-family: 'Inter', sans-serif;
}
.detail-label { font-size: 11px; color: #484f58; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px; }
.detail-value { font-size: 14px; color: #e6edf3; margin-bottom: 14px; }

/* ── Phase card ── */
.phase-card {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 6px; padding: 12px 14px; margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
}
.phase-title { font-size: 13px; font-weight: 600; color: #e6edf3; margin-bottom: 4px; }
.phase-meta  { font-size: 11px; color: #484f58; }

/* ── Chat ── */
.chat-bubble {
    padding: 8px 12px; border-radius: 8px; margin-bottom: 8px;
    font-size: 13px; font-family: 'Inter', sans-serif;
    max-width: 85%;
}
.chat-bubble.mine    { background: #1f4a24; color: #e6edf3; margin-left: auto; }
.chat-bubble.theirs  { background: #21262d; color: #e6edf3; }
.chat-sender { font-size: 10px; color: #484f58; margin-bottom: 2px; }
.chat-time   { font-size: 10px; color: #484f58; margin-top: 2px; text-align: right; }

/* ── Forms ── */
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stMultiSelect > label, .stDateInput > label {
    font-size: 13px !important; font-weight: 500 !important;
    color: #8b949e !important; font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input, .stTextArea textarea {
    background-color: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 6px !important; color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background-color: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 6px !important; color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
.stFormSubmitButton > button {
    background-color: #238636 !important; color: #ffffff !important;
    border: 1px solid #2ea043 !important; border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 13px !important; padding: 6px 20px !important;
}
.stFormSubmitButton > button:hover { background-color: #2ea043 !important; }

.empty-state {
    text-align: center; padding: 80px 20px; color: #484f58;
    font-family: 'Inter', sans-serif; font-size: 14px;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.coming-soon {
    background: #161b22; border: 1px solid #21262d; border-radius: 8px;
    padding: 40px; text-align: center; color: #484f58;
    font-family: 'Inter', sans-serif; font-size: 14px; margin-top: 16px;
}
.stAlert { background-color: #161b22 !important; border-radius: 6px !important; font-family: 'Inter', sans-serif !important; }

/* ── Delete project button ── */
[data-testid="del_project"] > button {
    background: transparent !important;
    border: 1px solid #3d1e1e !important;
    border-radius: 6px !important;
    color: #f85149 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    transition: all 0.12s !important;
}
[data-testid="del_project"] > button:hover {
    background: #3d1e1e !important;
    border-color: #f85149 !important;
}

/* ── Delete phase button ── */
[data-testid^="del_phase_"] > button {
    background: transparent !important;
    border: 1px solid #3d1e1e !important;
    border-radius: 4px !important;
    color: #f85149 !important;
    font-size: 12px !important;
    height: 26px !important;
    padding: 0 !important;
    transition: all 0.12s !important;
}
[data-testid^="del_phase_"] > button:hover {
    background: #3d1e1e !important;
    border-color: #f85149 !important;
}

/* ── Phase progress buttons ── */
[data-testid^="prog_"] > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 4px !important;
    color: #484f58 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    padding: 3px 0 !important;
    height: 26px !important;
    width: 100% !important;
    transition: all 0.12s !important;
}
[data-testid^="prog_"] > button:hover {
    background: #161b22 !important;
    border-color: #58a6ff !important;
    color: #58a6ff !important;
}

/* ── Employee Info button — small compact badge ── */
[data-testid^="sel_emp_"] > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    color: #8b949e !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    height: 40px !important;
    width: 100% !important;
    transition: background 0.12s, color 0.12s !important;
}
[data-testid^="sel_emp_"] > button:hover {
    background: #2d1b2e !important;
    border-color: #ff9eb5 !important;
    color: #ff9eb5 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATABASE — Supabase / PostgreSQL
# ─────────────────────────────────────────
@st.cache_resource
def get_db():
    db_url = st.secrets["database"]["url"]
    retries = 5
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(db_url, connect_timeout=10, sslmode='require')
            conn.autocommit = False
            break
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                st.error(f"Could not connect to database: {e}")
                st.stop()

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id   SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id           SERIAL PRIMARY KEY,
        name         TEXT NOT NULL,
        category     TEXT,
        est_duration TEXT,
        start_date   TEXT,
        created_by   TEXT,
        created_at   TEXT,
        completed    INTEGER DEFAULT 0,
        completed_by TEXT,
        completed_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS project_participants (
        project_id INTEGER,
        employee   TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id         SERIAL PRIMARY KEY,
        task_name  TEXT NOT NULL,
        project_id INTEGER,
        status     TEXT DEFAULT 'Open',
        created_by TEXT,
        created_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id        SERIAL PRIMARY KEY,
        action    TEXT,
        item_type TEXT,
        item_name TEXT,
        done_by   TEXT,
        done_at   TEXT,
        extra     TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS phases (
        id         SERIAL PRIMARY KEY,
        project_id INTEGER,
        phase_name TEXT,
        equipment  TEXT,
        comments   TEXT,
        added_by   TEXT,
        added_at   TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id         SERIAL PRIMARY KEY,
        project_id INTEGER,
        sender     TEXT,
        message    TEXT,
        sent_at    TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS phase_progress (
        id         SERIAL PRIMARY KEY,
        phase_id   INTEGER,
        status     TEXT,
        updated_by TEXT,
        updated_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS accounting (
        id           SERIAL PRIMARY KEY,
        project_id   INTEGER UNIQUE,
        project_name TEXT,
        category     TEXT,
        created_by   TEXT,
        completed_by TEXT,
        completed_at TEXT,
        billed       TEXT DEFAULT 'Not Completed',
        received     TEXT DEFAULT 'No'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS accounting_chat (
        id         SERIAL PRIMARY KEY,
        project_id INTEGER,
        sender     TEXT,
        message    TEXT,
        sent_at    TEXT
    )''')

    # Seed default employees
    for name in ["Alice", "Bob", "Carlos", "Diana", "Eve", "Frank", "Grace", "Guest"]:
        c.execute("INSERT INTO employees (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (name,))

    conn.commit()
    return conn, c

def get_fresh_cursor():
    """Get a fresh cursor, reconnecting if the connection dropped."""
    conn, c = get_db()
    try:
        c.execute("SELECT 1")
    except Exception:
        get_db.clear()
        conn, c = get_db()
    return conn, c

conn, c = get_fresh_cursor()

def db():
    """Always return a fresh (conn, cursor) — auto-reconnects on drop."""
    global conn, c
    try:
        c.execute("SELECT 1")
    except Exception:
        get_db.clear()
        conn, c = get_db()
    return conn, c

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def log_activity(action, item_type, item_name, done_by, extra=""):
    c.execute(
        'INSERT INTO activity_log (action, item_type, item_name, done_by, done_at, extra) VALUES (%s,%s,%s,%s,%s,%s)',
        (action, item_type, item_name, done_by, get_now(), extra)
    )
    conn.commit()

AVATAR_COLORS = [
    "#e05252","#e07d52","#d4a843","#52a852","#52a8a8",
    "#5271e0","#9452e0","#e052a8","#7a8fa6","#4ea87a",
]

def avatar_color(name):
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[idx]

def avatar_initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

def avatar_html(name, size="sm"):
    color = avatar_color(name)
    initials = avatar_initials(name)
    css_class = f"avatar-{size}"
    return f'<span class="{css_class}" style="background:{color};" title="{name}">{initials}</span>'

def avatars_row(names, size="sm"):
    return "".join(avatar_html(n, size) for n in names)

def get_participants(project_id):
    rows = c.execute(
        "SELECT employee FROM project_participants WHERE project_id=?", (project_id,)
    ).fetchall()
    return [r[0] for r in rows]

def all_employees():
    return [r[0] for r in c.execute("SELECT name FROM employees ORDER BY name").fetchall()]

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if 'page'              not in st.session_state: st.session_state.page = "Main Feed"
if 'active_project'    not in st.session_state: st.session_state.active_project = None
if 'emp_search'        not in st.session_state: st.session_state.emp_search = ""
if 'participants'      not in st.session_state: st.session_state.participants = []
if 'selected_employee' not in st.session_state: st.session_state.selected_employee = None
if 'confirm_delete'    not in st.session_state: st.session_state.confirm_delete = False
if 'active_accounting' not in st.session_state: st.session_state.active_accounting = None

# ── Handle click navigation via query params ──
_qp = st.query_params
if "sel_emp" in _qp:
    st.session_state.selected_employee = _qp["sel_emp"]
    st.session_state.page = "Employees"
    st.query_params.clear()
    st.rerun()
if "open_proj" in _qp:
    st.session_state.active_project = int(_qp["open_proj"])
    st.session_state.page = "Project Detail"
    st.query_params.clear()
    st.rerun()

USERNAME = "Guest"

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 16px 10px 16px;">
        <div style="font-size:20px;font-weight:800;color:#e6edf3;
                    letter-spacing:-0.3px;font-family:'Inter',sans-serif;">
            📦 Task-Box
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="welcome-block">
        <div class="welcome-label">Welcome</div>
        <div class="welcome-name">👤 {USERNAME}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='nav-section'>Quick Actions</div>", unsafe_allow_html=True)
    if st.button("🗞️  Main Feed",   use_container_width=True, key="nav_feed"):
        st.session_state.page = "Main Feed"
        st.session_state.active_project = None
    if st.button("＋  New Task",    use_container_width=True, key="nav_new_task"):
        st.session_state.page = "New Task"
        st.session_state.active_project = None
    if st.button("＋  New Project", use_container_width=True, key="nav_new_proj"):
        st.session_state.page = "New Project"
        st.session_state.active_project = None
        st.session_state.participants = []

    st.divider()
    st.markdown("<div class='nav-section'>Sections</div>", unsafe_allow_html=True)

    if st.button("👥  Employees", use_container_width=True, key="nav_Employees"):
        st.session_state.page = "Employees"
        st.session_state.active_project = None

    for label, page_name in [
        ("🔭  Explorations", "Explorations"),
        ("🏡  Residential",  "Residential"),
        ("🏢  Commercial",   "Commercial"),
        ("📄  Licenses",     "Licenses"),
        ("🔗  Bonds",        "Bonds"),
        ("💼  Accounting",   "Accounting"),
        ("💰  Payroll",      "Payroll"),
    ]:
        if st.button(label, use_container_width=True, key=f"nav_{page_name}"):
            st.session_state.page = page_name
            st.session_state.active_project = None

# ─────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────
page = st.session_state.page

# ══════════════════════════════════════════
# MAIN FEED
# ══════════════════════════════════════════
if page == "Main Feed":
    st.markdown("<div class='page-title'>🗞️ Activity Feed</div>", unsafe_allow_html=True)

    # ── Week Calendar ──
    today      = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_days  = [week_start + timedelta(days=i) for i in range(7)]
    DAY_NAMES  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Fetch all projects with start_date
    all_projects = c.execute(
        "SELECT id, name, start_date FROM projects WHERE start_date IS NOT NULL AND start_date != ''"
    ).fetchall()

    # Build calendar HTML — 7 columns
    cal_cols = st.columns(7)
    for col_idx, day in enumerate(week_days):
        day_str    = day.strftime("%Y-%m-%d")
        is_today   = (day == today)
        day_label  = DAY_NAMES[col_idx]
        day_num    = day.strftime("%d")

        header_bg    = "#FA8072" if is_today else "#161b22"
        header_color = "#fff"    if is_today else "#8b949e"
        border_color = "#FA8072" if is_today else "#21262d"

        # Find projects starting on this day
        day_projects = [(pid, pname) for pid, pname, pstart in all_projects if pstart == day_str]

        proj_items = ""
        for pid, pname in day_projects:
            parts      = get_participants(pid)
            av_html    = "".join(avatar_html(p, "sm") for p in parts[:3])
            short_name = pname[:14] + "…" if len(pname) > 14 else pname
            proj_items += (
                f'<a href="?open_proj={pid}" target="_self" style="text-decoration:none;">'
                f'<div style="background:#0d1117;border:1px solid #30363d;border-radius:5px;'
                f'padding:5px 6px;margin-top:4px;cursor:pointer;">'
                f'<div style="font-size:10px;font-weight:600;color:#e6edf3;margin-bottom:3px;">{short_name}</div>'
                f'<div style="display:flex;gap:2px;">{av_html}</div>'
                f'</div></a>'
            )

        if not proj_items:
            proj_items = '<div style="font-size:10px;color:#30363d;margin-top:6px;text-align:center;">—</div>'

        cal_cols[col_idx].markdown(
            f'<div style="background:{header_bg};border:1px solid {border_color};border-radius:8px;'
            f'padding:8px 6px;min-height:100px;">'
            f'<div style="font-size:10px;font-weight:700;color:{header_color};text-transform:uppercase;'
            f'letter-spacing:0.08em;text-align:center;">{day_label}</div>'
            f'<div style="font-size:16px;font-weight:700;color:{header_color};text-align:center;margin-bottom:4px;">{day_num}</div>'
            f'{proj_items}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#484f58;margin-bottom:10px;'>Recent Activity</div>", unsafe_allow_html=True)

    # ── Activity Log — single line per entry ──
    logs = c.execute(
        "SELECT action, item_type, item_name, done_by, done_at, extra FROM activity_log ORDER BY done_at DESC"
    ).fetchall()

    if not logs:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            Nothing here yet.<br>Create a project or task to get started.
        </div>
        """, unsafe_allow_html=True)
    else:
        feed_html = '<div>'
        for action, item_type, item_name, done_by, done_at, extra in logs:
            badge_class  = "badge-project" if item_type == "Project" else "badge-task"
            creator_av   = avatar_html(done_by, "sm")

            # Build participant avatars separately (never inside an f-string)
            part_av_html = ""
            if extra:
                names        = [n.strip() for n in extra.split(",") if n.strip()]
                part_av_html = "".join(avatar_html(n, "sm") for n in names[:4])
                if part_av_html:
                    part_av_html = (
                        '<span style="display:inline-flex;gap:2px;margin-left:6px;'
                        'vertical-align:middle;">' + part_av_html + '</span>'
                    )

            feed_html += (
                '<div style="display:flex;align-items:center;gap:8px;'
                'padding:8px 12px;border-bottom:1px solid #161b22;">'
                f'<span class="badge {badge_class}">{item_type}</span>'
                f'<span style="font-size:13px;font-weight:600;color:#e6edf3;flex:1;">{item_name}</span>'
                f'{part_av_html}'
                f'<span style="display:inline-flex;align-items:center;gap:4px;">'
                f'{creator_av}'
                f'<span style="font-size:11px;color:#484f58;">{done_by}</span>'
                f'</span>'
                f'<span style="font-size:11px;color:#30363d;white-space:nowrap;">{done_at}</span>'
                '</div>'
            )
        feed_html += '</div>'
        st.markdown(feed_html, unsafe_allow_html=True)

# ══════════════════════════════════════════
# NEW TASK
# ══════════════════════════════════════════
elif page == "New Task":
    st.markdown("<div class='page-title'>＋ New Task</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Add a new task to track.</div>", unsafe_allow_html=True)

    projects = c.execute("SELECT id, name FROM projects ORDER BY name").fetchall()
    project_map = {name: pid for pid, name in projects}

    with st.form("form_new_task", clear_on_submit=True):
        task_name   = st.text_input("Task Name")
        proj_choice = st.selectbox("Link to Project (optional)", ["— None —"] + list(project_map.keys()))
        status      = st.selectbox("Status", ["Open", "In Progress", "Done"])
        submitted   = st.form_submit_button("Create Task")

    if submitted:
        if task_name.strip():
            proj_id = project_map.get(proj_choice) if proj_choice != "— None —" else None
            c.execute(
                'INSERT INTO tasks (task_name, project_id, status, created_by, created_at) VALUES (%s,%s,%s,%s,%s)',
                (task_name.strip(), proj_id, status, USERNAME, get_now())
            )
            conn.commit()
            log_activity("Created", "Task", task_name.strip(), USERNAME)
            st.success(f"Task **{task_name.strip()}** created!")
            st.session_state.page = "Main Feed"
            st.rerun()
        else:
            st.warning("Please enter a task name.")

# ══════════════════════════════════════════
# NEW PROJECT
# ══════════════════════════════════════════
elif page == "New Project":
    st.markdown("<div class='page-title'>＋ New Project</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Fill in the details to start a new project.</div>", unsafe_allow_html=True)

    # ── Participant search (outside form so it's interactive) ──
    st.markdown("**Participants**")
    emp_search = st.text_input(
        "Search employee name", value=st.session_state.emp_search,
        placeholder="Start typing a name…", key="emp_search_input"
    )

    if emp_search:
        matches = [e for e in all_employees() if emp_search.lower() in e.lower()
                   and e not in st.session_state.participants]
        if matches:
            cols = st.columns(min(len(matches), 4))
            for i, emp in enumerate(matches[:4]):
                if cols[i].button(f"＋ {emp}", key=f"add_{emp}"):
                    st.session_state.participants.append(emp)
                    st.session_state.emp_search = ""
                    st.rerun()
        else:
            st.caption("No matches found.")

    # Show selected participants with remove option
    if st.session_state.participants:
        st.markdown("**Added:**")
        cols = st.columns(min(len(st.session_state.participants), 5))
        for i, p in enumerate(st.session_state.participants):
            with cols[i % 5]:
                st.markdown(
                    f"{avatar_html(p,'sm')} <span style='font-size:12px;color:#8b949e'>{p}</span>",
                    unsafe_allow_html=True
                )
                if st.button("✕", key=f"rm_{p}"):
                    st.session_state.participants.remove(p)
                    st.rerun()

    st.markdown("---")

    # ── Main form ──
    with st.form("form_new_proj", clear_on_submit=True):
        proj_name    = st.text_input("Project Name")
        proj_cat     = st.selectbox("Category", [
            "Commercial", "Residential", "Explorations",
            "Licenses", "Bonds", "Accounting", "Payroll"
        ])
        est_duration = st.text_input("Estimated Duration (e.g. 3 months)")
        start_date   = st.date_input("Starting Date")
        submitted    = st.form_submit_button("Create Project")

    if submitted:
        if proj_name.strip():
            c.execute(
                '''INSERT INTO projects (name, category, est_duration, start_date, created_by, created_at)
                   VALUES (%s,%s,%s,%s,%s,%s) RETURNING id''',
                (proj_name.strip(), proj_cat, est_duration.strip(),
                 str(start_date), USERNAME, get_now())
            )
            proj_id = c.fetchone()[0]
            conn.commit()

            # Add creator as participant if not already
            all_parts = list(st.session_state.participants)
            if USERNAME not in all_parts:
                all_parts.append(USERNAME)

            for emp in all_parts:
                c.execute(
                    "INSERT INTO project_participants (project_id, employee) VALUES (%s,%s)",
                    (proj_id, emp)
                )
            conn.commit()

            log_activity("Created", "Project", proj_name.strip(), USERNAME,
                         extra=",".join(all_parts))

            st.session_state.participants = []
            st.session_state.page = "Main Feed"
            st.rerun()
        else:
            st.warning("Please enter a project name.")

# ══════════════════════════════════════════
# PROJECT DETAIL PAGE
# ══════════════════════════════════════════
elif page == "Project Detail" and st.session_state.active_project:
    proj_id = st.session_state.active_project
    proj = c.execute(
        "SELECT name, category, est_duration, start_date, created_by, created_at FROM projects WHERE id=?",
        (proj_id,)
    ).fetchone()

    if not proj:
        st.error("Project not found.")
    else:
        name, category, est_duration, start_date, created_by, created_at = proj
        participants = get_participants(proj_id)

        # Back button
        if st.button("← Back", key="back_btn"):
            st.session_state.page = category
            st.session_state.active_project = None
            st.rerun()

        st.markdown(f"<div class='page-title'>📁 {name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='page-subtitle'>{category}</div>", unsafe_allow_html=True)

        left_col, right_col = st.columns([1, 1], gap="large")

        # ── LEFT: Details + Phases ──
        with left_col:
            part_html       = "".join(avatar_html(p, "sm") for p in participants)
            part_names_html = "".join(
                f'<span style="font-size:11px;color:#8b949e;align-self:center;">{p}</span>'
                for p in participants
            )
            st.markdown(f"""
            <div class="detail-box">
                <div class="detail-label">Category</div><div class="detail-value">{category}</div>
                <div class="detail-label">Estimated Duration</div><div class="detail-value">{est_duration or "—"}</div>
                <div class="detail-label">Starting Date</div><div class="detail-value">{start_date or "—"}</div>
                <div class="detail-label">Created By</div><div class="detail-value">{created_by}</div>
                <div class="detail-label">Created At</div><div class="detail-value">{created_at}</div>
                <div class="detail-label">Participants</div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
                    {part_html}{part_names_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Phases ──
            st.markdown("**Project Phases**")
            phases = c.execute(
                "SELECT id, phase_name, equipment, comments, added_by, added_at FROM phases WHERE project_id=? ORDER BY added_at",
                (proj_id,)
            ).fetchall()

            PROGRESS_STEPS = ["Started", "25%", "50%", "75%", "Finished"]
            PROGRESS_COLORS = {
                "Started":  "#58a6ff",
                "25%":      "#d29922",
                "50%":      "#d29922",
                "75%":      "#3fb950",
                "Finished": "#3fb950",
            }

            if phases:
                for ph_id, ph_name, ph_equip, ph_comment, ph_by, ph_at in phases:
                    latest_prog    = c.execute(
                        "SELECT status, updated_by, updated_at FROM phase_progress WHERE phase_id=? ORDER BY updated_at DESC LIMIT 1",
                        (ph_id,)
                    ).fetchone()
                    current_status = latest_prog[0] if latest_prog else None

                    # Build each field only if it has content — no HTML leaking into text
                    equip_str   = ph_equip.strip()   if ph_equip   else ""
                    comment_str = ph_comment.strip() if ph_comment else ""

                    # Build progress pills (pure HTML, no f-string conditionals inside tags)
                    pills_html = ""
                    for step in PROGRESS_STEPS:
                        is_active  = (step == current_status)
                        pill_color = PROGRESS_COLORS[step]
                        if is_active:
                            pills_html += (
                                f'<span style="background:{pill_color};color:#fff;font-size:10px;'
                                f'font-weight:700;padding:4px 10px;border-radius:4px;'
                                f'border:1px solid {pill_color};">{step}</span> '
                            )
                        else:
                            pills_html += (
                                f'<span style="background:#21262d;color:#484f58;font-size:10px;'
                                f'font-weight:600;padding:4px 10px;border-radius:4px;'
                                f'border:1px solid #30363d;">{step}</span> '
                            )

                    # Last update line
                    if latest_prog:
                        prog_color       = PROGRESS_COLORS[latest_prog[0]]
                        last_update_html = (
                            f'<div style="font-size:11px;color:#484f58;margin-top:6px;">'
                            f'Last updated to <span style="color:{prog_color};font-weight:600;">'
                            f'{latest_prog[0]}</span> by '
                            f'<span style="color:#8b949e;font-weight:600;">{latest_prog[1]}</span>'
                            f' &middot; {latest_prog[2]}</div>'
                        )
                    else:
                        last_update_html = '<div style="font-size:11px;color:#484f58;margin-top:6px;">Not started yet.</div>'

                    # Full card — one single self-contained HTML block
                    card_html = (
                        '<div class="phase-card">'
                          '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">'
                            f'<div style="font-size:13px;font-weight:700;color:#e6edf3;">📌 {ph_name}</div>'
                            f'<div style="font-size:10px;color:#484f58;text-align:right;">'
                              f'Created by <span style="color:#8b949e;font-weight:600;">{ph_by}</span>'
                              f'<br>{ph_at}'
                            f'</div>'
                          '</div>'
                    )
                    if equip_str:
                        card_html += (
                            f'<div style="font-size:12px;color:#8b949e;margin-bottom:4px;">'
                            f'🔧 <strong>Equipment:</strong> {equip_str}</div>'
                        )
                    if comment_str:
                        card_html += (
                            f'<div style="font-size:12px;color:#8b949e;margin-bottom:4px;">'
                            f'💬 <strong>Comments:</strong> {comment_str}</div>'
                        )
                    card_html += (
                        '<div style="margin-top:12px;">'
                          '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                               'letter-spacing:0.08em;color:#484f58;margin-bottom:6px;">Progress</div>'
                          f'<div style="display:flex;gap:5px;flex-wrap:wrap;">{pills_html}</div>'
                          f'{last_update_html}'
                        '</div>'
                        '</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    # Progress click buttons + Delete Phase — participants only
                    if USERNAME in participants:
                        # 5 progress steps + 1 delete column
                        prog_cols = st.columns(len(PROGRESS_STEPS) + 1)
                        for i, step in enumerate(PROGRESS_STEPS):
                            if prog_cols[i].button(step, key=f"prog_{ph_id}_{step}"):
                                c.execute(
                                    "INSERT INTO phase_progress (phase_id, status, updated_by, updated_at) VALUES (%s,%s,%s,%s)",
                                    (ph_id, step, USERNAME, get_now())
                                )
                                conn.commit()
                                st.rerun()
                        # Delete phase button in last column
                        if prog_cols[-1].button("🗑️", key=f"del_phase_{ph_id}", help="Delete this phase"):
                            c.execute("DELETE FROM phases WHERE id=%s", (ph_id,))
                            c.execute("DELETE FROM phase_progress WHERE phase_id=%s", (ph_id,))
                            conn.commit()
                            st.rerun()
                        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#484f58;font-size:13px;'>No phases yet.</div>", unsafe_allow_html=True)

            if USERNAME in participants:
                st.markdown("<br>**Add a Phase**")
                with st.form("form_phase", clear_on_submit=True):
                    ph_name    = st.text_input("Phase Name")
                    ph_equip   = st.text_input("Equipment (optional)")
                    ph_comment = st.text_area("Comments (optional)", height=80)
                    ph_submit  = st.form_submit_button("Add Phase")

                if ph_submit and ph_name.strip():
                    c.execute(
                        "INSERT INTO phases (project_id, phase_name, equipment, comments, added_by, added_at) VALUES (%s,%s,%s,%s,%s,%s)",
                        (proj_id, ph_name.strip(), ph_equip.strip(), ph_comment.strip(), USERNAME, get_now())
                    )
                    conn.commit()
                    st.rerun()
            else:
                st.caption("Only project participants can add phases.")

            # ── Complete / Delete Project ──
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#21262d;'>", unsafe_allow_html=True)

            # Check if already completed
            proj_status = c.execute("SELECT completed, completed_by, completed_at FROM projects WHERE id=%s", (proj_id,)).fetchone()
            is_completed = proj_status and proj_status[0] == 1

            if is_completed:
                st.markdown(
                    f'<div style="background:#0d1a10;border:1px solid #1f4a24;border-radius:6px;'
                    f'padding:10px 14px;font-size:12px;color:#3fb950;margin-bottom:8px;">'
                    f'✅ Completed by <strong>{proj_status[1]}</strong> · {proj_status[2]}</div>',
                    unsafe_allow_html=True
                )
            elif USERNAME in participants:
                if st.button("✅  Mark as Complete", key="complete_project", use_container_width=True):
                    now = get_now()
                    c.execute(
                        "UPDATE projects SET completed=1, completed_by=?, completed_at=? WHERE id=?",
                        (USERNAME, now, proj_id)
                    )
                    # Log to activity feed
                    log_activity("Completed", "Project", name, USERNAME)
                    # If qualifying category, create accounting entry
                    if category in ("Explorations", "Residential", "Commercial"):
                        proj_creator = c.execute("SELECT created_by FROM projects WHERE id=%s", (proj_id,)).fetchone()[0]
                        c.execute(
                            "INSERT OR IGNORE INTO accounting (project_id, project_name, category, created_by, completed_by, completed_at) VALUES (%s,%s,%s,%s,%s,%s)",
                            (proj_id, name, category, proj_creator, USERNAME, now)
                        )
                    conn.commit()
                    st.rerun()

            if USERNAME in participants:
                if st.button("🗑️  Delete Project", key="del_project", use_container_width=True):
                    st.session_state.confirm_delete = True

                if st.session_state.get("confirm_delete"):
                    st.warning("⚠️ Are you sure? This will permanently delete the project and all its phases.")
                    c1, c2 = st.columns(2)
                    if c1.button("Yes, delete it", key="confirm_del_yes"):
                        c.execute("DELETE FROM projects WHERE id=%s", (proj_id,))
                        c.execute("DELETE FROM project_participants WHERE project_id=%s", (proj_id,))
                        # Delete all phases and their progress
                        phase_ids = [r[0] for r in c.execute("SELECT id FROM phases WHERE project_id=%s", (proj_id,)).fetchall()]
                        for pid2 in phase_ids:
                            c.execute("DELETE FROM phase_progress WHERE phase_id=%s", (pid2,))
                        c.execute("DELETE FROM phases WHERE project_id=%s", (proj_id,))
                        c.execute("DELETE FROM chat_messages WHERE project_id=%s", (proj_id,))
                        conn.commit()
                        st.session_state.confirm_delete = False
                        st.session_state.active_project = None
                        st.session_state.page = category
                        st.rerun()
                    if c2.button("Cancel", key="confirm_del_no"):
                        st.session_state.confirm_delete = False
                        st.rerun()

        # ── RIGHT: Timeline + Chat ──
        with right_col:

            # ── Phase Timeline ──
            timeline_phases = c.execute(
                "SELECT id, phase_name FROM phases WHERE project_id=? ORDER BY added_at",
                (proj_id,)
            ).fetchall()

            if timeline_phases:
                timeline_html = (
                    '<div style="margin-bottom:20px;">'
                    '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                         'letter-spacing:0.08em;color:#484f58;margin-bottom:12px;">Phase Timeline</div>'
                    '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0;">'
                )
                for t_idx, (t_id, t_name) in enumerate(timeline_phases):
                    t_prog = c.execute(
                        "SELECT status FROM phase_progress WHERE phase_id=? ORDER BY updated_at DESC LIMIT 1",
                        (t_id,)
                    ).fetchone()
                    t_status = t_prog[0] if t_prog else None

                    # Ball color: green=current/in-progress, light blue=finished, grey=not started
                    if t_status == "Finished":
                        ball_color  = "#58a6ff"   # light blue
                        label_color = "#58a6ff"
                        ring        = "#58a6ff"
                    elif t_status in ("Started", "25%", "50%", "75%"):
                        ball_color  = "#3fb950"   # green = active
                        label_color = "#3fb950"
                        ring        = "#3fb950"
                    else:
                        ball_color  = "#21262d"   # grey = not started
                        label_color = "#484f58"
                        ring        = "#30363d"

                    # Connector line between balls (not after last)
                    connector = ""
                    if t_idx < len(timeline_phases) - 1:
                        connector = '<div style="flex:1;height:2px;background:#21262d;min-width:16px;max-width:40px;"></div>'

                    timeline_html += (
                        '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                          f'<div style="width:14px;height:14px;border-radius:50%;'
                               f'background:{ball_color};border:2px solid {ring};'
                               f'box-shadow:0 0 6px {ball_color}33;"></div>'
                          f'<div style="font-size:9px;color:{label_color};font-weight:600;'
                               f'text-align:center;max-width:60px;line-height:1.2;">{t_name}</div>'
                        '</div>'
                        + connector
                    )
                timeline_html += '</div></div>'
                st.markdown(timeline_html, unsafe_allow_html=True)

            st.markdown("**Project Chat**")

            messages = c.execute(
                "SELECT sender, message, sent_at FROM chat_messages WHERE project_id=? ORDER BY sent_at",
                (proj_id,)
            ).fetchall()

            chat_html = "<div style='height:360px;overflow-y:auto;padding:8px;background:#0d1117;border:1px solid #21262d;border-radius:8px;margin-bottom:12px;'>"
            if messages:
                for sender, message, sent_at in messages:
                    bubble_class = "mine" if sender == USERNAME else "theirs"
                    chat_html += f"""
                    <div style="display:flex;flex-direction:column;align-items:{'flex-end' if sender==USERNAME else 'flex-start'};margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">
                            {avatar_html(sender,'sm')}
                            <span style="font-size:10px;color:#484f58;">{sender} · {sent_at}</span>
                        </div>
                        <div class="chat-bubble {bubble_class}">{message}</div>
                    </div>
                    """
            else:
                chat_html += "<div style='text-align:center;color:#484f58;font-size:13px;padding:40px 0;'>No messages yet. Start the conversation!</div>"
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

            if USERNAME in participants:
                with st.form("chat_form", clear_on_submit=True):
                    msg_cols = st.columns([5, 1])
                    chat_input = msg_cols[0].text_input("Message", label_visibility="collapsed", placeholder="Type a message…")
                    send_btn   = msg_cols[1].form_submit_button("Send")

                if send_btn and chat_input.strip():
                    c.execute(
                        "INSERT INTO chat_messages (project_id, sender, message, sent_at) VALUES (%s,%s,%s,%s)",
                        (proj_id, USERNAME, chat_input.strip(), get_now())
                    )
                    conn.commit()
                    st.rerun()
            else:
                st.caption("Only project participants can send messages.")

# ══════════════════════════════════════════
# SECTION PAGES (Explorations, Residential, etc.)
# ══════════════════════════════════════════
elif page in ["Explorations", "Residential", "Commercial", "Licenses", "Bonds", "Payroll"]:
    icons = {
        "Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢",
        "Licenses": "📄", "Bonds": "🔗", "Payroll": "💰",
    }
    icon = icons.get(page, "📁")
    st.markdown(f"<div class='page-title'>{icon} {page}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>Projects in {page.lower()}.</div>", unsafe_allow_html=True)

    if page in ["Explorations", "Residential", "Commercial", "Licenses", "Bonds", "Payroll"]:
        # Active (not completed) projects
        rows = c.execute(
            "SELECT id, name, created_by FROM projects WHERE category=? AND (completed IS NULL OR completed=0) ORDER BY created_at DESC",
            (page,)
        ).fetchall()

        if rows:
            cols_per_row = 4
            for row_start in range(0, len(rows), cols_per_row):
                row_projects = rows[row_start:row_start + cols_per_row]
                cols = st.columns(cols_per_row)
                for col_idx, (pid, pname, pcreator) in enumerate(row_projects):
                    participants = get_participants(pid)
                    creator_html = avatar_html(pcreator, "lg")
                    part_mini    = "".join(avatar_html(p, "sm") for p in participants[:6])
                    with cols[col_idx]:
                        st.markdown(f"""
                        <a href="?open_proj={pid}" target="_self" style="text-decoration:none;">
                            <div class="proj-card">
                                <div class="proj-card-name">{pname}</div>
                                <div style="margin:8px 0;">{creator_html}</div>
                                <div class="proj-card-participants">{part_mini}</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="empty-state" style="padding:40px 20px;">
                <div class="empty-icon">{icon}</div>
                No active {page.lower()} projects yet.<br>
                Use <strong style="color:#3fb950">＋ New Project</strong> to add one.
            </div>
            """, unsafe_allow_html=True)

        # ── Completed Projects ──
        completed_rows = c.execute(
            "SELECT id, name, created_by, completed_by, completed_at FROM projects WHERE category=? AND completed=1 ORDER BY completed_at DESC",
            (page,)
        ).fetchall()

        if completed_rows:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:11px;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.08em;color:#484f58;margin-bottom:10px;">Completed Projects</div>',
                unsafe_allow_html=True
            )
            completed_html = ""
            for cpid, cpname, ccreator, cby, cat2 in completed_rows:
                cparts   = get_participants(cpid)
                av_html  = "".join(avatar_html(p, "sm") for p in cparts[:5])
                completed_html += (
                    f'<a href="?open_proj={cpid}" target="_self" style="text-decoration:none;">'
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'background:#0d1117;border:1px solid #21262d;border-radius:6px;'
                    f'padding:8px 14px;margin-bottom:5px;cursor:pointer;">'
                    f'<span style="font-size:11px;background:#0d1a10;color:#3fb950;border:1px solid #1f4a24;'
                    f'border-radius:20px;padding:2px 8px;font-weight:700;">DONE</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#8b949e;flex:1;">{cpname}</span>'
                    f'<span style="display:flex;gap:3px;">{av_html}</span>'
                    f'<span style="font-size:11px;color:#484f58;">Completed by '
                    f'<strong style="color:#8b949e">{cby}</strong> · {cat2}</span>'
                    f'</div></a>'
                )
            st.markdown(completed_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="coming-soon">🚧 This section is coming soon.</div>', unsafe_allow_html=True)



# ══════════════════════════════════════════
# ACCOUNTING PAGE
# ══════════════════════════════════════════
elif page == "Accounting":
    st.markdown("<div class='page-title'>💼 Accounting</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Completed projects — billing and payment tracking.</div>", unsafe_allow_html=True)

    acc_rows = c.execute(
        "SELECT id, project_id, project_name, category, created_by, completed_by, completed_at, billed, received FROM accounting ORDER BY completed_at DESC"
    ).fetchall()

    if not acc_rows:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💼</div>
            No completed projects yet.<br>
            Complete a project to see it here.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Check if opening a specific accounting entry
        if st.session_state.get("active_accounting"):
            acc_id = st.session_state.active_accounting
            entry  = c.execute(
                "SELECT id, project_id, project_name, category, created_by, completed_by, completed_at, billed, received FROM accounting WHERE id=?",
                (acc_id,)
            ).fetchone()

            if not entry:
                st.error("Entry not found.")
            else:
                a_id, a_proj_id, a_name, a_cat, a_creator, a_cby, a_cat2, a_billed, a_received = entry
                participants = get_participants(a_proj_id)

                if st.button("← Back to Accounting", key="back_acc"):
                    st.session_state.active_accounting = None
                    st.rerun()

                st.markdown(f"<div class='page-title'>📁 {a_name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='page-subtitle'>{a_cat} · Completed</div>", unsafe_allow_html=True)

                left_col, right_col = st.columns([1, 1], gap="large")

                with left_col:
                    # Project info
                    part_html      = "".join(avatar_html(p, "sm") for p in participants)
                    part_names_html = "".join(
                        f'<span style="font-size:11px;color:#8b949e;align-self:center;">{p}</span>'
                        for p in participants
                    )
                    orig_proj = c.execute(
                        "SELECT est_duration, start_date FROM projects WHERE id=?", (a_proj_id,)
                    ).fetchone()
                    est_dur   = orig_proj[0] if orig_proj else "—"
                    start_d   = orig_proj[1] if orig_proj else "—"

                    st.markdown(f"""
                    <div class="detail-box">
                        <div class="detail-label">Category</div><div class="detail-value">{a_cat}</div>
                        <div class="detail-label">Estimated Duration</div><div class="detail-value">{est_dur or "—"}</div>
                        <div class="detail-label">Starting Date</div><div class="detail-value">{start_d or "—"}</div>
                        <div class="detail-label">Created By</div><div class="detail-value">{a_creator}</div>
                        <div class="detail-label">Completed By</div><div class="detail-value">{a_cby} · {a_cat2}</div>
                        <div class="detail-label">Participants</div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
                            {part_html}{part_names_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── Billed status ──
                    st.markdown(
                        '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                        'letter-spacing:0.08em;color:#484f58;margin-bottom:8px;">Billed</div>',
                        unsafe_allow_html=True
                    )
                    billed_opts   = ["Not Completed", "Completed"]
                    billed_colors = {"Not Completed": "#d29922", "Completed": "#3fb950"}
                    b_cols = st.columns(len(billed_opts))
                    for i, opt in enumerate(billed_opts):
                        is_sel     = (a_billed == opt)
                        btn_style  = "border: 1px solid " + (billed_colors[opt] if is_sel else "#30363d")
                        btn_color  = billed_colors[opt] if is_sel else "#484f58"
                        b_cols[i].markdown(
                            f'<div style="background:{"#161b22" if is_sel else "#0d1117"};'
                            f'{btn_style};border-radius:5px;padding:6px;text-align:center;'
                            f'font-size:11px;font-weight:600;color:{btn_color};">{opt}</div>',
                            unsafe_allow_html=True
                        )
                        if b_cols[i].button(opt, key=f"billed_{opt}_{a_id}"):
                            c.execute("UPDATE accounting SET billed=%s WHERE id=%s", (opt, a_id))
                            conn.commit()
                            st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── Received status ──
                    st.markdown(
                        '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                        'letter-spacing:0.08em;color:#484f58;margin-bottom:8px;">Received</div>',
                        unsafe_allow_html=True
                    )
                    recv_opts   = ["No", "Partially", "Completed"]
                    recv_colors = {"No": "#f85149", "Partially": "#d29922", "Completed": "#3fb950"}
                    r_cols = st.columns(len(recv_opts))
                    for i, opt in enumerate(recv_opts):
                        is_sel    = (a_received == opt)
                        btn_style = "border: 1px solid " + (recv_colors[opt] if is_sel else "#30363d")
                        btn_color = recv_colors[opt] if is_sel else "#484f58"
                        r_cols[i].markdown(
                            f'<div style="background:{"#161b22" if is_sel else "#0d1117"};'
                            f'{btn_style};border-radius:5px;padding:6px;text-align:center;'
                            f'font-size:11px;font-weight:600;color:{btn_color};">{opt}</div>',
                            unsafe_allow_html=True
                        )
                        if r_cols[i].button(opt, key=f"recv_{opt}_{a_id}"):
                            c.execute("UPDATE accounting SET received=%s WHERE id=%s", (opt, a_id))
                            conn.commit()
                            st.rerun()

                with right_col:
                    st.markdown("**Project Chat**")
                    msgs = c.execute(
                        "SELECT sender, message, sent_at FROM accounting_chat WHERE project_id=? ORDER BY sent_at",
                        (a_proj_id,)
                    ).fetchall()

                    chat_html = "<div style='height:400px;overflow-y:auto;padding:8px;background:#0d1117;border:1px solid #21262d;border-radius:8px;margin-bottom:12px;'>"
                    if msgs:
                        for sender, message, sent_at in msgs:
                            bubble_class = "mine" if sender == USERNAME else "theirs"
                            av           = avatar_html(sender, "sm")
                            align        = "flex-end" if sender == USERNAME else "flex-start"
                            chat_html += (
                                f'<div style="display:flex;flex-direction:column;align-items:{align};margin-bottom:8px;">'
                                f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">'
                                f'{av}<span style="font-size:10px;color:#484f58;">{sender} · {sent_at}</span></div>'
                                f'<div class="chat-bubble {bubble_class}">{message}</div>'
                                f'</div>'
                            )
                    else:
                        chat_html += "<div style='text-align:center;color:#484f58;font-size:13px;padding:40px 0;'>No messages yet.</div>"
                    chat_html += "</div>"
                    st.markdown(chat_html, unsafe_allow_html=True)

                    with st.form("acc_chat_form", clear_on_submit=True):
                        msg_cols    = st.columns([5, 1])
                        chat_input  = msg_cols[0].text_input("Message", label_visibility="collapsed", placeholder="Type a message…")
                        send_btn    = msg_cols[1].form_submit_button("Send")

                    if send_btn and chat_input.strip():
                        c.execute(
                            "INSERT INTO accounting_chat (project_id, sender, message, sent_at) VALUES (%s,%s,%s,%s)",
                            (a_proj_id, USERNAME, chat_input.strip(), get_now())
                        )
                        conn.commit()
                        st.rerun()

        else:
            # ── Accounting list ──
            billed_color  = {"Not Completed": "#d29922", "Completed": "#3fb950"}
            recv_color    = {"No": "#f85149", "Partially": "#d29922", "Completed": "#3fb950"}

            for a_id, a_proj_id, a_name, a_cat, a_creator, a_cby, a_cat2, a_billed, a_received in acc_rows:
                bc = billed_color.get(a_billed, "#484f58")
                rc = recv_color.get(a_received, "#484f58")
                cat_icon = {"Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢"}.get(a_cat, "📁")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'background:#161b22;border:1px solid #21262d;border-radius:6px;'
                    f'padding:10px 14px;margin-bottom:6px;">'
                    f'<span style="font-size:14px;">{cat_icon}</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#e6edf3;flex:1;">{a_name}</span>'
                    f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
                    f'background:#161b22;border:1px solid {bc};color:{bc};">BILLED: {a_billed}</span>'
                    f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
                    f'background:#161b22;border:1px solid {rc};color:{rc};">RECEIVED: {a_received}</span>'
                    f'<span style="font-size:11px;color:#484f58;">{a_cat2}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"Open  {a_name}", key=f"acc_open_{a_id}"):
                    st.session_state.active_accounting = a_id
                    st.rerun()

# ══════════════════════════════════════════
# EMPLOYEES PAGE
# ══════════════════════════════════════════
elif page == "Employees":
    st.markdown("<div class='page-title'>👥 Employees</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Manage your team and view their projects.</div>", unsafe_allow_html=True)

    # ── Add Employee button + form ──
    if st.button("＋  Add Employee", key="add_emp_btn"):
        st.session_state.show_add_emp = True

    if st.session_state.get("show_add_emp"):
        with st.form("form_add_employee", clear_on_submit=True):
            new_emp_name = st.text_input("Employee Name")
            col_s, col_c = st.columns([1, 5])
            save_emp = col_s.form_submit_button("Save")
            col_c.form_submit_button("Cancel", on_click=lambda: st.session_state.update(show_add_emp=False))

        if save_emp:
            if new_emp_name.strip():
                try:
                    c.execute("INSERT INTO employees (name) VALUES (%s)", (new_emp_name.strip(),))
                    conn.commit()
                    st.success(f"{new_emp_name.strip()} added!")
                    st.session_state.show_add_emp = False
                    st.rerun()
                except Exception:
                    st.warning("That employee already exists.")
            else:
                st.warning("Please enter a name.")

    st.markdown("<br>", unsafe_allow_html=True)

    employees = all_employees()

    if not employees:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">👥</div>
            No employees yet. Add one above!
        </div>
        """, unsafe_allow_html=True)
    else:
        left_col, right_col = st.columns([1, 2], gap="large")

        with left_col:
            st.markdown("<div class='detail-label' style='padding-bottom:8px;'>Team Members</div>", unsafe_allow_html=True)
            for emp in employees:
                is_selected = st.session_state.selected_employee == emp
                bg     = "#2d1b2e" if is_selected else "#161b22"
                color  = "#ff9eb5" if is_selected else "#e6edf3"
                border = "#ff9eb5" if is_selected else "#21262d"
                weight = "700"     if is_selected else "400"

                row_left, row_right = st.columns([5, 1])
                row_left.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;
                            background:{bg};border:1px solid {border};
                            border-radius:8px;padding:8px 12px;height:40px;">
                    {avatar_html(emp, "sm")}
                    <span style="font-size:13px;font-weight:{weight};color:{color};">{emp}</span>
                </div>
                """, unsafe_allow_html=True)
                if row_right.button("Info", key=f"sel_emp_{emp}"):
                    st.session_state.selected_employee = emp
                    st.rerun()

        with right_col:
            if st.session_state.selected_employee:
                emp = st.session_state.selected_employee
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                    {avatar_html(emp, "lg")}
                    <div>
                        <div style="font-size:18px;font-weight:700;color:#e6edf3;">{emp}</div>
                        <div style="font-size:12px;color:#484f58;">Employee</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Get all projects this employee is participating in
                emp_projects = c.execute("""
                    SELECT p.id, p.name, p.category, p.created_by, p.created_at
                    FROM projects p
                    JOIN project_participants pp ON p.id = pp.project_id
                    WHERE pp.employee = ?
                    ORDER BY p.created_at DESC
                """, (emp,)).fetchall()

                st.markdown(f"<div class='detail-label'>Projects ({len(emp_projects)})</div>", unsafe_allow_html=True)

                if emp_projects:
                    for pid, pname, pcat, pcreator, pdate in emp_projects:
                        participants = get_participants(pid)
                        part_avatars = "".join(avatar_html(p, "sm") for p in participants[:5])
                        st.markdown(f"""
                        <a href="?open_proj={pid}" target="_self" style="text-decoration:none;">
                            <div class="a-card" style="margin-bottom:8px;cursor:pointer;transition:border-color 0.15s;"
                                 onmouseover="this.style.borderColor='#58a6ff'"
                                 onmouseout="this.style.borderColor='#21262d'">
                                <div class="a-card-top">
                                    <span class="badge badge-project">{pcat}</span>
                                    <span class="a-card-name">{pname}</span>
                                </div>
                                <div class="a-card-meta" style="margin-bottom:6px;">
                                    Created by <strong style="color:#8b949e">{pcreator}</strong> · {pdate}
                                </div>
                                <div style="display:flex;gap:4px;">{part_avatars}</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

                else:
                    st.markdown("""
                    <div style="color:#484f58;font-size:13px;padding:20px 0;">
                        Not assigned to any projects yet.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state" style="padding:60px 20px;">
                    <div class="empty-icon">👈</div>
                    Select an employee on the left<br>to see their projects.
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# FALLBACK
# ══════════════════════════════════════════
else:
    st.session_state.page = "Main Feed"
    st.rerun()
