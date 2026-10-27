Live app: https://transcendent-gnome-27ca53.netlify.app
Backend API: https://leave-advisory-agent.onrender.com/docs
# Employee Leave Advisory Agent

A leave-management project with a FastAPI backend and an HTML/JavaScript frontend.
An employee enters leave details, the backend checks eligibility against the leave policy and balance,
and a confirmed request is saved with the status **pending approval**.

## Features

- Checks leave eligibility (balance, policy rules, working days)
- Shows problems and alternative suggestions when a request is not eligible
- Gives a one-time token for an eligible request
- Confirms the request using that token and saves it to `requests.csv`
- Cancels a pending request using the token
- Handles invalid input (unknown employee ID, balance exceeded, end date before start date)

## Project Structure

**Backend**

| File | Purpose |
|---|---|
| `api.py` | FastAPI app with the `/check`, `/confirm` and `/cancel` endpoints |
| `leave_logic.py` | Eligibility checking logic |
| `tools.py`, `agent.py` | Helper functions and agent logic |
| `balances.json` | Leave balance of each employee |
| `policy.json`, `leave_policy.txt` | Leave policy rules |
| `requests.csv` | Saved leave requests |
| `requirements.txt` | Python dependencies |

**Frontend**

| File | Purpose |
|---|---|
| `main.html` | Leave application page |
| `main.js` | Form handling and API calls |
| `main.css` | Styling |

## How to Run

### 1. Backend

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API documentation opens at `http://127.0.0.1:8000/docs`.

### 2. Frontend

1. Open `main.js` and set `BASE_URL` at the top to the backend address,
   for example `http://127.0.0.1:8000` (same laptop) or `http://<backend-laptop-ip>:8000` (different laptop on the same WiFi).
2. Open `main.html` in a browser.

## API Endpoints

### POST `/check`

Request:
```json
{
  "employee_id": "E101",
  "leave_type": "CL",
  "start_date": "2026-11-02",
  "end_date": "2026-11-03",
  "reason": "Personal work"
}
```

Response (eligible):
```json
{
  "eligible": true,
  "days": 2,
  "balance": 8,
  "problems": [],
  "alternatives": [],
  "notes": [],
  "token": "f77d92d3215746dbbf01d3650954b7c3"
}
```

When `eligible` is `false`, the `problems` list explains why. No token is returned.

### POST `/confirm`

Request:
```json
{ "token": "f77d92d3215746dbbf01d3650954b7c3" }
```

Response:
```json
{ "saved": true, "request_id": "LR-0003", "message": "Request pending approval." }
```

### POST `/cancel`

Request:
```json
{ "token": "f77d92d3215746dbbf01d3650954b7c3" }
```

Response:
```json
{ "message": "Cancelled." }
```

## Example Flow

1. Employee `E101` applies for Casual Leave (CL) from 2026-11-02 to 2026-11-03.
2. `/check` returns `eligible: true`, 2 working days, balance 8, and a token.
3. The user clicks **Confirm & Submit Request**. `/confirm` saves the request as `pending`.

## Test Cases Covered

| Case | Result |
|---|---|
| Valid request (E101, CL, 2 days) | Eligible, token returned |
| Days more than balance | Not eligible, reason shown |
| Unknown employee ID (E999) | Not eligible, "Employee ID not found" |
| Short notice for CL | Not eligible, policy reason shown |
| End date before start date | Blocked in the frontend |

## Notes and Limitations

- Pending tokens are stored in memory. Restarting the server clears them, so run `/check` again after a restart.
- Requests are saved in `requests.csv`. There is no approval endpoint yet; approval by a manager is a possible next step.
- Both laptops must be on the same WiFi when the frontend and backend run on different machines.
- Do not share or upload the `.env` file.
