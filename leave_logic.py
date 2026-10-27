import csv, os
import json
from datetime import date, datetime, timedelta


with open("policy.json", encoding="utf-8") as f:
    POLICY = json.load(f)

RULES = POLICY["rules"]
HOLIDAYS = set(POLICY["holidays"])


def _count_days(start, end):
    d, e, count = date.fromisoformat(start), date.fromisoformat(end), 0
    while d <= e:
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS:
            count += 1
        d += timedelta(days=1)
    return count 

def _fail(msg):
    return {"eligible": False, "days": 0, "problems": [msg],
            "alternatives": [], "notes": []}


def check_eligibility(emp_id, leave_type, start, end):
    with open("balances.json", encoding="utf-8") as f:
        emp = json.load(f).get(emp_id)
    if not emp:
        return _fail("Employee ID nahi mili.")
    if leave_type not in RULES:
        return _fail("Leave type galat hai.")

    s, e = date.fromisoformat(start), date.fromisoformat(end)
    if e < s:
        return _fail("End date, start date se pehle hai.")

    days = _count_days(start, end)
    rule = RULES[leave_type]
    balance = emp.get(leave_type, 0)
    notice = (s - date.today()).days

    problems = []
    if days == 0:
        problems.append("In dates mein koi working day nahi hai.")
    if days > balance:
        problems.append(f"{leave_type} balance {balance} din hai, aapne {days} din maange.")
    if rule["max_days"] and days > rule["max_days"]:
        problems.append(f"{leave_type} mein ek baar mein max {rule['max_days']} din milte hain.")
    if notice < rule["advance"]:
        problems.append(f"{leave_type} ke liye kam se kam {rule['advance']} din pehle apply karna hota hai.")

    # जो दूसरा leave type सारे नियम पूरे करता हो, वो alternative बनेगा
    alternatives = []
    if problems and days > 0:
        for t, r in RULES.items():
            if (t != leave_type
                    and emp.get(t, 0) >= days
                    and (r["max_days"] is None or days <= r["max_days"])
                    and notice >= r["advance"]):
                alternatives.append(f"{t} le sakte ho ({emp.get(t, 0)} din balance).")

    notes = []
    if leave_type == "SL" and days > 2:
        notes.append("2 din se zyada ki SL ke liye medical certificate chahiye.")

    return {"eligible": not problems, "days": days, "balance": balance,
            "problems": problems, "alternatives": alternatives, "notes": notes}

CSV_FILE = "requests.csv"
FIELDS = ["request_id", "employee_id", "leave_type", "start_date",
          "end_date", "days", "reason", "status", "created_at"]


def _next_id():
    if not os.path.exists(CSV_FILE):
        return "LR-0001"
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        n = sum(1 for _ in csv.reader(f))  # header + rows
    return f"LR-{n:04d}"


def save_request(p):
    """p में employee_id, leave_type, start_date, end_date, days, reason चाहिए।"""
    rid = _next_id()
    exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow({
            "request_id": rid,
            "employee_id": p["employee_id"],
            "leave_type": p["leave_type"],
            "start_date": p["start_date"],
            "end_date": p["end_date"],
            "days": p["days"],
            "reason": p.get("reason", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
    return rid