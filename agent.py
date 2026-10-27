from datetime import date
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import (get_leave_policy, check_balance,
                   calc_working_days, save_pending_request)

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", timeout=60, max_retries=2)
tools = [get_leave_policy, check_balance,
         calc_working_days, save_pending_request]

SYSTEM_PROMPT = f"""You are a Leave Advisory assistant for employees.
Today's date is {date.today().isoformat()}.

Follow these steps:
1. If you don't know the employee ID, ask for it first.
2. Use get_leave_policy for rules, check_balance for balance, and
   calc_working_days for the number of leave days. Never guess these.
3. Explain clearly whether the employee is eligible (balance, max
   consecutive days, advance notice). If not eligible, suggest
   alternatives (another leave type, shorter duration, other dates).
4. If eligible, summarise the request and ask: "Should I submit this?"
5. Call save_pending_request with confirmed=True ONLY after the
   employee clearly says yes. Never save before that.
Reply in the same language the employee uses."""

agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

if __name__ == "__main__":
    history = []
    while True:
        q = input("You: ")
        if q.lower() in ("exit", "quit"):
            break
        history.append({"role": "user", "content": q})
        result = agent.invoke({"messages": history})
        history = result["messages"]
        for m in history:
            if m.type == "ai" and m.tool_calls:
                print("TOOL CALL:", m.tool_calls)
        print("Agent:", history[-1].text, "\n")