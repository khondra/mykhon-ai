import hashlib
import hmac
import secrets
import sqlite3


DB_NAME = "chatbot.db"
PASSWORD_HASH_ITERATIONS = 600_000


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def register_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS
    )
    hashed_password = "pbkdf2_sha256${}${}${}".format(
        PASSWORD_HASH_ITERATIONS,
        salt.hex(),
        digest.hex()
    )

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email.lower(), hashed_password)
        )

        conn.commit()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "This email is already registered."

    finally:
        conn.close()


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email, password FROM users WHERE email = ?",
        (email.lower(),)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    user_id, user_email, stored_password = user

    try:
        algorithm, iterations, salt_hex, digest_hex = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return None
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations)
        )
    except (ValueError, TypeError):
        return None

    if hmac.compare_digest(candidate.hex(), digest_hex):
        return {
            "id": user_id,
            "email": user_email
        }

    return None


def save_conversation(user_id, mode, user_message, ai_response):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations
        (user_id, mode, user_message, ai_response)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        mode,
        user_message,
        ai_response
    ))

    conn.commit()
    conn.close()


def get_history(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mode, user_message, ai_response, created_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    history = cursor.fetchall()

    conn.close()

    return history

MODEL = "qwen3:4b"


SYSTEM_PROMPTS = {

    "💬 Q&A": """
You are a helpful AI assistant.

Answer the user's questions clearly and accurately.

Important language rule:
- If the user writes in Khmer, respond in Khmer.
- If the user writes in English, respond in English.
- If the user mixes Khmer and English, understand both.

Use simple explanations when appropriate.
""",

    "✍️ Prompt Generator": """
You are an expert AI Prompt Engineer.

Your job is to transform the user's idea into a professional,
detailed and useful AI prompt.

Structure the prompt using:

1. Role
2. Objective
3. Context
4. Requirements
5. Style
6. Output format

If the user writes in Khmer, explain the result in Khmer.
The generated prompt can be in English when that produces
better results for AI image, video, marketing or technical tools.
""",

    "📰 Article Writer": """
You are a professional article and content writer.

Write high-quality articles based on the user's topic.

Use this structure when appropriate:

# Title

## Introduction

## Main Content

## Examples

## Conclusion

If the user writes in Khmer, write the article in Khmer.

Make the article natural, informative and easy to read.
""",

    "🌐 Khmer ↔ English Translation": """
You are a professional Khmer-English translator.

Detect the language automatically.

If the user writes Khmer:
    translate it into natural English.

If the user writes English:
    translate it into natural Khmer.

Preserve:
- Meaning
- Tone
- Names
- Numbers
- Context

Do not unnecessarily add information.
"""
}


def generate_response(mode, user_message):

    import ollama

    system_prompt = SYSTEM_PROMPTS.get(
        mode,
        SYSTEM_PROMPTS["💬 Q&A"]
    )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response["message"]["content"]

import streamlit as st


# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ------------------------------------------------
# DATABASE
# ------------------------------------------------

create_tables()


# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------------------------
# LOGIN / REGISTER
# ------------------------------------------------

def authentication_page():

    st.title("🤖 AI Assistant")

    st.write(
        "Ask questions, generate prompts, write articles "
        "and translate Khmer ↔ English."
    )

    tab1, tab2 = st.tabs([
        "🔐 Login",
        "📝 Create Account"
    ])

    # LOGIN
    with tab1:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:
                st.error("Please enter email and password.")

            else:

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user = user

                    st.success("Login successful.")

                    st.rerun()

                else:

                    st.error(
                        "Incorrect email or password."
                    )

    # REGISTER
    with tab2:

        new_email = st.text_input(
            "Email",
            key="register_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not new_email or not new_password:

                st.error(
                    "Please complete all fields."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = register_user(
                    new_email,
                    new_password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


# ------------------------------------------------
# CHATBOT
# ------------------------------------------------

def chatbot_page():

    user = st.session_state.user

    # SIDEBAR
    with st.sidebar:

        st.title("🤖 AI Assistant")

        st.write("Logged in as:")

        st.info(user["email"])

        st.divider()

        mode = st.radio(
            "Choose AI Function",
            [
                "💬 Q&A",
                "✍️ Prompt Generator",
                "📰 Article Writer",
                "🌐 Khmer ↔ English Translation"
            ]
        )

        st.divider()

        if st.button(
            "🗑️ New Chat",
            use_container_width=True
        ):

            st.session_state.messages = []

            st.rerun()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.messages = []

            st.rerun()

    # HEADER

    st.title("🤖 AI Assistant")

    st.caption(
        "Ask questions • Generate prompts • Write articles • "
        "Khmer ↔ English"
    )

    st.subheader(mode)

    # DISPLAY CHAT

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # USER INPUT

    user_message = st.chat_input(
        "Type your question here..."
    )

    if user_message:

        # USER MESSAGE

        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):

            st.markdown(user_message)

        # AI RESPONSE

        with st.chat_message("assistant"):

            with st.spinner(
                "AI is thinking..."
            ):

                try:

                    response = generate_response(
                        mode,
                        user_message
                    )

                    st.markdown(response)

                except Exception as e:

                    response = (
                        "Sorry, I couldn't connect to "
                        "the AI model.\n\n"
                        f"Error: {e}"
                    )

                    st.error(response)

        # SAVE

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        save_conversation(
            user["id"],
            mode,
            user_message,
            response
        )


# ------------------------------------------------
# APP ROUTER
# ------------------------------------------------

if not st.session_state.logged_in:

    authentication_page()

else:

    chatbot_page()
