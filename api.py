import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from leave_logic import check_eligibility, save_request

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

pending = {}  # token -> checked request


class CheckIn(BaseModel):
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    reason: str = ""


class TokenIn(BaseModel):
    token: str


@app.post("/check")
def check(b: CheckIn):
    r = check_eligibility(b.employee_id.strip(), b.leave_type,
                          b.start_date, b.end_date)
    if r["eligible"]:
        token = uuid.uuid4().hex
        pending[token] = {**b.model_dump(), "days": r["days"]}
        r["token"] = token
    return r


@app.post("/confirm")
def confirm(b: TokenIn):
    p = pending.pop(b.token, None)
    if not p:
        return {"saved": False,
                "message": "Request expire ho gayi, dobara check karo."}
    return {"saved": True, "request_id": save_request(p),
            "message": "Request pending approval mein hai."}


@app.post("/cancel")
def cancel(b: TokenIn):
    pending.pop(b.token, None)
    
    return {"message": "Cancelled."}