# 🧠 Persistent OpenAI GPT-4o Agent (LangGraph + Streamlit)

A full-featured, production-ready AI assistant built using **LangGraph**, **LangChain**, **Streamlit**, and **OpenAI's GPT-4o API**.  
This app supports persistent memory across sessions, token-authenticated access, and secure user isolation using hashing.

---

## 🚀 Features

### 🔐 Secure Token-Based Authentication
- Users must enter their OpenAI API key to begin.
- Each key is **SHA-256 hashed** to create a secure `user_hash`.
- This hash is used to isolate user sessions without storing any real API tokens in the database.

### 💬 Persistent Chat Sessions
- Chat messages are stored in an **SQLite database**.
- Each user has access to their own sessions based on their `user_hash`.
- Session names, message types, and timestamps are preserved.

### 🧠 LangGraph-Powered Agent
- Implements a memory-based LangGraph agent with message accumulation.
- Supports streaming OpenAI responses, system prompts, and structured tool/function messages.
- Easily extensible for tools, functions, or RAG integrations.

### 🗂️ Multi-Session Management
- Users can create, name, and switch between multiple chat sessions.
- Each session maintains its own conversation history.

### 💥 Clean Log Out & Key Reset
- One-click logout instantly clears session, key, and chat history from memory.
- Brings user back to a welcome screen prompting for a new API key.

---

## 📂 File Structure

```bash
├── main.py # Streamlit app entry point (OpenAI version)
├── agent.py # LangGraph agent logic
├── chat_messages.db # SQLite DB for chat and sessions
├── requirements.txt # Python dependencies
└── README.md # You're here!
```

---

## 🧪 Getting Started

## 1. **Clone the repo**
```bash
git clone https://github.com/your-username/OpenAI-GPT4o-Agent.git
cd OpenAI-GPT4o-Agent
```

## 2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 3. **Run the app**
```bash
streamlit run main.py
```

## 4. **Use your OpenAI API key**
- 💡 Get one at https://platform.openai.com/account/api-keys

---

## 🔒 Privacy & Security
- Tokens are never saved — only hashes are stored.
- SQLite is used only for message history, not sensitive data.
- Fully isolated session control via user_hash.

---

## 🧰 Tech Stack
- LangGraph & LangChain
- Streamlit
- SQLite (for state persistence)
- OpenAI API

---

## 📸 Previews
---
![image](https://github.com/user-attachments/assets/f29a4cc6-af83-4aa2-ae42-1d997a716886)
---
![image](https://github.com/user-attachments/assets/0224e80e-f9e1-472d-afbe-8771d5ab3138)
---
![image](https://github.com/user-attachments/assets/55ba3db2-9c42-499f-ae9f-5f02056e8196)
---
![image](https://github.com/user-attachments/assets/620174c5-df83-415b-8e3f-6ee62648e348)
---

## 🧑‍💻 Author
Jayesh Suryawanshi
- 🧠 Python Developer | 💡 AI Tools Builder | 🌍 Data & Engineering Enthusiast
- 📫 [LinkedIn](https://www.linkedin.com/in/jayesh-suryawanshi-858bb21aa/)

---

## 📃 License
MIT License
