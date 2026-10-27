import json
from datetime import date, timedelta
from langchain_core.tools import tool

HOLIDAYS = {"2026-11-08", "2026-12-25"}  # sample holidays


def _count_days(start, end):
    d, e, count = date.fromisoformat(start), date.fromisoformat(end), 0
    while d <= e:
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS:
            count += 1
        d += timedelta(days=1)
    return count


@tool
def get_leave_policy() -> str:
    """Return the company leave policy rules."""
    with open("leave_policy.txt", encoding="utf-8") as f:
        return f.read()


@tool
def check_balance(employee_id: str, leave_type: str) -> str:
    """Check remaining leave balance. leave_type is CL, SL or EL."""
    with open("balances.json", encoding="utf-8") as f:
        data = json.load(f)
    emp = data.get(employee_id)
    if not emp:
        return "Employee not found."
    return f"{emp['name']} has {emp.get(leave_type, 0)} days of {leave_type} left."


@tool
def calc_working_days(start_date: str, end_date: str) -> str:
    """Count working days between two dates (YYYY-MM-DD), excluding weekends and holidays."""
    return f"{_count_days(start_date, end_date)} working days"


@tool
def save_pending_request(employee_id: str, leave_type: str,
                         start_date: str, end_date: str,
                         confirmed: bool) -> str:
    """Save a pending leave request. Call ONLY after the employee
    has clearly said yes. Set confirmed=True only then."""
    if not confirmed:
        return "Not saved. Employee has not confirmed yet."
    try:
        with open("requests.json", encoding="utf-8") as f:
            requests = json.load(f)
    except FileNotFoundError:
        requests = []
    requests.append({
        "employee_id": employee_id, "leave_type": leave_type,
        "start_date": start_date, "end_date": end_date,
        "status": "pending",
    })
    with open("requests.json", "w", encoding="utf-8") as f:
        json.dump(requests, f, indent=2)
    return "Request saved with status: pending."