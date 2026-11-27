import json
import os
import re
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Personal AI Agent (Groq)",
    page_icon="🧠",
    layout="wide",
)

NOTES_DIR = "personal_notes"
DB_PATH = "personal_agent.db"
MODEL_NAME = "openai/gpt-oss-120b"
os.makedirs(NOTES_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            category TEXT,
            title TEXT,
            details TEXT,
            status TEXT DEFAULT 'Completed'
        )
        """
    )
    conn.commit()
    conn.close()


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", name.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = f"personal_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return f"{cleaned}.md"


def log_personal_activity(
    category: str, title: str, details: str = "", status: str = "Completed"
) -> str:
    """വ്യക്തിഗത പ്രവർത്തനങ്ങളും ടാസ്കുകളും SQLite ഡാറ്റാബേസിൽ സ്ഥിരമായി രേഖപ്പെടുത്തുക."""
    init_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO personal_logs (created_at, category, title, details, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (now_str, category, title, details, status),
    )
    conn.commit()
    conn.close()
    return f"[Memory Saved] '{category}' -> '{title}' ({status})."


def load_personal_logs_df() -> pd.DataFrame:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT created_at AS Time, category AS Category, title AS Title,
               details AS Details, status AS Status
        FROM personal_logs
        ORDER BY id DESC
        """,
        conn,
    )
    conn.close()
    return df


# ==========================================
# 1. PERSONAL AI AGENT ടൂളുകൾ
# ==========================================

def manage_personal_notes(action: str, note_title: str, content: str = "") -> str:
    """
    വ്യക്തിഗത നോട്ടുകൾ, ജേണൽ, പഠന/പ്രൊജക്ട് കുറിപ്പുകൾ എന്നിവ കൈകാര്യം ചെയ്യുക.
    action: 'save', 'read', 'list', 'append'.
    """
    act = (action or "save").strip().lower()

    if act == "list":
        files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md"))
        if not files:
            return "[Notes] നിലവിൽ വ്യക്തിഗത നോട്ടുകൾ ഒന്നും സേവ് ചെയ്തിട്ടില്ല."
        log_personal_activity("Notes", "Listed personal notes", ", ".join(files))
        return "[Notes] ലഭ്യമായ നോട്ടുകൾ: " + ", ".join(files)

    filename = _safe_filename(note_title)
    filepath = os.path.join(NOTES_DIR, filename)

    if act == "read":
        if not os.path.exists(filepath):
            return f"[Notes] '{filename}' എന്ന നോട്ട് കണ്ടെത്താനായില്ല."
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        log_personal_activity("Notes", f"Read note: {filename}", "Fetched note content")
        return f"[Notes] '{filename}' ഉള്ളടക്കം:\n\n{text}"

    if act == "append":
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        addition = f"\n\n---\n*Added: {stamp}*\n\n{content}"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(addition)
        log_personal_activity("Notes", f"Appended to {filename}", content[:120])
        return f"[Notes] '{filename}' എന്ന നോട്ടിലേക്ക് പുതിയ വിവരങ്ങൾ ചേർത്തു."

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"# {note_title}\n\n*Created: {stamp}*\n\n"
    body = content if content else f"{note_title} സംബന്ധിച്ച വ്യക്തിഗത കുറിപ്പ്."
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    log_personal_activity("Notes", f"Saved note: {filename}", body[:120])
    return f"[Notes] '{filepath}' എന്ന ഫയലിൽ നോട്ട് സേവ് ചെയ്തു."


def manage_tasks_and_schedule(
    action: str, item_title: str, time_or_priority: str = "", requires_approval: bool = False
) -> str:
    """
    വ്യക്തിഗത ടാസ്കുകൾ, റിമൈൻഡറുകൾ, ഷെഡ്യൂളുകൾ എന്നിവ കൈകാര്യം ചെയ്യുക.
    പ്രധാന മാറ്റങ്ങൾക്ക് requires_approval=True നൽകുക.
    """
    if requires_approval:
        log_personal_activity(
            "Schedule / Task",
            f"Pending Approval: {item_title}",
            time_or_priority,
            status="Needs Approval",
        )
        return (
            f"[Human-in-the-Loop] '{item_title}' ({time_or_priority}) എന്ന മാറ്റം "
            "നടപ്പാക്കുന്നതിന് മുമ്പ് നിങ്ങളുടെ സ്ഥിരീകരണം (Approval) ആവശ്യമാണ്."
        )

    log_personal_activity(
        "Schedule / Task",
        f"{action}: {item_title}",
        time_or_priority,
        status="Scheduled / Done",
    )
    return f"[Task/Schedule] '{action}' പൂർത്തിയായി: '{item_title}' ({time_or_priority or 'വിവരങ്ങൾ രേഖപ്പെടുത്തി'})."


def create_personal_plan(
    domain: str, goal: str, constraints_or_budget: str = ""
) -> str:
    """
    യാത്രാ പ്ലാൻ, പഠന പ്ലാൻ, ബജറ്റ്/ചെലവ് പ്ലാൻ, ഹെൽത്ത്/ഫിറ്റ്നസ് ദിനചര്യ എന്നിവ തയ്യാറാക്കുക.
    """
    log_personal_activity(
        f"Plan ({domain})",
        goal,
        f"Constraints/Budget: {constraints_or_budget or 'None specified'}",
        status="Planned",
    )
    return (
        f"[Personal Plan - {domain}] '{goal}' എന്ന ലക്ഷ്യത്തിനുള്ള ഘട്ടം ഘട്ടമായുള്ള പ്ലാൻ "
        f"({constraints_or_budget or 'സാധാരണ മുൻഗണനകൾ'}) തയ്യാറാക്കി."
    )


def summarize_and_reflect(focus_area: str, key_points: str = "") -> str:
    """
    പഠന സംഗ്രഹം, പ്രതിദിന അവലോകനം, അടുത്ത ഘട്ടങ്ങൾ, അല്ലെങ്കിൽ പ്രധാന തീരുമാനങ്ങൾ തയ്യാറാക്കുക.
    """
    log_personal_activity(
        "Reflection / Summary",
        focus_area,
        key_points[:140],
        status="Reviewed",
    )
    return f"[Reflection - {focus_area}] സംഗ്രഹവും അടുത്ത ഘട്ടങ്ങളും തയ്യാറാക്കി."


TOOL_FUNCTIONS = {
    "manage_personal_notes": manage_personal_notes,
    "manage_tasks_and_schedule": manage_tasks_and_schedule,
    "create_personal_plan": create_personal_plan,
    "summarize_and_reflect": summarize_and_reflect,
}

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "manage_personal_notes",
            "description": "Save, read, list, or append personal notes (.md files).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["save", "read", "list", "append"],
                        "description": "Action to perform on personal notes.",
                    },
                    "note_title": {
                        "type": "string",
                        "description": "Title of the note.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Note body text to save or append.",
                    },
                },
                "required": ["action", "note_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_tasks_and_schedule",
            "description": "Manage personal tasks, reminders, and schedules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action such as add, update, complete, or reminder.",
                    },
                    "item_title": {
                        "type": "string",
                        "description": "Task or event title.",
                    },
                    "time_or_priority": {
                        "type": "string",
                        "description": "Time, deadline, or priority level.",
                    },
                    "requires_approval": {
                        "type": "boolean",
                        "description": "Set True if human confirmation is needed before applying a major change.",
                    },
                },
                "required": ["action", "item_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_personal_plan",
            "description": "Create structured plans for travel, study, budget, or health/fitness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain such as Travel, Study, Budget, or Health.",
                    },
                    "goal": {
                        "type": "string",
                        "description": "The main personal goal.",
                    },
                    "constraints_or_budget": {
                        "type": "string",
                        "description": "Budget, time limits, or preferences.",
                    },
                },
                "required": ["domain", "goal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_and_reflect",
            "description": "Create summaries, daily briefings, next steps, or reflections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "focus_area": {
                        "type": "string",
                        "description": "Topic or area being summarized.",
                    },
                    "key_points": {
                        "type": "string",
                        "description": "Key points or notes to summarize.",
                    },
                },
                "required": ["focus_area"],
            },
        },
    },
]


# ==========================================
# 2. API KEY & GROQ AGENT LOOP
# ==========================================

def get_groq_api_key() -> str | None:
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return os.environ.get("GROQ_API_KEY")


SYSTEM_INSTRUCTION = (
    "നിങ്ങൾ ഒരു വ്യക്തിഗത AI ഏജന്റാണ് (Personal AI Agent). "
    "ഉപയോക്താവിന്റെ ദൈനംദിന ടാസ്കുകൾ, ഷെഡ്യൂൾ, നോട്ടുകൾ, പഠനം, യാത്ര/ബജറ്റ് പ്ലാനിംഗ് എന്നിവയിൽ "
    "ഘട്ടം ഘട്ടമായി സഹായിക്കുക. ലഭ്യമായ ടൂളുകൾ ഉപയോഗിച്ച് വിവരങ്ങൾ സേവ് ചെയ്യുകയും പ്ലാൻ ചെയ്യുകയും ചെയ്യുക. "
    "പ്രധാനപ്പെട്ടതോ സംശയാസ്പദമായതോ ആയ മാറ്റങ്ങളിൽ (പ്രത്യേകിച്ച് സമയമാറ്റങ്ങൾ, പ്രധാന തീരുമാനങ്ങൾ) "
    "ഉപയോക്താവിന്റെ അനുമതി (Human-in-the-loop) ചോദിക്കുകയും, വ്യക്തമായ ചെക്കുകൾ പാലിക്കുകയും ചെയ്യുക. "
    "മറുപടി വ്യക്തവും പ്രായോഗികവും മലയാളത്തിലുമായിരിക്കണം."
)


def run_groq_agent(api_key: str, chat_history: list[dict], user_text: str) -> str:
    client = Groq(api_key=api_key)

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in chat_history:
        if msg["role"] in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_text})

    max_iterations = 6
    for _ in range(max_iterations):
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=GROQ_TOOLS,
            tool_choice="auto",
            temperature=0.35,
        )

        assistant_msg = completion.choices[0].message
        tool_calls = assistant_msg.tool_calls or []

        if not tool_calls:
            return assistant_msg.content or "ജോലി പൂർത്തിയായി."

        messages.append(
            {
                "role": "assistant",
                "content": assistant_msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tc in tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                fn_args = {}

            fn = TOOL_FUNCTIONS.get(fn_name)
            if fn:
                try:
                    tool_result = fn(**fn_args)
                except TypeError as exc:
                    tool_result = f"[Tool Argument Error] {exc}"
            else:
                tool_result = f"[Unknown Tool] '{fn_name}' ലഭ്യമല്ല."

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(tool_result),
                }
            )

    final_completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.35,
    )
    return final_completion.choices[0].message.content or "ജോലി പൂർത്തിയായി."


# ==========================================
# 3. STREAMLIT UI
# ==========================================

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

api_key = get_groq_api_key()

st.title("🧠 Personal AI Agent (Groq)")
st.caption("നിങ്ങളുടെ വ്യക്തിഗത ടാസ്കുകൾ, നോട്ടുകൾ, പ്ലാനുകൾ, പ്രതിദിന അവലോകനം എന്നിവയ്ക്കുള്ള AI ഏജന്റ്.")

if not api_key:
    st.warning(
        '`GROQ_API_KEY` കണ്ടെത്താനായില്ല. Streamlit Cloud-ൽ **Secrets**-ൽ `GROQ_API_KEY = "നിങ്ങളുടെ_GROQ_KEY"` എന്ന് ചേർക്കുക.'
    )
    st.stop()

col_left, col_right = st.columns([1.35, 1])

with col_left:
    st.subheader("ചാറ്റ് & വ്യക്തിഗത സഹായം")

    if st.button("☀️ ഇന്നത്തെ പേഴ്സണൽ ബ്രീഫിംഗ് തയ്യാറാക്കുക"):
        brief_prompt = (
            "ഇന്നത്തെ എന്റെ വ്യക്തിഗത ടാസ്കുകൾ, നോട്ടുകൾ, അടുത്ത ഘട്ടങ്ങൾ എന്നിവ അടിസ്ഥാനമാക്കി "
            "ചെറിയൊരു പ്രതിദിന അവലോകനവും (Daily Briefing) മുൻഗണനാ ലിസ്റ്റും തയ്യാറാക്കുക."
        )
        st.session_state.messages.append({"role": "user", "content": brief_prompt})
        with st.spinner("ദൈനംദിന അവലോകനം തയ്യാറാക്കുന്നു..."):
            reply = run_groq_agent(api_key, st.session_state.messages[:-1], brief_prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input(
        "ഉദാ: 'ദുബായ് യാത്രാ പ്ലാൻ' തയ്യാറാക്കുക, അല്ലെങ്കിൽ 'AI ചാമ്പ്യൻഷിപ്പ് ഐഡിയ' നോട്ട് സേവ് ചെയ്യുക..."
    )

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("ഏജന്റ് പ്രവർത്തിക്കുന്നു..."):
                reply_text = run_groq_agent(api_key, st.session_state.messages[:-1], user_prompt)
                st.markdown(reply_text)

        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.rerun()

with col_right:
    st.subheader("📓 പേഴ്സണൽ നോട്ടുകൾ (`personal_notes/`)")
    note_files = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md"))

    if note_files:
        chosen = st.selectbox("നോട്ട് തിരഞ്ഞെടുക്കുക", note_files)
        with open(os.path.join(NOTES_DIR, chosen), "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("ഇതുവരെ നോട്ടുകൾ ഒന്നും സേവ് ചെയ്തിട്ടില്ല.")

    st.divider()
    st.subheader("📌 സ്ഥിരമായ ആക്റ്റിവിറ്റി & മെമ്മറി ലോഗ്")
    logs_df = load_personal_logs_df()

    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True, hide_index=True)
        csv_bytes = logs_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 ലോഗുകൾ CSV ആയി ഡൗൺലോഡ് ചെയ്യുക",
            data=csv_bytes,
            file_name="personal_ai_agent_logs.csv",
            mime="text/csv",
        )
    else:
        st.info("ഏജന്റ് ചെയ്യുന്ന ടാസ്കുകളും പ്ലാനുകളും ഇവിടെ സ്ഥിരമായി രേഖപ്പെടുത്തും.")

    if st.button("ചാറ്റ് ഹിസ്റ്ററി ക്ലിയർ ചെയ്യുക"):
        st.session_state.messages = []
        st.rerun()