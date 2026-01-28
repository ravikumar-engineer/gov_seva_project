import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# ---------------- ENV ----------------
load_dotenv()  # HF_TOKEN in .env

# ---------------- HF CLIENT ----------------
client = InferenceClient(
    token=os.getenv("HF_TOKEN")
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Gov Scheme Chatbot 2026",
    page_icon="🇮🇳",
    layout="centered"
)

st.markdown(
"""
<style>
/* --- General Page Styling --- */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f6f8;
    color: #1b2a49;
}

/* --- Header --- */
header, .css-1v3fvcr {
    position: fixed;
    top: 0;
    width: 100%;
    background-color: #003366;
    color: white;
    font-size: 1.5rem;
    font-weight: 600;
    padding: 0.8rem 1rem;
    text-align: center;
    z-index: 1000;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* --- Chat container --- */
.chat-container {
    margin-top: 80px; /* header space */
    padding: 1rem;
    max-height: 75vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* --- Chat bubbles --- */
.chat-message {
    padding: 0.8rem 1rem;
    border-radius: 12px;
    max-width: 75%;
    word-wrap: break-word;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    opacity: 0;
    transform: translateY(10px);
    animation: fadeInUp 0.4s forwards;
}

/* --- User vs Bot --- */
.chat-message.user {
    background-color: #cfe2ff;
    color: #003366;
    align-self: flex-end;
}

.chat-message.bot {
    background-color: #e9ecef;
    color: #1b2a49;
    align-self: flex-start;
}

/* --- Chat Input --- */
.stTextInput>div>div>input {
    border-radius: 10px;
    padding: 0.5rem 1rem;
    border: 1px solid #ced4da;
    font-size: 1rem;
}

.stButton>button {
    background-color: #0056b3;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: background-color 0.3s, transform 0.2s;
}

.stButton>button:hover {
    background-color: #003366;
    transform: translateY(-2px);
}

/* --- Scrollbar Styling --- */
.chat-container::-webkit-scrollbar {
    width: 8px;
}

.chat-container::-webkit-scrollbar-thumb {
    background-color: #a9a9a9;
    border-radius: 4px;
}

.chat-container::-webkit-scrollbar-track {
    background-color: #f4f6f8;
}

/* --- Animations --- */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* --- Responsive --- */
@media screen and (max-width: 600px) {
    .chat-message {
        max-width: 90%;
        font-size: 0.95rem;
    }
    header, .css-1v3fvcr {
        font-size: 1.2rem;
        padding: 0.6rem;
    }
}
</style>
""",
unsafe_allow_html=True
)



st.title("🇮🇳 Government Scheme Advisor")
st.caption("Brutally honest. Actually useful.")

# Session state for history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar input
st.sidebar.header("Tell me about yourself")
with st.sidebar.form(key="user_form"):
    age = st.number_input("Your Age", min_value=18, max_value=100, step=1)
    occupation = st.selectbox(
        "Occupation",
        ("Student", "Farmer", "Private Job", "Government Job", "Self Employed", "Unemployed")
    )
    income = st.number_input("Monthly Income (₹)", min_value=0, step=1000)
    state = st.text_input("State (e.g. Uttar Pradesh)")
    category = st.selectbox("Category", ("General", "OBC", "SC", "ST"))
    submitted = st.form_submit_button("Find My Schemes")


# Core recommendation function
def recommend_schemes(age, occupation, income, state, category):
    system_prompt = """
You are a brutal but helpful Indian Government Scheme Advisor.
STRICT RULES:
- Be honest and direct
- Clearly explain eligibility or rejection
- Recommend only REAL schemes
- Prefer Central then State
- Use bullets
- Plain text output
"""
    user_prompt = f"""
User Profile:
- Age: {age}
- Occupation: {occupation}
- Income: ₹{income}
- State: {state}
- Category: {category}

Task:
Recommend the best government schemes with steps.
"""
    # Model that is *actually supported* via providers
    model_id = "deepseek-ai/DeepSeek-V3-0324"

    response = client.chat_completion(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=800,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# Clear history
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# Sidebar history
if st.session_state.chat_history:
    st.sidebar.divider()
    st.sidebar.header("Previous Queries")
    for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
        st.sidebar.markdown(f"**Query {i}:** {chat['user']}")
        st.sidebar.markdown(f"**Response:** {chat['assistant']}")
        st.sidebar.markdown("---")

st.divider()

# When form submitted
if submitted:
    user_input = (
        f"Age: {age}, Occupation: {occupation}, Income: ₹{income}, "
        f"State: {state}, Category: {category}"
    )

    with st.spinner("Crunching numbers and govt rules... 🇮🇳"):
        answer = recommend_schemes(age, occupation, income, state, category)

    st.session_state.chat_history.append({"user": user_input, "assistant": answer})
    st.chat_message("assistant").markdown(answer)

# Follow‑up chat
user_question = st.chat_input("Ask about a scheme...")

if user_question:
    messages = [
        {"role": "system", "content": "You are Brutal Government Scheme Advisor. Answer plainly."}
    ]
    for chat in st.session_state.chat_history:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})
    messages.append({"role": "user", "content": user_question})

    with st.spinner("Thinking... 🇮🇳"):
        response = client.chat_completion(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )

    text = response.choices[0].message.content.strip()
    st.session_state.chat_history.append({"user": user_question, "assistant": text})
    st.chat_message("assistant").markdown(text)

st.divider()
st.caption("⚠️ Always verify schemes from official government portals.")
