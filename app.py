import streamlit as st
import time
import database
import os

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

# Load environment variables
load_dotenv()

# ================= API KEYS =================

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 🔹 Groq Client (Text AI)
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
else:
    groq_client = None

# 🔹 OpenAI Client (Vision AI)
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None

# Stop app only if Groq missing (text is required)
if not groq_client:
    st.error("GROQ_API_KEY not found!")
    st.stop()

client = groq_client

# ================= DB INIT =================
database.init_db()

st.set_page_config(page_title="NovaStudy PRO", layout="wide")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    
# 🔥 Initialize theme globally (FIXES ERROR)
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"    

# ================= GLOBAL PREMIUM CSS =================
st.markdown("""
<style>

/* Remove Streamlit padding */
.block-container {
    padding-top: 2rem;
}

/* Neon Header */
.neon-header {
    width: 420px;
    margin: 40px auto 40px auto;
    padding: 18px;
    text-align: center;
    font-size: 26px;
    font-weight: bold;
    border-radius: 20px;
    background: rgba(0,255,150,0.08);
    box-shadow: 0 0 25px rgba(0,255,150,0.6),
                0 0 50px rgba(0,255,150,0.4),
                0 0 80px rgba(0,255,150,0.3);
    color: #00ffcc;
}

/* Glass Login Card */
.login-wrapper {
    display: flex;
    justify-content: center;
}

.login-card {
    width: 420px;
    padding: 40px;
    border-radius: 20px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    box-shadow: 0 0 50px rgba(0,255,150,0.25);
}

/* Buttons */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    font-weight: 600;
    background: linear-gradient(90deg, #00ff99, #00ccff);
    color: black;
}

/* Chat bubble glow */
div[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 12px;
    background: rgba(255,255,255,0.05);
    margin-bottom: 10px;
}.stSidebar img {
    border-radius: 50%;
    border: 3px solid #00ffcc;
    box-shadow: 0 0 20px #00ffcc;
}



</style>
""", unsafe_allow_html=True)

# ================= THEME STYLING =================
if st.session_state.get("theme") == "Light":
    st.markdown("""
    <style>
    body {
        background-color: #f5f5f5;
        color: black;
    }
    .neon-header {
        background: rgba(0,0,0,0.05);
        color: #111;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= BACKGROUND PARTICLES =================
st.markdown("""
<style>
#bg-canvas {
    position: fixed;
    top: 0;
    left: 0;
    z-index: -1;
}
</style>

<canvas id="bg-canvas"></canvas>

<script>
const canvas = document.getElementById("bg-canvas");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

for (let i = 0; i < 60; i++) {
    particles.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        r: Math.random()*3,
        dx:(Math.random()-0.5)*2,
        dy:(Math.random()-0.5)*2
    });
}

function animate(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach(p=>{
        ctx.beginPath();
        ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle="#00ffcc";
        ctx.fill();
        p.x+=p.dx;
        p.y+=p.dy;
        if(p.x<0||p.x>canvas.width)p.dx*=-1;
        if(p.y<0||p.y>canvas.height)p.dy*=-1;
    });
    requestAnimationFrame(animate);
}
animate();
</script>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="neon-header">NovaStudy PRO</div>', unsafe_allow_html=True)

# ================= AUTH =================
if not st.session_state.get("user"):

    st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = database.login(username, password)
        if user:
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Register"):
        if database.register(username, password):
            st.success("Registered successfully")
        else:
            st.error("User already exists")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ================= AFTER LOGIN =================
else:
    st.sidebar.title("NovaStudy PRO")

    # 🌗 Theme Toggle
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"

    
    

    # ================= PROFILE SECTION =================

    if "edit_profile" not in st.session_state:
        st.session_state.edit_profile = False

    
    
    

    # Upload section
    if st.session_state.edit_profile:

        uploaded_profile = st.sidebar.file_uploader(
            "Upload new profile image",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_profile is not None:
            import base64
            image_bytes = uploaded_profile.read()
            encoded_image = base64.b64encode(image_bytes).decode()

            database.save_profile_image(
                st.session_state.user,
                encoded_image
            )

            st.session_state.edit_profile = False
            st.success("Profile updated!")
            st.rerun()

    # 🔥 Load image AFTER upload logic
    stored_image = database.get_profile_image(st.session_state.user)

    if stored_image:
        st.sidebar.image(
            f"data:image/png;base64,{stored_image}",
            width=120
        )
    else:
        st.sidebar.image(
            "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            width=120
        )

    st.sidebar.markdown(f"**{st.session_state.user}**")

    # ================= CHAT ID INIT =================
    if "chat_id" not in st.session_state:
        chats = database.get_user_chats(st.session_state.user)
        if chats:
            st.session_state.chat_id = chats[0]
        else:
            st.session_state.chat_id = database.create_chat(st.session_state.user)

    # ================= NAVIGATION =================
    if "page" not in st.session_state:
        st.session_state.page = "💬 Chat"

    page = st.sidebar.radio(
        "Navigation",
        ["💬 Chat", "📊 Dashboard", "📂 Recent Chats", "⚙ Admin"],
        index=["💬 Chat", "📊 Dashboard", "📂 Recent Chats", "⚙ Admin"].index(st.session_state.page)
    )

    st.session_state.page = page

    if st.sidebar.button("➕ New Chat"):
        st.session_state.chat_id = database.create_chat(st.session_state.user)
        st.session_state.page = "💬 Chat"
        st.rerun()

    if st.sidebar.button("✏ Edit Profile"):
        st.session_state.edit_profile = True
        
    theme_choice = st.sidebar.toggle(" Dark Mode", value=True)
    st.session_state.theme = "Dark" if theme_choice else "Light"    

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
        
        
# ================= CHAT =================
    if page == "💬 Chat":

        st.title(f"Welcome {st.session_state.user} 👋")

    history = database.load_messages(
        st.session_state.user,
        st.session_state.chat_id
    )

    for role, content, created_at in history:
        with st.chat_message(role):
            st.markdown(content)
            st.caption(created_at)

    uploaded_image = st.file_uploader(
        "Upload an image (optional)",
        type=["png", "jpg", "jpeg"]
    )

    prompt = st.chat_input("Type a message")

    if prompt or uploaded_image:

        user_content = []

        if prompt:
            user_content.append({
                "type": "text",
                "text": prompt
            })

        if uploaded_image:
            import base64
            image_bytes = uploaded_image.read()
            encoded_image = base64.b64encode(image_bytes).decode()

            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            })

        database.save_message(
            st.session_state.user,
            st.session_state.chat_id,
            "user",
            prompt if prompt else "[Image Uploaded]"
        )

        with st.chat_message("user"):
            if prompt:
                st.markdown(prompt)
            if uploaded_image:
                st.image(uploaded_image)

        # Vision → GPT-4o
                # ================= AI RESPONSE =================

        # Vision → GPT-4o
        if uploaded_image and openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are NovaStudy AI, an intelligent academic assistant."
                        },
                        {
                            "role": "user",
                            "content": user_content
                        }
                    ],
                    max_tokens=1000
                )

                reply = response.choices[0].message.content

            except Exception as e:
                st.error(f"OpenAI Error: {str(e)}")
                reply = "Vision model failed."

        # Text → Groq (WITH MEMORY)
        else:

            # 🧠 Load last 10 messages
            history = database.load_messages(
                st.session_state.user,
                st.session_state.chat_id
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are NovaStudy AI, an intelligent academic assistant."
                }
            ]

            # Add last 10 messages only
            for role, content, created_at in history[-10:]:
                messages.append({
                "role": role,
                "content": content
        })
                
                    
                    
                

            # Add new user message
            messages.append({
                "role": "user",
                "content": prompt
            })

            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages
            )

            reply = response.choices[0].message.content

        # ================= SAVE REPLY =================

        database.save_message(
            st.session_state.user,
            st.session_state.chat_id,
            "assistant",
            reply
        )

        
        with st.chat_message("assistant"):

            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("🟢 NovaStudy is thinking...")

            time.sleep(0.8)  # small delay for realism

            thinking_placeholder.empty()

            message_placeholder = st.empty()
            full_text = ""

            for word in reply.split():
                full_text += word + " "
                message_placeholder.markdown(full_text + "▌")
                time.sleep(0.03)

            message_placeholder.markdown(full_text)

    # ================= DASHBOARD =================
    elif page == "📊 Dashboard":
        st.title("Dashboard")
        st.write("Coming soon...")

    # ================= RECENT CHATS =================
    elif page == "📂 Recent Chats":
        st.title("Recent Chats")
        chats = database.get_user_chats(st.session_state.user)

        if not chats:
            st.info("No chats yet.")
        else:
            for chat in chats:
                col1, col2 = st.columns([6, 1])

                with col1:
                    if st.button(f"Open Chat {chat[:8]}", key=chat):
                        st.session_state.chat_id = chat
                        st.session_state.page = "💬 Chat"
                        st.rerun()

                with col2:
                    if st.button("❌", key=f"del_{chat}"):
                        database.delete_chat(chat)
                        st.rerun()

    # ================= ADMIN =================
    elif page == "⚙ Admin":
        st.title("Admin Panel")
        st.write("Admin tools coming soon...")