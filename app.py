import streamlit as st
import psycopg2
import psycopg2.errors
from psycopg2.extras import RealDictCursor
import time
import hashlib
import html as _html
from datetime import datetime, date, timedelta

def esc(x):
    """HTML-escape any user-typed text before it goes into markup."""
    return "" if x is None else _html.escape(str(x))

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="My-Task-Box", page_icon="📦", layout="wide")

# ─────────────────────────────────────────
# CSS — LIGHT THEME
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #f6f8fa !important;
    color: #1f2328 !important;
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
    background-color: #ffffff !important;
    border-right: 1px solid #d0d7de !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

.welcome-block {
    padding: 20px 16px 16px 16px;
    border-bottom: 1px solid #eaeef2;
    margin-bottom: 8px;
}
.welcome-label {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #656d76; margin-bottom: 4px;
}
.welcome-name { font-size: 16px; font-weight: 700; color: #1f2328; }

.nav-section {
    font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #656d76; padding: 12px 16px 4px 16px;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    border-radius: 6px !important; font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 400 !important;
    color: #57606a !important; text-align: left !important;
    width: 100% !important; padding: 6px 16px !important;
    height: 34px !important; box-shadow: none !important;
    margin: 1px 0 !important; transition: background 0.12s, color 0.12s !important;
}
[data-testid="stSidebar"] .stButton > button p {
    text-align: left !important; width: 100% !important;
    margin: 0 !important; color: inherit !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #f6f8fa !important; color: #1f2328 !important;
}

/* ── Main Feed highlight — thicker salmon accent ── */
[data-testid="nav_feed"] > button,
[data-testid="nav_feed"] > button p {
    color: #cf4d3d !important;
    font-weight: 800 !important;
    font-size: 14px !important;
}
[data-testid="nav_feed"] > button {
    border-left: 3px solid #FA8072 !important;
    padding-left: 13px !important;
    background-color: #fff5f3 !important;
}
[data-testid="nav_feed"] > button:hover {
    background-color: #ffe9e5 !important;
}

[data-testid="nav_new_task"] > button,
[data-testid="nav_new_task"] > button p { color: #1a7f37 !important; font-weight: 700 !important; }
[data-testid="nav_new_proj"] > button,
[data-testid="nav_new_proj"] > button p { color: #1a7f37 !important; font-weight: 700 !important; }

[data-testid="stSidebar"] hr { border-color: #eaeef2 !important; margin: 6px 0 !important; }

/* ── Main content ── */
[data-testid="stMainBlockContainer"] {
    background-color: #f6f8fa !important; padding: 32px 40px !important;
}
.page-title {
    font-size: 24px; font-weight: 700; color: #1f2328;
    margin-bottom: 4px; font-family: 'Inter', sans-serif;
}
.page-subtitle {
    font-size: 13px; color: #656d76;
    margin-bottom: 28px; font-family: 'Inter', sans-serif;
}

/* ── Activity card ── */
.a-card {
    background: #ffffff; border: 1px solid #d0d7de;
    border-radius: 8px; padding: 14px 18px;
    margin-bottom: 8px; font-family: 'Inter', sans-serif;
}
.a-card-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.a-card-name { font-size: 14px; font-weight: 600; color: #1f2328; }
.a-card-meta { font-size: 12px; color: #656d76; }
.a-card-avatars { display: flex; gap: 4px; margin-top: 6px; }
.badge {
    display: inline-block; font-size: 10px; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase;
    padding: 2px 8px; border-radius: 20px;
}
.badge-task    { background: #dafbe1; color: #1a7f37; border: 1px solid #aee5bd; }
.badge-project { background: #ddf4ff; color: #0969da; border: 1px solid #b6d9f7; }

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
    background: #ffffff; border: 1px solid #d0d7de;
    border-radius: 10px; padding: 16px;
    width: 160px; height: 160px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: space-between;
    cursor: pointer; transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 2px rgba(31, 35, 40, 0.04);
}
.proj-card:hover {
    border-color: #0969da;
    background: #f6f8fa;
    box-shadow: 0 3px 8px rgba(31, 35, 40, 0.08);
}
.proj-card-name {
    font-size: 13px; font-weight: 600; color: #1f2328;
    text-align: center; word-break: break-word;
}
.proj-card-participants { display: flex; gap: 3px; flex-wrap: wrap; justify-content: center; }

/* ── Project detail ── */
.detail-box {
    background: #ffffff; border: 1px solid #d0d7de;
    border-radius: 8px; padding: 20px;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 2px rgba(31, 35, 40, 0.04);
}
.detail-label { font-size: 11px; color: #656d76; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2px; }
.detail-value { font-size: 14px; color: #1f2328; margin-bottom: 14px; }

/* ── Phase card ── */
.phase-card {
    background: #ffffff; border: 1px solid #d0d7de;
    border-radius: 6px; padding: 12px 14px; margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 1px 2px rgba(31, 35, 40, 0.04);
}
.phase-title { font-size: 13px; font-weight: 600; color: #1f2328; margin-bottom: 4px; }
.phase-meta  { font-size: 11px; color: #656d76; }

/* ── Chat ── */
.chat-bubble {
    padding: 8px 12px; border-radius: 8px; margin-bottom: 8px;
    font-size: 13px; font-family: 'Inter', sans-serif;
    max-width: 85%;
}
.chat-bubble.mine    { background: #dafbe1; color: #1f2328; margin-left: auto; }
.chat-bubble.theirs  { background: #eaeef2; color: #1f2328; }
.chat-sender { font-size: 10px; color: #656d76; margin-bottom: 2px; }
.chat-time   { font-size: 10px; color: #656d76; margin-top: 2px; text-align: right; }

/* ── Forms ── */
.stTextInput > label, .stSelectbox > label, .stTextArea > label,
.stMultiSelect > label, .stDateInput > label {
    font-size: 13px !important; font-weight: 500 !important;
    color: #57606a !important; font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input, .stTextArea textarea {
    background-color: #ffffff !important; border: 1px solid #d0d7de !important;
    border-radius: 6px !important; color: #1f2328 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background-color: #ffffff !important; border: 1px solid #d0d7de !important;
    border-radius: 6px !important; color: #1f2328 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
.stFormSubmitButton > button {
    background-color: #1f883d !important; color: #ffffff !important;
    border: 1px solid #1a7f37 !important; border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    font-size: 13px !important; padding: 6px 20px !important;
}
.stFormSubmitButton > button:hover { background-color: #1a7f37 !important; }

.empty-state {
    text-align: center; padding: 80px 20px; color: #656d76;
    font-family: 'Inter', sans-serif; font-size: 14px;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.coming-soon {
    background: #ffffff; border: 1px solid #d0d7de; border-radius: 8px;
    padding: 40px; text-align: center; color: #656d76;
    font-family: 'Inter', sans-serif; font-size: 14px; margin-top: 16px;
}
.stAlert { background-color: #ffffff !important; border-radius: 6px !important; font-family: 'Inter', sans-serif !important; }

/* ── Delete project button ── */
[data-testid="del_project"] > button {
    background: transparent !important;
    border: 1px solid #ffcecb !important;
    border-radius: 6px !important;
    color: #cf222e !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    transition: all 0.12s !important;
}
[data-testid="del_project"] > button:hover {
    background: #ffebe9 !important;
    border-color: #cf222e !important;
}

/* ── Delete phase button ── */
[data-testid^="del_phase_"] > button {
    background: transparent !important;
    border: 1px solid #ffcecb !important;
    border-radius: 4px !important;
    color: #cf222e !important;
    font-size: 12px !important;
    height: 26px !important;
    padding: 0 !important;
    transition: all 0.12s !important;
}
[data-testid^="del_phase_"] > button:hover {
    background: #ffebe9 !important;
    border-color: #cf222e !important;
}

/* ── Phase progress buttons ── */
[data-testid^="prog_"] > button {
    background: #f6f8fa !important;
    border: 1px solid #d0d7de !important;
    border-radius: 4px !important;
    color: #656d76 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    padding: 3px 0 !important;
    height: 26px !important;
    width: 100% !important;
    transition: all 0.12s !important;
}
[data-testid^="prog_"] > button:hover {
    background: #ffffff !important;
    border-color: #0969da !important;
    color: #0969da !important;
}

/* ── Employee Info button — small compact badge ── */
[data-testid^="sel_emp_"] > button {
    background: #f6f8fa !important;
    border: 1px solid #d0d7de !important;
    border-radius: 6px !important;
    color: #57606a !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    height: 40px !important;
    width: 100% !important;
    transition: background 0.12s, color 0.12s !important;
}
[data-testid^="sel_emp_"] > button:hover {
    background: #fff0f3 !important;
    border-color: #d1493b !important;
    color: #d1493b !important;
}

/* ── Filter chips (Tasks page) ── */
.chip-row {
    display: flex; flex-wrap: wrap; gap: 6px;
    margin-bottom: 14px;
}
.chip-row .chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    border: 1px solid #d0d7de;
    background: #ffffff;
    color: #57606a;
    cursor: pointer;
    transition: all 0.12s;
    white-space: nowrap;
}
.chip-row .chip:hover { border-color: #0969da; color: #0969da; }
.chip-row .chip.active {
    background: #ddf4ff; border-color: #0969da; color: #0969da;
}
.chip-row .chip.open.active         { border-color: #0969da; color: #0969da; background: #ddf4ff; }
.chip-row .chip.progress.active     { border-color: #9a6700; color: #9a6700; background: #fff8c5; }
.chip-row .chip.done.active         { border-color: #1a7f37; color: #1a7f37; background: #dafbe1; }
.chip-row .chip.overdue.active      { border-color: #cf222e; color: #cf222e; background: #ffebe9; }
.chip-row .chip .count {
    display: inline-block;
    margin-left: 6px;
    padding: 0 6px;
    border-radius: 10px;
    font-size: 10px;
    background: #eaeef2;
    color: inherit;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATABASE — Supabase / PostgreSQL
# ─────────────────────────────────────────

def make_conn():
    """Open a PostgreSQL connection from Streamlit Secrets.

    Supports two layouts of .streamlit/secrets.toml under [database]:
      1) separate keys: host, port, user, password, dbname   (preferred)
      2) a single connection string: url
    """
    if "database" not in st.secrets:
        raise RuntimeError("The [database] section is missing from Streamlit Secrets.")
    db = st.secrets["database"]

    if "host" in db:
        missing = [k for k in ("port", "user", "password", "dbname") if k not in db]
        if missing:
            raise RuntimeError("Missing database settings in Streamlit Secrets: " + ", ".join(missing))
        return psycopg2.connect(
            host=str(db["host"]), port=int(db["port"]), user=str(db["user"]),
            password=str(db["password"]), dbname=str(db["dbname"]),
            sslmode="require", connect_timeout=15,
        )
    if "url" in db:
        return psycopg2.connect(db["url"], sslmode="require", connect_timeout=15)
    raise RuntimeError("Streamlit Secrets [database] needs either host/port/user/password/dbname or url.")

def get_conn():
    """Fresh connection per Streamlit rerun, in AUTOCOMMIT mode."""
    conn = make_conn()
    conn.autocommit = True
    return conn, conn.cursor()

# One connection per run
conn, c = get_conn()

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def qall(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchall()

def qone(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchone()

def get_now():
    """Real datetime — the *_at columns are timestamp now, not text."""
    return datetime.now()

def fmt_ts(ts):
    """Render a timestamp for display, tolerating legacy text values."""
    if ts is None:
        return ""
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M")
    return str(ts)

def log_activity(action, item_type, item_name, done_by, extra=""):
    c.execute(
        'INSERT INTO activity_log (action, item_type, item_name, done_by, done_at, extra) VALUES (%s,%s,%s,%s,%s,%s)',
        (action, item_type, item_name, done_by, get_now(), extra)
    )

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
    return f'<span class="{css_class}" style="background:{color};" title="{esc(name)}">{esc(initials)}</span>'

def avatars_row(names, size="sm"):
    return "".join(avatar_html(n, size) for n in names)

_part_cache = {}

def get_participants(project_id):
    """All participants are loaded once per page render, then served from memory."""
    if not _part_cache:
        _part_cache["__loaded__"] = True
        for pid, emp in qall(c, "SELECT project_id, employee FROM project_participants ORDER BY employee"):
            _part_cache.setdefault(pid, []).append(emp)
    return list(_part_cache.get(project_id, []))

def all_employees():
    return [r[0] for r in qall(c, "SELECT name FROM employees ORDER BY name")]

# ─────────────────────────────────────────
# TASK HELPERS
# ─────────────────────────────────────────
TASK_STATUSES      = ["Open", "In Progress", "Done"]
TASK_STATUS_COLORS = {"Open": "#0969da", "In Progress": "#9a6700", "Done": "#1a7f37"}
CAT_ICONS = {"Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢",
             "Licenses": "📄", "Bonds": "🔗", "Payroll": "💰", "Accounting": "💼"}

def as_date(d):
    if d is None or d == "":
        return None
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None

def due_info(due, status):
    """Return (label, color, is_overdue) for a task's due date."""
    d = as_date(due)
    if d is None:
        return "", "#656d76", False
    label = d.strftime("%b %d")
    if status == "Done":
        return f"Due {label}", "#656d76", False
    today = date.today()
    if d < today:
        return f"Overdue · {label}", "#cf222e", True
    if d == today:
        return "Due today", "#9a6700", False
    return f"Due {label}", "#57606a", False

def task_row_html(name, status, due, proj_id=None, proj_name=None, proj_cat=None,
                  created_by=None, show_project=True):
    """One task as a single compact line (all user text escaped)."""
    scol = TASK_STATUS_COLORS.get(status, "#57606a")
    dlabel, dcol, overdue = due_info(due, status)
    border     = "#ffcecb" if overdue else "#d0d7de"
    bg         = "#fff8f7" if overdue else "#ffffff"
    name_style = "text-decoration:line-through;color:#656d76;" if status == "Done" else "color:#1f2328;"
    h  = f'<div style="display:flex;align-items:center;gap:10px;background:{bg};border:1px solid {border};border-radius:8px;padding:10px 14px;min-height:44px;box-shadow:0 1px 2px rgba(31,35,40,0.04);">'
    h += (f'<span style="font-size:10px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;'
          f'padding:2px 8px;border-radius:20px;border:1px solid {scol};color:{scol};background:#fff;white-space:nowrap;">{esc(status)}</span>')
    h += f'<span style="font-size:13px;font-weight:600;flex:1;{name_style}">{esc(name)}</span>'
    if show_project and proj_name and proj_id:
        icon = CAT_ICONS.get(proj_cat, "📁")
        h += (f'<a href="?open_proj={int(proj_id)}" target="_self" style="text-decoration:none;font-size:11px;'
              f'color:#0969da;white-space:nowrap;">{icon} {esc(proj_name)}</a>')
    if dlabel:
        h += f'<span style="font-size:11px;font-weight:600;color:{dcol};white-space:nowrap;">{esc(dlabel)}</span>'
    if created_by:
        h += f'<span style="font-size:11px;color:#656d76;white-space:nowrap;">{esc(created_by)}</span>'
    h += '</div>'
    return h

def update_task_status(task_id, task_name, old_status, new_status):
    c.execute("UPDATE tasks SET status=%s WHERE id=%s", (new_status, task_id))
    if new_status == "Done" and old_status != "Done":
        log_activity("Completed", "Task", task_name, USERNAME)

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
if 'edit_task'         not in st.session_state: st.session_state.edit_task = None
if 'confirm_del_task'  not in st.session_state: st.session_state.confirm_del_task = None
if 'task_f_status_chip' not in st.session_state: st.session_state.task_f_status_chip = "Active"

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

# ═══════ PART 2 STARTS HERE ═══════
# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 16px 10px 16px;">
        <div style="font-size:20px;font-weight:800;color:#1f2328;
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

    _overdue_count = qone(c,
        "SELECT COUNT(*) FROM tasks WHERE status <> 'Done' AND due_date < %s",
        (date.today(),)
    )[0] or 0
    tasks_label = f"✅  Tasks  ({_overdue_count})" if _overdue_count > 0 else "✅  Tasks"
    if st.button(tasks_label, use_container_width=True, key="nav_Tasks"):
        st.session_state.page = "Tasks"
        st.session_state.active_project = None
        st.session_state.edit_task = None
        st.session_state.confirm_del_task = None

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

    today      = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_days  = [week_start + timedelta(days=i) for i in range(7)]
    DAY_NAMES  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    all_projects = qall(c,
        "SELECT id, name, start_date, category FROM projects WHERE start_date IS NOT NULL"
    )
    CAL_ICONS = {"Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢",
                 "Licenses": "📄", "Bonds": "🔗", "Payroll": "💰"}

    cal_cols = st.columns(7)
    for col_idx, day in enumerate(week_days):
        is_today   = (day == today)
        day_label  = DAY_NAMES[col_idx]
        day_num    = day.strftime("%d")

        header_bg    = "#FA8072" if is_today else "#ffffff"
        header_color = "#ffffff" if is_today else "#57606a"
        border_color = "#FA8072" if is_today else "#d0d7de"

        day_projects = [(pid, pname, pcat) for pid, pname, pstart, pcat in all_projects
                        if as_date(pstart) == day]

        proj_items = ""
        for pid, pname, pcat in day_projects:
            parts      = get_participants(pid)
            av_html    = "".join(avatar_html(p, "sm") for p in parts[:3])
            short_name = pname[:13] + "…" if len(pname) > 13 else pname
            cat_icon   = CAL_ICONS.get(pcat, "📁")
            proj_items += (
                f'<a href="?open_proj={pid}" target="_self" style="text-decoration:none;">'
                f'<div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:5px;'
                f'padding:5px 6px;margin-top:4px;cursor:pointer;">'
                f'<div style="font-size:10px;font-weight:600;color:#1f2328;margin-bottom:3px;">'
                f'{cat_icon} {esc(short_name)}</div>'
                f'<div style="display:flex;gap:2px;">{av_html}</div>'
                f'</div></a>'
            )

        if not proj_items:
            proj_items = '<div style="font-size:10px;color:#656d76;margin-top:6px;text-align:center;">—</div>'

        cal_cols[col_idx].markdown(
            f'<div style="background:{header_bg};border:1px solid {border_color};border-radius:8px;'
            f'padding:8px 6px;min-height:100px;box-shadow:0 1px 2px rgba(31,35,40,0.04);">'
            f'<div style="font-size:10px;font-weight:700;color:{header_color};text-transform:uppercase;'
            f'letter-spacing:0.08em;text-align:center;">{day_label}</div>'
            f'<div style="font-size:16px;font-weight:700;color:{header_color};text-align:center;margin-bottom:4px;">{day_num}</div>'
            f'{proj_items}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    feed_col, status_col = st.columns([3, 1], gap="large")

    with feed_col:
        st.markdown("<div style='font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:#656d76;margin-bottom:10px;'>Recent Activity</div>", unsafe_allow_html=True)

        logs = qall(c,
            "SELECT action, item_type, item_name, done_by, done_at, extra FROM activity_log ORDER BY done_at DESC, id DESC"
        )

        if not logs:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                Nothing here yet.<br>Create a project or task to get started.
            </div>
            """, unsafe_allow_html=True)
        else:
            CATEGORY_ICONS = {
                "Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢",
                "Licenses": "📄", "Bonds": "🔗", "Accounting": "💼", "Payroll": "💰",
            }
            feed_html = '<div>'
            for action, item_type, item_name, done_by, done_at, extra in logs:
                creator_av   = avatar_html(done_by, "sm")
                cat_icon     = ""
                part_av_html = ""
                if extra and item_type == "Project":
                    if "|" in extra:
                        cat_part, names_part = extra.split("|", 1)
                        cat_icon = CATEGORY_ICONS.get(cat_part.strip(), "📁") + " "
                        names = [n.strip() for n in names_part.split(",") if n.strip()]
                    else:
                        names = [n.strip() for n in extra.split(",") if n.strip()]
                    part_av_html = "".join(avatar_html(n, "sm") for n in names[:5])

                done_at_s   = fmt_ts(done_at)
                badge_class = "badge-project" if item_type == "Project" else "badge-task"
                card  = '<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:8px;padding:12px 16px;margin-bottom:6px;box-shadow:0 1px 2px rgba(31,35,40,0.04);">'
                card += (
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                    f'<span style="font-size:16px;">{cat_icon}</span>'
                    f'<span class="badge {badge_class}">{item_type}</span>'
                    f'<span style="font-size:14px;font-weight:600;color:#1f2328;flex:1;">{esc(item_name)}</span>'
                    f'</div>'
                )
                card += '<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">'
                card += f'<span style="font-size:11px;color:#656d76;">{esc(action)} by</span>'
                card += creator_av
                card += f'<span style="font-size:11px;color:#57606a;font-weight:600;">{esc(done_by)}</span>'
                card += f'<span style="font-size:11px;color:#656d76;">· {done_at_s}</span>'
                if part_av_html:
                    card += f'<span style="display:inline-flex;gap:3px;margin-left:8px;">{part_av_html}</span>'
                card += '</div></div>'
                feed_html += card
            feed_html += '</div>'
            st.markdown(feed_html, unsafe_allow_html=True)

    with status_col:
        st.markdown(
            '<div style="font-size:11px;font-weight:600;text-transform:uppercase;'
            'letter-spacing:0.08em;color:#656d76;margin-bottom:10px;">🟢 Field Status</div>',
            unsafe_allow_html=True
        )

        try:
            all_emps    = qall(c, "SELECT name FROM employees ORDER BY name")
            clocked_in  = []
            clocked_out = []

            latest_by_emp = {
                r[0]: r for r in qall(c,
                    "SELECT DISTINCT ON (employee) employee, event_type, project_id, created_at "
                    "FROM clock_events ORDER BY employee, created_at DESC"
                )
            }
            proj_lookup = {
                r[0]: (r[1], r[2]) for r in qall(c, "SELECT id, name, category FROM projects")
            }
            for (emp_name,) in all_emps:
                latest = latest_by_emp.get(emp_name)
                if latest and latest[1] == "clock_in":
                    proj = proj_lookup.get(latest[2]) if latest[2] else None
                    clocked_in.append((emp_name, proj, latest[3]))
                else:
                    clocked_out.append(emp_name)

            status_html = '<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:8px;padding:12px;min-height:200px;box-shadow:0 1px 2px rgba(31,35,40,0.04);">'

            if clocked_in:
                for emp_name, proj, clock_time in clocked_in:
                    av        = avatar_html(emp_name, "sm")
                    proj_name = proj[0] if proj else "Unknown project"
                    proj_cat  = proj[1] if proj else ""
                    cat_icon  = {"Explorations":"🔭","Residential":"🏡","Commercial":"🏢"}.get(proj_cat, "📁")
                    try:
                        clocked_at = (clock_time if isinstance(clock_time, datetime)
                                      else datetime.strptime(str(clock_time), "%Y-%m-%d %H:%M"))
                        elapsed    = datetime.now() - clocked_at
                        hrs, mins  = divmod(int(elapsed.total_seconds() // 60), 60)
                        since      = f"{hrs}h {mins}m" if hrs else f"{mins}m"
                    except Exception:
                        since = str(clock_time)
                    status_html += (
                        '<div style="display:flex;align-items:center;gap:8px;'
                        'padding:7px 0;border-bottom:1px solid #eaeef2;">'
                        f'{av}'
                        '<div style="flex:1;min-width:0;">'
                        f'<div style="font-size:12px;font-weight:600;color:#1f2328;'
                        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{esc(emp_name)}</div>'
                        f'<div style="font-size:10px;color:#1a7f37;">{cat_icon} {esc(proj_name)}</div>'
                        f'<div style="font-size:10px;color:#656d76;">{since} ago</div>'
                        '</div>'
                        '<div style="width:8px;height:8px;border-radius:50%;background:#1a7f37;'
                        'box-shadow:0 0 6px #1a7f3755;flex-shrink:0;"></div>'
                        '</div>'
                    )
            else:
                status_html += (
                    '<div style="font-size:12px;color:#656d76;text-align:center;padding:20px 0;">'
                    '👷 No one clocked in yet</div>'
                )

            if clocked_out:
                status_html += (
                    '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                    'letter-spacing:0.08em;color:#656d76;margin-top:14px;margin-bottom:6px;">Off</div>'
                )
                for emp_name in clocked_out:
                    av = avatar_html(emp_name, "sm")
                    status_html += (
                        '<div style="display:flex;align-items:center;gap:6px;padding:4px 0;opacity:0.5;">'
                        f'{av}'
                        f'<span style="font-size:11px;color:#656d76;">{esc(emp_name)}</span>'
                        '</div>'
                    )

            status_html += '</div>'
            st.markdown(status_html, unsafe_allow_html=True)

        except Exception as e:
            if "clock_events" in str(e):
                st.markdown(
                    '<div style="background:#ffffff;border:1px solid #d0d7de;border-radius:8px;'
                    'padding:20px;text-align:center;color:#656d76;font-size:12px;">'
                    '📱 ClockBox not connected yet.<br>'
                    '<span style="font-size:10px;">Run setup.sql in Supabase to enable.</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div style="background:#ffffff;border:1px solid #ffcecb;border-radius:8px;'
                    f'padding:12px;color:#cf222e;font-size:11px;">Field status error: {esc(str(e))}</div>',
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════
# NEW TASK
# ══════════════════════════════════════════
elif page == "New Task":
    st.markdown("<div class='page-title'>＋ New Task</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Add a new task to track.</div>", unsafe_allow_html=True)

    projects      = qall(c, "SELECT id, name FROM projects ORDER BY name")
    proj_names    = {pid: pname for pid, pname in projects}
    proj_options  = [None] + [pid for pid, _ in projects]

    with st.form("form_new_task", clear_on_submit=True):
        task_name   = st.text_input("Task Name")
        proj_choice = st.selectbox("Link to Project (optional)", proj_options,
                                   format_func=lambda v: "— None —" if v is None else proj_names.get(v, "?"))
        status      = st.selectbox("Status", TASK_STATUSES)
        due_date    = st.date_input("Due date (optional)", value=None)
        submitted   = st.form_submit_button("Create Task")

    if submitted:
        if task_name.strip():
            c.execute(
                'INSERT INTO tasks (task_name, project_id, status, created_by, created_at, due_date) VALUES (%s,%s,%s,%s,%s,%s)',
                (task_name.strip(), proj_choice, status, USERNAME, get_now(), due_date)
            )
            log_activity("Created", "Task", task_name.strip(), USERNAME)
            st.session_state.page = "Tasks"
            st.rerun()
        else:
            st.warning("Please enter a task name.")

# ══════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════
elif page == "Tasks":
    st.markdown("<div class='page-title'>✅ Tasks</div>", unsafe_allow_html=True)

    status_counts = dict(qall(c, "SELECT status, COUNT(*) FROM tasks GROUP BY status"))
    overdue_n     = qone(c, "SELECT COUNT(*) FROM tasks WHERE status <> 'Done' AND due_date < %s", (date.today(),))[0]
    chips = ""
    for label, n, col in [("Open", status_counts.get("Open", 0), "#0969da"),
                          ("In progress", status_counts.get("In Progress", 0), "#9a6700"),
                          ("Done", status_counts.get("Done", 0), "#1a7f37"),
                          ("Overdue", overdue_n, "#cf222e")]:
        chips += (f'<span style="display:inline-block;margin-right:8px;padding:3px 12px;border-radius:20px;'
                  f'border:1px solid {col};color:{col};font-size:11px;font-weight:700;background:#fff;">{n} {label}</span>')
    st.markdown(f"<div class='page-subtitle' style='margin-bottom:16px;'>{chips}</div>", unsafe_allow_html=True)

    projects_all = qall(c, "SELECT id, name FROM projects ORDER BY name")
    proj_names   = {pid: pname for pid, pname in projects_all}

# ═══════ PART 3 STARTS HERE ═══════

    # ── Edit panel (opens when ✏️ is clicked) ──
    edit_id = st.session_state.get("edit_task")
    if edit_id:
        erow = qone(c, "SELECT task_name, project_id, status, due_date FROM tasks WHERE id=%s", (edit_id,))
        if erow:
            e_options = [None] + [pid for pid, _ in projects_all]
            with st.form("form_edit_task"):
                st.markdown("**Edit task**")
                e_name   = st.text_input("Task name", value=erow[0])
                e_proj   = st.selectbox("Project", e_options,
                                        index=e_options.index(erow[1]) if erow[1] in e_options else 0,
                                        format_func=lambda v: "— None —" if v is None else proj_names.get(v, "?"))
                e_status = st.selectbox("Status", TASK_STATUSES,
                                        index=TASK_STATUSES.index(erow[2]) if erow[2] in TASK_STATUSES else 0)
                e_due    = st.date_input("Due date (optional)", value=as_date(erow[3]))
                b1, b2   = st.columns(2)
                save_edit   = b1.form_submit_button("Save changes")
                cancel_edit = b2.form_submit_button("Cancel")
            if cancel_edit:
                st.session_state.edit_task = None
                st.rerun()
            if save_edit:
                if e_name.strip():
                    c.execute("UPDATE tasks SET task_name=%s, project_id=%s, status=%s, due_date=%s WHERE id=%s",
                              (e_name.strip(), e_proj, e_status, e_due, edit_id))
                    if e_status == "Done" and erow[2] != "Done":
                        log_activity("Completed", "Task", e_name.strip(), USERNAME)
                    st.session_state.edit_task = None
                    st.rerun()
                else:
                    st.warning("Please enter a task name.")
        else:
            st.session_state.edit_task = None

    # ── Delete confirmation (opens when 🗑️ is clicked) ──
    del_id = st.session_state.get("confirm_del_task")
    if del_id:
        drow = qone(c, "SELECT task_name FROM tasks WHERE id=%s", (del_id,))
        if drow:
            st.warning(f"Delete the task \"{esc(drow[0])}\" permanently?")
            d1, d2 = st.columns(2)
            if d1.button("Yes, delete it", key="task_del_yes"):
                c.execute("DELETE FROM tasks WHERE id=%s", (del_id,))
                st.session_state.confirm_del_task = None
                st.rerun()
            if d2.button("Cancel", key="task_del_no"):
                st.session_state.confirm_del_task = None
                st.rerun()
        else:
            st.session_state.confirm_del_task = None

    # ── Status chips (visual) ──
    status_filter = st.session_state.get("task_f_status_chip", "Active")
    chips_def = [
        ("Active",      "Active",       "chip"),
        ("Open",        "Open",         "chip open"),
        ("In Progress", "In Progress",  "chip progress"),
        ("Done",        "Done",         "chip done"),
        ("Overdue",     "Overdue",      "chip overdue"),
        ("All",         "All",          "chip"),
    ]
    chip_html = "<div class='chip-row'>"
    for key, label, cls in chips_def:
        is_active = (status_filter == key)
        if key == "Active":
            cnt = status_counts.get("Open", 0) + status_counts.get("In Progress", 0)
        elif key == "Overdue":
            cnt = overdue_n
        elif key in status_counts:
            cnt = status_counts[key]
        else:
            cnt = 0
        chip_cls = cls + (" active" if is_active else "")
        chip_html += f"<span class='{chip_cls}'>{label}<span class='count'>{cnt}</span></span>"
    chip_html += "</div>"
    st.markdown(chip_html, unsafe_allow_html=True)

    chip_cols = st.columns(len(chips_def))
    for i, (key, label, _cls) in enumerate(chips_def):
        if chip_cols[i].button(label, key=f"task_chip_{key}", use_container_width=True):
            st.session_state.task_f_status_chip = key
            st.rerun()

    # ── Secondary filters ──
    f1, f2, f3, f4 = st.columns([3, 2, 3, 2])
    proj_filter = f1.selectbox("Project", ["All projects", "No project"] + [pid for pid, _ in projects_all],
                               format_func=lambda v: v if isinstance(v, str) else proj_names.get(v, "?"),
                               key="task_f_proj")
    due_filter  = f2.selectbox("Due", ["Any", "Due today", "Due this week", "Overdue only"], key="task_f_due")
    search_text = f3.text_input("Search", placeholder="Search tasks…", key="task_f_search")
    sort_by     = f4.selectbox("Sort", ["Due date", "Recently added", "Alphabetical"], key="task_f_sort")

    where, params = [], []
    if status_filter == "Active":
        where.append("t.status <> 'Done'")
    elif status_filter in ("Open", "In Progress", "Done"):
        where.append("t.status = %s"); params.append(status_filter)
    if status_filter == "Overdue":
        where.append("t.status <> 'Done' AND t.due_date < %s"); params.append(date.today())

    if proj_filter == "No project":
        where.append("t.project_id IS NULL")
    elif proj_filter != "All projects":
        where.append("t.project_id = %s"); params.append(proj_filter)

    today_d = date.today()
    if due_filter == "Due today":
        where.append("t.due_date = %s"); params.append(today_d)
    elif due_filter == "Due this week":
        where.append("t.due_date >= %s AND t.due_date <= %s")
        params.extend([today_d, today_d + timedelta(days=7)])
    elif due_filter == "Overdue only":
        where.append("t.status <> 'Done' AND t.due_date < %s"); params.append(today_d)

    if search_text.strip():
        pat = search_text.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        where.append("t.task_name ILIKE %s"); params.append("%" + pat + "%")

    order_clauses = {
        "Due date":       "(t.status = 'Done'), t.due_date NULLS LAST, t.id DESC",
        "Recently added": "t.id DESC",
        "Alphabetical":   "t.task_name ASC",
    }
    order_by = order_clauses.get(sort_by, order_clauses["Due date"])

    sql = ("SELECT t.id, t.task_name, t.status, t.due_date, t.created_by, t.project_id, p.name, p.category "
           "FROM tasks t LEFT JOIN projects p ON p.id = t.project_id")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY " + order_by
    tasks = qall(c, sql, tuple(params))

    st.markdown("<br>", unsafe_allow_html=True)
    if not tasks:
        st.markdown("""
        <div class="empty-state" style="padding:50px 20px;">
            <div class="empty-icon">✅</div>
            No tasks match.<br>Use <strong style="color:#1a7f37">＋ New Task</strong> to add one.
        </div>
        """, unsafe_allow_html=True)
    else:
        MAX_SHOWN = 60
        for tid, tname, tstatus, tdue, tby, tpid, tpname, tpcat in tasks[:MAX_SHOWN]:
            col_card, col_stat, col_edit, col_del = st.columns([7, 2, 1, 1])
            col_card.markdown(task_row_html(tname, tstatus, tdue, tpid, tpname, tpcat, tby), unsafe_allow_html=True)
            cur_idx    = TASK_STATUSES.index(tstatus) if tstatus in TASK_STATUSES else 0
            new_status = col_stat.selectbox("Status", TASK_STATUSES, index=cur_idx,
                                            key=f"tstat_{tid}", label_visibility="collapsed")
            if new_status != TASK_STATUSES[cur_idx]:
                update_task_status(tid, tname, tstatus, new_status)
                st.rerun()
            if col_edit.button("✏️", key=f"tedit_{tid}", help="Edit task"):
                st.session_state.edit_task = tid
                st.session_state.confirm_del_task = None
                st.rerun()
            if col_del.button("🗑️", key=f"tdel_{tid}", help="Delete task"):
                st.session_state.confirm_del_task = tid
                st.session_state.edit_task = None
                st.rerun()
        if len(tasks) > MAX_SHOWN:
            st.caption(f"Showing the first {MAX_SHOWN} of {len(tasks)} tasks — use the filters to narrow the list.")

# ══════════════════════════════════════════
# NEW PROJECT
# ══════════════════════════════════════════
elif page == "New Project":
    st.markdown("<div class='page-title'>＋ New Project</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Fill in the details to start a new project.</div>", unsafe_allow_html=True)

    emp_list = all_employees()

    with st.form("form_new_proj", clear_on_submit=True):
        proj_name    = st.text_input("Project Name")
        proj_cat     = st.selectbox("Category", [
            "Commercial", "Residential", "Explorations",
            "Licenses", "Bonds", "Accounting", "Payroll"
        ])
        est_duration  = st.text_input("Estimated Duration (e.g. 3 months)")
        start_date    = st.date_input("Starting Date")
        proj_customer = st.text_input("Customer / Client (optional)")
        proj_address  = st.text_input("Address (optional)")

        st.markdown("<div style='font-size:13px;font-weight:500;color:#57606a;margin-top:8px;margin-bottom:6px;'>Participants</div>", unsafe_allow_html=True)
        selected_emps = []
        cols_per_row = 4
        emp_rows = [emp_list[i:i+cols_per_row] for i in range(0, len(emp_list), cols_per_row)]
        for row in emp_rows:
            row_cols = st.columns(cols_per_row)
            for idx, emp in enumerate(row):
                checked = row_cols[idx].checkbox(emp, key=f"chk_{emp}", value=(emp == USERNAME))
                if checked:
                    selected_emps.append(emp)

        submitted = st.form_submit_button("Create Project")

    if submitted:
        if proj_name.strip():
            addr_val = proj_address.strip() if proj_cat in ("Commercial","Residential","Explorations") else ""
            cust_val = proj_customer.strip() if proj_cat in ("Commercial","Residential","Explorations") else ""
            all_parts = list(selected_emps)
            if USERNAME not in all_parts:
                all_parts.append(USERNAME)

            conn.autocommit = False
            try:
                c.execute(
                    '''INSERT INTO projects (name, category, est_duration, start_date, created_by, created_at, address, customer)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id''',
                    (proj_name.strip(), proj_cat, est_duration.strip(),
                     start_date, USERNAME, get_now(), addr_val, cust_val)
                )
                proj_id = c.fetchone()[0]
                for emp in all_parts:
                    c.execute(
                        "INSERT INTO project_participants (project_id, employee) VALUES (%s,%s)",
                        (proj_id, emp)
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                st.error("Could not create the project. Please try again.")
                st.stop()
            finally:
                conn.autocommit = True

            log_activity("Created", "Project", proj_name.strip(), USERNAME,
                         extra=proj_cat + "|" + ",".join(all_parts))

            st.session_state.participants = []
            st.session_state.page = "Main Feed"
            st.rerun()
        else:
            st.warning("Please enter a project name.")

# ═══════ PART 4 STARTS HERE ═══════

# ══════════════════════════════════════════
# PROJECT DETAIL PAGE
# ══════════════════════════════════════════
elif page == "Project Detail" and st.session_state.active_project:
    proj_id = st.session_state.active_project
    proj = qone(c,
        "SELECT name, category, est_duration, start_date, created_by, created_at, address, customer FROM projects WHERE id=%s",
        (proj_id,)
    )

    if not proj:
        st.error("Project not found.")
    else:
        name, category, est_duration, start_date, created_by, created_at, address, customer = proj
        participants = get_participants(proj_id)

        if st.button("← Back", key="back_btn"):
            st.session_state.page = category
            st.session_state.active_project = None
            st.rerun()

        st.markdown(f"<div class='page-title'>📁 {esc(name)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='page-subtitle'>{esc(category)}</div>", unsafe_allow_html=True)

        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            part_html       = "".join(avatar_html(p, "sm") for p in participants)
            part_names_html = "".join(
                f'<span style="font-size:11px;color:#57606a;align-self:center;">{esc(p)}</span>'
                for p in participants
            )
            box = '<div class="detail-box">'
            box += f'<div class="detail-label">Category</div><div class="detail-value">{esc(category)}</div>'
            if customer:
                box += f'<div class="detail-label">Customer</div><div class="detail-value">{esc(customer)}</div>'
            if address:
                box += f'<div class="detail-label">Address</div><div class="detail-value">{esc(address)}</div>'
            box += f'<div class="detail-label">Estimated Duration</div><div class="detail-value">{esc(est_duration) or "—"}</div>'
            box += f'<div class="detail-label">Starting Date</div><div class="detail-value">{as_date(start_date) or "—"}</div>'
            box += f'<div class="detail-label">Created By</div><div class="detail-value">{esc(created_by)}</div>'
            box += f'<div class="detail-label">Created At</div><div class="detail-value">{fmt_ts(created_at)}</div>'
            box += '<div class="detail-label">Participants</div>'
            box += '<div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">'
            box += part_html + part_names_html
            box += '</div></div>'
            st.markdown(box, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**Project Phases**")
            phases = qall(c,
                """SELECT p.id, p.phase_name, p.equipment, p.comments, p.added_by, p.added_at,
                          pp.status AS latest_status, pp.updated_by, pp.updated_at
                   FROM phases p
                   LEFT JOIN LATERAL (
                       SELECT status, updated_by, updated_at
                       FROM phase_progress
                       WHERE phase_id = p.id
                       ORDER BY updated_at DESC, id DESC
                       LIMIT 1
                   ) pp ON TRUE
                   WHERE p.project_id = %s
                   ORDER BY p.added_at, p.id""",
                (proj_id,)
            )

            PROGRESS_STEPS = ["Started", "25%", "50%", "75%", "Finished"]
            PROGRESS_COLORS = {
                "Started":  "#0969da",
                "25%":      "#9a6700",
                "50%":      "#9a6700",
                "75%":      "#1a7f37",
                "Finished": "#1a7f37",
            }

            if phases:
                for (ph_id, ph_name, ph_equip, ph_comment, ph_by, ph_at,
                     latest_status, latest_by, latest_at) in phases:

                    current_status = latest_status
                    equip_str      = ph_equip.strip()   if ph_equip   else ""
                    comment_str    = ph_comment.strip() if ph_comment else ""

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
                                f'<span style="background:#f6f8fa;color:#656d76;font-size:10px;'
                                f'font-weight:600;padding:4px 10px;border-radius:4px;'
                                f'border:1px solid #d0d7de;">{step}</span> '
                            )

                    if latest_status:
                        prog_color       = PROGRESS_COLORS[latest_status]
                        last_update_html = (
                            f'<div style="font-size:11px;color:#656d76;margin-top:6px;">'
                            f'Last updated to <span style="color:{prog_color};font-weight:600;">'
                            f'{esc(latest_status)}</span> by '
                            f'<span style="color:#57606a;font-weight:600;">{esc(latest_by)}</span>'
                            f' &middot; {fmt_ts(latest_at)}</div>'
                        )
                    else:
                        last_update_html = '<div style="font-size:11px;color:#656d76;margin-top:6px;">Not started yet.</div>'

                    card_html = (
                        '<div class="phase-card">'
                          '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">'
                            f'<div style="font-size:13px;font-weight:700;color:#1f2328;">📌 {esc(ph_name)}</div>'
                            f'<div style="font-size:10px;color:#656d76;text-align:right;">'
                              f'Created by <span style="color:#57606a;font-weight:600;">{esc(ph_by)}</span>'
                              f'<br>{fmt_ts(ph_at)}'
                            f'</div>'
                          '</div>'
                    )
                    if equip_str:
                        card_html += (
                            f'<div style="font-size:12px;color:#57606a;margin-bottom:4px;">'
                            f'🔧 <strong>Equipment:</strong> {esc(equip_str)}</div>'
                        )
                    if comment_str:
                        card_html += (
                            f'<div style="font-size:12px;color:#57606a;margin-bottom:4px;">'
                            f'💬 <strong>Comments:</strong> {esc(comment_str)}</div>'
                        )
                    card_html += (
                        '<div style="margin-top:12px;">'
                          '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                               'letter-spacing:0.08em;color:#656d76;margin-bottom:6px;">Progress</div>'
                          f'<div style="display:flex;gap:5px;flex-wrap:wrap;">{pills_html}</div>'
                          f'{last_update_html}'
                        '</div>'
                        '</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    if USERNAME in participants:
                        prog_cols = st.columns(len(PROGRESS_STEPS) + 1)
                        for i, step in enumerate(PROGRESS_STEPS):
                            if prog_cols[i].button(step, key=f"prog_{ph_id}_{step}"):
                                c.execute(
                                    "INSERT INTO phase_progress (phase_id, status, updated_by, updated_at) VALUES (%s,%s,%s,%s)",
                                    (ph_id, step, USERNAME, get_now())
                                )
                                st.rerun()
                        if prog_cols[-1].button("🗑️", key=f"del_phase_{ph_id}", help="Delete this phase"):
                            c.execute("DELETE FROM phases WHERE id=%s", (ph_id,))
                            st.rerun()
                        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#656d76;font-size:13px;'>No phases yet.</div>", unsafe_allow_html=True)

            if USERNAME in participants:
                st.markdown("<br>**Add a Phase**", unsafe_allow_html=True)
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
                    st.rerun()
            else:
                st.caption("Only project participants can add phases.")

            st.markdown("<br>**Tasks**", unsafe_allow_html=True)
            ptasks = qall(c,
                "SELECT id, task_name, status, due_date, created_by FROM tasks WHERE project_id=%s "
                "ORDER BY (status = 'Done'), due_date NULLS LAST, id DESC",
                (proj_id,)
            )
            if ptasks:
                for tid, tname, tstatus, tdue, tby in ptasks:
                    tc1, tc2 = st.columns([3, 1])
                    tc1.markdown(task_row_html(tname, tstatus, tdue, created_by=tby, show_project=False),
                                 unsafe_allow_html=True)
                    if USERNAME in participants:
                        cur_idx    = TASK_STATUSES.index(tstatus) if tstatus in TASK_STATUSES else 0
                        new_status = tc2.selectbox("Status", TASK_STATUSES, index=cur_idx,
                                                   key=f"ptstat_{tid}", label_visibility="collapsed")
                        if new_status != TASK_STATUSES[cur_idx]:
                            update_task_status(tid, tname, tstatus, new_status)
                            st.rerun()
            else:
                st.markdown("<div style='color:#656d76;font-size:13px;'>No tasks yet.</div>", unsafe_allow_html=True)

            if USERNAME in participants:
                with st.form("form_proj_task", clear_on_submit=True):
                    pt_name   = st.text_input("New task")
                    pt_due    = st.date_input("Due date (optional)", value=None)
                    pt_submit = st.form_submit_button("Add Task")
                if pt_submit and pt_name.strip():
                    c.execute(
                        "INSERT INTO tasks (task_name, project_id, status, created_by, created_at, due_date) VALUES (%s,%s,%s,%s,%s,%s)",
                        (pt_name.strip(), proj_id, "Open", USERNAME, get_now(), pt_due)
                    )
                    log_activity("Created", "Task", pt_name.strip(), USERNAME)
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#d0d7de;'>", unsafe_allow_html=True)

            proj_status  = qone(c, "SELECT completed, completed_by, completed_at FROM projects WHERE id=%s", (proj_id,))
            is_completed = proj_status and proj_status[0] is True

            if is_completed:
                st.markdown(
                    f'<div style="background:#dafbe1;border:1px solid #aee5bd;border-radius:6px;'
                    f'padding:10px 14px;font-size:12px;color:#1a7f37;margin-bottom:8px;">'
                    f'✅ Completed by <strong>{esc(proj_status[1])}</strong> · {fmt_ts(proj_status[2])}</div>',
                    unsafe_allow_html=True
                )
            elif USERNAME in participants:
                if st.button("✅  Mark as Complete", key="complete_project", use_container_width=True):
                    now = get_now()
                    conn.autocommit = False
                    try:
                        c.execute(
                            "UPDATE projects SET completed=TRUE, completed_by=%s, completed_at=%s WHERE id=%s",
                            (USERNAME, now, proj_id)
                        )
                        log_activity("Completed", "Project", name, USERNAME)
                        if category in ("Explorations", "Residential", "Commercial"):
                            proj_creator = qone(c, "SELECT created_by FROM projects WHERE id=%s", (proj_id,))[0]
                            c.execute(
                                "INSERT INTO accounting (project_id, project_name, category, created_by, completed_by, completed_at) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (project_id) DO NOTHING",
                                (proj_id, name, category, proj_creator, USERNAME, now)
                            )
                        conn.commit()
                    except Exception:
                        conn.rollback()
                        st.error("Could not complete the project. Please try again.")
                        st.stop()
                    finally:
                        conn.autocommit = True
                    st.rerun()

            if USERNAME in participants:
                if st.button("🗑️  Delete Project", key="del_project", use_container_width=True):
                    st.session_state.confirm_delete = True

                if st.session_state.get("confirm_delete"):
                    st.warning("⚠️ Are you sure? This will permanently delete the project and everything under it.")
                    c1, c2 = st.columns(2)
                    if c1.button("Yes, delete it", key="confirm_del_yes"):
                        c.execute("DELETE FROM projects WHERE id=%s", (proj_id,))
                        st.session_state.confirm_delete    = False
                        st.session_state.active_project    = None
                        st.session_state.page              = category
                        st.rerun()
                    if c2.button("Cancel", key="confirm_del_no"):
                        st.session_state.confirm_delete = False
                        st.rerun()

        with right_col:

            timeline_phases = qall(c,
                """SELECT p.id, p.phase_name, pp.status
                   FROM phases p
                   LEFT JOIN LATERAL (
                       SELECT status FROM phase_progress
                       WHERE phase_id = p.id
                       ORDER BY updated_at DESC, id DESC
                       LIMIT 1
                   ) pp ON TRUE
                   WHERE p.project_id = %s
                   ORDER BY p.added_at, p.id""",
                (proj_id,)
            )

            if timeline_phases:
                timeline_html = (
                    '<div style="margin-bottom:20px;">'
                    '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                         'letter-spacing:0.08em;color:#656d76;margin-bottom:12px;">Phase Timeline</div>'
                    '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0;">'
                )
                for t_idx, (t_id, t_name, t_status) in enumerate(timeline_phases):
                    if t_status == "Finished":
                        ball_color  = "#0969da"
                        label_color = "#0969da"
                        ring        = "#0969da"
                    elif t_status in ("Started", "25%", "50%", "75%"):
                        ball_color  = "#1a7f37"
                        label_color = "#1a7f37"
                        ring        = "#1a7f37"
                    else:
                        ball_color  = "#eaeef2"
                        label_color = "#656d76"
                        ring        = "#d0d7de"

                    connector = ""
                    if t_idx < len(timeline_phases) - 1:
                        connector = '<div style="flex:1;height:2px;background:#d0d7de;min-width:16px;max-width:40px;"></div>'

                    timeline_html += (
                        '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                          f'<div style="width:14px;height:14px;border-radius:50%;'
                               f'background:{ball_color};border:2px solid {ring};"></div>'
                          f'<div style="font-size:9px;color:{label_color};font-weight:600;'
                               f'text-align:center;max-width:60px;line-height:1.2;">{esc(t_name)}</div>'
                        '</div>'
                        + connector
                    )
                timeline_html += '</div></div>'
                st.markdown(timeline_html, unsafe_allow_html=True)

            st.markdown("**Project Chat**")

            messages = qall(c,
                "SELECT sender, message, sent_at FROM chat_messages WHERE project_id=%s ORDER BY sent_at, id",
                (proj_id,)
            )

            chat_html = "<div style='height:360px;overflow-y:auto;padding:8px;background:#ffffff;border:1px solid #d0d7de;border-radius:8px;margin-bottom:12px;'>"
            if messages:
                for sender, message, sent_at in messages:
                    bubble_class = "mine" if sender == USERNAME else "theirs"
                    align        = "flex-end" if sender == USERNAME else "flex-start"
                    av           = avatar_html(sender, "sm")
                    chat_html += (
                        f'<div style="display:flex;flex-direction:column;align-items:{align};margin-bottom:8px;">'
                        f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">'
                        f'{av}'
                        f'<span style="font-size:10px;color:#656d76;">{esc(sender)} · {fmt_ts(sent_at)}</span>'
                        f'</div>'
                        f'<div class="chat-bubble {bubble_class}">{esc(message)}</div>'
                        f'</div>'
                    )
            else:
                chat_html += "<div style='text-align:center;color:#656d76;font-size:13px;padding:40px 0;'>No messages yet. Start the conversation!</div>"
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
        rows = qall(c,
            "SELECT id, name, created_by FROM projects WHERE category=%s AND completed IS NOT TRUE ORDER BY created_at DESC, id DESC",
            (page,)
        )

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
                                <div class="proj-card-name">{esc(pname)}</div>
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
                Use <strong style="color:#1a7f37">＋ New Project</strong> to add one.
            </div>
            """, unsafe_allow_html=True)

        completed_rows = qall(c,
            "SELECT id, name, created_by, completed_by, completed_at FROM projects WHERE category=%s AND completed IS TRUE ORDER BY completed_at DESC",
            (page,)
        )

        if completed_rows:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:11px;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.08em;color:#656d76;margin-bottom:10px;">Completed Projects</div>',
                unsafe_allow_html=True
            )
            completed_html = ""
            for cpid, cpname, ccreator, cby, cat2 in completed_rows:
                cparts   = get_participants(cpid)
                av_html  = "".join(avatar_html(p, "sm") for p in cparts[:5])
                completed_html += (
                    f'<a href="?open_proj={cpid}" target="_self" style="text-decoration:none;">'
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'background:#ffffff;border:1px solid #d0d7de;border-radius:6px;'
                    f'padding:8px 14px;margin-bottom:5px;cursor:pointer;'
                    f'box-shadow:0 1px 2px rgba(31,35,40,0.04);">'
                    f'<span style="font-size:11px;background:#dafbe1;color:#1a7f37;border:1px solid #aee5bd;'
                    f'border-radius:20px;padding:2px 8px;font-weight:700;">DONE</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#57606a;flex:1;">{esc(cpname)}</span>'
                    f'<span style="display:flex;gap:3px;">{av_html}</span>'
                    f'<span style="font-size:11px;color:#656d76;">Completed by '
                    f'<strong style="color:#57606a">{esc(cby)}</strong> · {fmt_ts(cat2)}</span>'
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

    acc_rows = qall(c,
        "SELECT id, project_id, project_name, category, created_by, completed_by, completed_at, billed, received FROM accounting ORDER BY completed_at DESC"
    )

    if not acc_rows:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💼</div>
            No completed projects yet.<br>
            Complete a project to see it here.
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.session_state.get("active_accounting"):
            acc_id = st.session_state.active_accounting
            entry  = qall(c,
                "SELECT id, project_id, project_name, category, created_by, completed_by, completed_at, billed, received FROM accounting WHERE id=%s",
                (acc_id,)
            )

            if not entry:
                st.error("Entry not found.")
            else:
                (a_id, a_proj_id, a_name, a_cat, a_creator, a_cby, a_cat2,
                 a_billed, a_received) = entry[0]
                participants = get_participants(a_proj_id)

                if st.button("← Back to Accounting", key="back_acc"):
                    st.session_state.active_accounting = None
                    st.rerun()

                st.markdown(f"<div class='page-title'>📁 {esc(a_name)}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='page-subtitle'>{esc(a_cat)} · Completed</div>", unsafe_allow_html=True)

                left_col, right_col = st.columns([1, 1], gap="large")

                with left_col:
                    part_html       = "".join(avatar_html(p, "sm") for p in participants)
                    part_names_html = "".join(
                        f'<span style="font-size:11px;color:#57606a;align-self:center;">{esc(p)}</span>'
                        for p in participants
                    )
                    orig_proj = qone(c,
                        "SELECT est_duration, start_date FROM projects WHERE id=%s", (a_proj_id,)
                    )
                    est_dur   = orig_proj[0] if orig_proj else "—"
                    start_d   = as_date(orig_proj[1]) if orig_proj else "—"

                    st.markdown(f"""
                    <div class="detail-box">
                        <div class="detail-label">Category</div><div class="detail-value">{esc(a_cat)}</div>
                        <div class="detail-label">Estimated Duration</div><div class="detail-value">{esc(est_dur) or "—"}</div>
                        <div class="detail-label">Starting Date</div><div class="detail-value">{start_d or "—"}</div>
                        <div class="detail-label">Created By</div><div class="detail-value">{esc(a_creator)}</div>
                        <div class="detail-label">Completed By</div><div class="detail-value">{esc(a_cby)} · {fmt_ts(a_cat2)}</div>
                        <div class="detail-label">Participants</div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
                            {part_html}{part_names_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown(
                        '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                        'letter-spacing:0.08em;color:#656d76;margin-bottom:8px;">Billed</div>',
                        unsafe_allow_html=True
                    )
                    billed_opts   = ["Not Completed", "Completed"]
                    billed_colors = {"Not Completed": "#9a6700", "Completed": "#1a7f37"}
                    b_cols = st.columns(len(billed_opts))
                    for i, opt in enumerate(billed_opts):
                        is_sel     = (a_billed == opt)
                        btn_style  = "border: 1px solid " + (billed_colors[opt] if is_sel else "#d0d7de")
                        btn_color  = billed_colors[opt] if is_sel else "#656d76"
                        btn_bg     = "#fff8c5" if (is_sel and opt == "Not Completed") else (
                                     "#dafbe1" if (is_sel and opt == "Completed") else "#ffffff")
                        b_cols[i].markdown(
                            f'<div style="background:{btn_bg};'
                            f'{btn_style};border-radius:5px;padding:6px;text-align:center;'
                            f'font-size:11px;font-weight:600;color:{btn_color};">{opt}</div>',
                            unsafe_allow_html=True
                        )
                        if b_cols[i].button(opt, key=f"billed_{opt}_{a_id}"):
                            c.execute("UPDATE accounting SET billed=%s WHERE id=%s", (opt, a_id))
                            st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown(
                        '<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                        'letter-spacing:0.08em;color:#656d76;margin-bottom:8px;">Received</div>',
                        unsafe_allow_html=True
                    )
                    recv_opts   = ["No", "Partially", "Completed"]
                    recv_colors = {"No": "#cf222e", "Partially": "#9a6700", "Completed": "#1a7f37"}
                    r_cols = st.columns(len(recv_opts))
                    for i, opt in enumerate(recv_opts):
                        is_sel    = (a_received == opt)
                        btn_style = "border: 1px solid " + (recv_colors[opt] if is_sel else "#d0d7de")
                        btn_color = recv_colors[opt] if is_sel else "#656d76"
                        btn_bg    = "#ffebe9" if (is_sel and opt == "No") else (
                                    "#fff8c5" if (is_sel and opt == "Partially") else (
                                    "#dafbe1" if (is_sel and opt == "Completed") else "#ffffff"))
                        r_cols[i].markdown(
                            f'<div style="background:{btn_bg};'
                            f'{btn_style};border-radius:5px;padding:6px;text-align:center;'
                            f'font-size:11px;font-weight:600;color:{btn_color};">{opt}</div>',
                            unsafe_allow_html=True
                        )
                        if r_cols[i].button(opt, key=f"recv_{opt}_{a_id}"):
                            c.execute("UPDATE accounting SET received=%s WHERE id=%s", (opt, a_id))
                            st.rerun()

                with right_col:
                    st.markdown("**Project Chat**")
                    msgs = c.execute(
                        "SELECT sender, message, sent_at FROM accounting_chat WHERE project_id=%s ORDER BY sent_at, id",
                        (a_proj_id,)
                    )

                    chat_html = "<div style='height:400px;overflow-y:auto;padding:8px;background:#ffffff;border:1px solid #d0d7de;border-radius:8px;margin-bottom:12px;'>"
                    if msgs:
                        for sender, message, sent_at in msgs:
                            bubble_class = "mine" if sender == USERNAME else "theirs"
                            av           = avatar_html(sender, "sm")
                            align        = "flex-end" if sender == USERNAME else "flex-start"
                            chat_html += (
                                f'<div style="display:flex;flex-direction:column;align-items:{align};margin-bottom:8px;">'
                                f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;">'
                                f'{av}<span style="font-size:10px;color:#656d76;">{esc(sender)} · {fmt_ts(sent_at)}</span></div>'
                                f'<div class="chat-bubble {bubble_class}">{esc(message)}</div>'
                                f'</div>'
                            )
                    else:
                        chat_html += "<div style='text-align:center;color:#656d76;font-size:13px;padding:40px 0;'>No messages yet.</div>"
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
                        st.rerun()

        else:
            billed_color  = {"Not Completed": "#9a6700", "Completed": "#1a7f37"}
            recv_color    = {"No": "#cf222e", "Partially": "#9a6700", "Completed": "#1a7f37"}

            for a_id, a_proj_id, a_name, a_cat, a_creator, a_cby, a_cat2, a_billed, a_received in acc_rows:
                bc = billed_color.get(a_billed, "#656d76")
                rc = recv_color.get(a_received, "#656d76")
                cat_icon = {"Explorations": "🔭", "Residential": "🏡", "Commercial": "🏢"}.get(a_cat, "📁")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'background:#ffffff;border:1px solid #d0d7de;border-radius:6px;'
                    f'padding:10px 14px;margin-bottom:6px;box-shadow:0 1px 2px rgba(31,35,40,0.04);">'
                    f'<span style="font-size:14px;">{cat_icon}</span>'
                    f'<span style="font-size:13px;font-weight:600;color:#1f2328;flex:1;">{esc(a_name)}</span>'
                    f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
                    f'background:#ffffff;border:1px solid {bc};color:{bc};">BILLED: {esc(a_billed)}</span>'
                    f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
                    f'background:#ffffff;border:1px solid {rc};color:{rc};">RECEIVED: {esc(a_received)}</span>'
                    f'<span style="font-size:11px;color:#656d76;">{fmt_ts(a_cat2)}</span>'
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
                    st.success(f"{esc(new_emp_name.strip())} added!")
                    st.session_state.show_add_emp = False
                    st.rerun()
                except psycopg2.errors.UniqueViolation:
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
                bg     = "#fff0f3" if is_selected else "#ffffff"
                color  = "#d1493b" if is_selected else "#1f2328"
                border = "#d1493b" if is_selected else "#d0d7de"
                weight = "700"     if is_selected else "400"

                row_left, row_right = st.columns([5, 1])
                row_left.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;
                            background:{bg};border:1px solid {border};
                            border-radius:8px;padding:8px 12px;height:40px;">
                    {avatar_html(emp, "sm")}
                    <span style="font-size:13px;font-weight:{weight};color:{color};">{esc(emp)}</span>
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
                        <div style="font-size:18px;font-weight:700;color:#1f2328;">{esc(emp)}</div>
                        <div style="font-size:12px;color:#656d76;">Employee</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                emp_projects = qall(c, """
                    SELECT p.id, p.name, p.category, p.created_by, p.created_at
                    FROM projects p
                    JOIN project_participants pp ON p.id = pp.project_id
                    WHERE pp.employee = %s
                    ORDER BY p.created_at DESC
                """, (emp,))

                st.markdown(f"<div class='detail-label'>Projects ({len(emp_projects)})</div>", unsafe_allow_html=True)

                if emp_projects:
                    for pid, pname, pcat, pcreator, pdate in emp_projects:
                        participants = get_participants(pid)
                        part_avatars = "".join(avatar_html(p, "sm") for p in participants[:5])
                        st.markdown(f"""
                        <a href="?open_proj={pid}" target="_self" style="text-decoration:none;">
                            <div class="a-card" style="margin-bottom:8px;cursor:pointer;transition:border-color 0.15s;"
                                 onmouseover="this.style.borderColor='#0969da'"
                                 onmouseout="this.style.borderColor='#d0d7de'">
                                <div class="a-card-top">
                                    <span class="badge badge-project">{esc(pcat)}</span>
                                    <span class="a-card-name">{esc(pname)}</span>
                                </div>
                                <div class="a-card-meta" style="margin-bottom:6px;">
                                    Created by <strong style="color:#57606a">{esc(pcreator)}</strong> · {fmt_ts(pdate)}
                                </div>
                                <div style="display:flex;gap:4px;">{part_avatars}</div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

                else:
                    st.markdown("""
                    <div style="color:#656d76;font-size:13px;padding:20px 0;">
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