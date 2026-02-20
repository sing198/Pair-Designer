import streamlit as st
import google.generativeai as genai

# 1. API KEY
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. System Prompt 
system_instruction = """
คุณคือ Senior Software Architect ที่มีประสบการณ์สูงในการออกแบบระบบ 
หน้าที่ของคุณคือให้คำปรึกษาด้าน Software Architecture, การเลือกใช้ Tech Stack, การจัดการ Database และวิเคราะห์ Trade-offs
ตอบคำถามให้กระชับ เป็นมืออาชีพ เน้นหลักการ Best Practice และอธิบายให้เข้าใจง่าย
"""

# 3. Model
model = genai.GenerativeModel(
    'gemini-3.5-flash',
    system_instruction=system_instruction
)

# 3. สร้างหน้าตาเว็บไซต์ด้วย Streamlit
st.set_page_config(page_title="Pair Designer", page_icon="🏗️")
st.title("🏗️ Pair Designer: AI System Architect")
st.write("ผู้ช่วยออกแบบสถาปัตยกรรมซอฟต์แวร์ของคุณ พิมพ์ไอเดียระบบที่คุณอยากทำลงไปได้เลย!")

# 4. ระบบเก็บประวัติการแชท (เพื่อให้คุยต่อเนื่องได้)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. กล่องรับข้อความและประมวลผล
if prompt := st.chat_input("ตัวอย่าง: อยากทำระบบ E-commerce รับคนเข้าเว็บ 10,000 คนพร้อมกัน ควรออกแบบโครงสร้างยังไง?"):
    # แสดงข้อความของเรา
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # เรียก AI มาตอบ
    with st.chat_message("assistant"):
        # ส่งข้อความไปหา Gemini
        response = model.generate_content(prompt)
        st.markdown(response.text)
        # เก็บคำตอบลงประวัติ
        st.session_state.messages.append({"role": "assistant", "content": response.text})