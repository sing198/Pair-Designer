import streamlit as st
import google.generativeai as genai
import sqlite3
import uuid

# ----------------------------------------
# 0. ตั้งค่าหน้าเว็บ
# ----------------------------------------
st.set_page_config(page_title="Pair Designer", page_icon="🏗️", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
system_instruction = "คุณคือ AI System Architect ผู้เชี่ยวชาญด้านการออกแบบระบบและฐานข้อมูล"
model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

# ----------------------------------------
# 1. Database Logic
# ----------------------------------------
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT)''')
    conn.commit()
    conn.close()

def create_session(username, title):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect('chat_history.db')
    conn.execute("INSERT INTO sessions (id, username, title) VALUES (?, ?, ?)", (session_id, username, title))
    conn.commit()
    conn.close()
    return session_id

def get_sessions(username):
    conn = sqlite3.connect('chat_history.db')
    data = conn.execute("SELECT id, title FROM sessions WHERE username = ? ORDER BY created_at DESC", (username,)).fetchall()
    conn.close()
    return data

def save_message(session_id, role, content):
    conn = sqlite3.connect('chat_history.db')
    conn.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def load_messages(session_id):
    conn = sqlite3.connect('chat_history.db')
    data = conn.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
    conn.close()
    return data

def delete_session(session_id):
    conn = sqlite3.connect('chat_history.db')
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

init_db()

# ----------------------------------------
# 2. ระบบซ่อนตัวตน (Anonymous Session)
# ----------------------------------------
if 'hidden_user_id' not in st.session_state:
    st.session_state.hidden_user_id = "user_" + str(uuid.uuid4())[:8]

my_secret_id = st.session_state.hidden_user_id

if 'current_session' not in st.session_state:
    st.session_state.current_session = None

sessions = get_sessions(my_secret_id)

# ----------------------------------------
# 3. Sidebar
# ----------------------------------------
if len(sessions) > 0:
    with st.sidebar:
        st.header("💬 ประวัติการสนทนา")
        if st.button("➕ สร้างแชทใหม่", use_container_width=True):
            st.session_state.current_session = None
            st.rerun()
            
        st.divider()
        
        for s_id, title in sessions:
            col1, col2 = st.columns([8, 2])
            with col1:
                if st.button(title, key=f"btn_{s_id}", use_container_width=True):
                    st.session_state.current_session = s_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{s_id}", use_container_width=True):
                    delete_session(s_id)
                    if st.session_state.current_session == s_id:
                        st.session_state.current_session = None
                    st.rerun()

# ----------------------------------------
# 4. Main Area (UI แบบใหม่ มินิมอลตรงกลางจอ)
# ----------------------------------------
# ----------------------------------------
# 4. Main Area (UI แบบใหม่ มินิมอล + กล่องแชททรงแคปซูล)
# ----------------------------------------

# ฝัง CSS ระดับ Global เพื่อแต่งกล่องแชทให้เหมือน Gemini (มีผลตลอดการใช้งาน)
# ฝัง CSS ระดับ Global เพื่อแต่งกล่องแชทและข้อความให้ออกมาเหมือน Gemini
st.markdown("""
    <style>
    /* 1. จัดระเบียบข้อความแชท (Output) ให้อยู่กึ่งกลางจอและกว้างเท่ากล่อง Input */
    [data-testid="stChatMessage"] {
        max-width: 800px !important; /* ปรับให้กว้างเท่ากล่องแชทด้านล่าง */
        margin: 0 auto !important;   /* ดันให้อยู่กึ่งกลางจอเสมอ */
        padding: 1rem 0 !important;  /* เพิ่มช่องว่างระหว่างบรรทัดให้อ่านง่ายขึ้น */
    }

    /* 2. บีบความกว้างของกล่องแชท (Input) ให้อยู่กึ่งกลางจอ */
    [data-testid="stChatInput"] {
        max-width: 800px !important; 
        margin: 0 auto !important;   
        padding-bottom: 15px !important; 
    }
    
    /* 3. ทำขอบกล่องข้อความให้โค้งมน (Pill Shape) */
    [data-testid="stChatInput"] > div {
        border-radius: 50px !important; 
        padding: 8px 20px !important;   
        border: 1px solid #5f6368 !important; 
        background-color: #1e1e1e !important; 
    }
    
    /* 4. ขยับปุ่มลูกศรส่งข้อความ */
    [data-testid="stChatInput"] button {
        margin-right: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.current_session is None:
    # CSS ดันข้อความต้อนรับให้อยู่ตรงกลางจอ
    st.markdown("""
        <style>
        .center-screen {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 60vh; 
            text-align: center;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .sub-title {
            font-size: 1.2rem;
            color: #9aa0a6;
        }
        </style>
        
        <div class="center-screen">
            <div class="main-title">มาเริ่มออกแบบระบบกันเลย 🏗️</div>
            <div class="sub-title">Pair Designer: AI System Architect พร้อมช่วยคุณคิดโครงสร้างแล้ว</div>
        </div>
    """, unsafe_allow_html=True)
else:
    # ส่วนแสดงผลตอนกำลังแชท
    st.markdown("""
            <div style='max-width: 800px; margin: 0 auto;'>
                <h3>🏗️ Pair Designer</h3>
            </div>
        """, unsafe_allow_html=True)
    active_session = st.session_state.current_session
    db_messages = load_messages(active_session)
    
    for role, content in db_messages:
        with st.chat_message(role):
            st.markdown(content)

# ----------------------------------------
# 5. Chat Input (ตัวกล่องนี้จะอยู่ล่างสุดเสมอโดยอัตโนมัติ)
# ----------------------------------------
if prompt := st.chat_input("พิมพ์ไอเดียระบบที่คุณอยากทำลงไปได้เลย..."):
    
    if st.session_state.current_session is None:
        short_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
        new_id = create_session(my_secret_id, short_title)
        st.session_state.current_session = new_id

    active_session = st.session_state.current_session

    st.chat_message("user").markdown(prompt)
    save_message(active_session, "user", prompt)

    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        save_message(active_session, "assistant", response.text)
    
    st.rerun()