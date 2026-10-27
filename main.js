// ====== SETTINGS ======
// Backend ka address. IP badle to sirf yahi ek line change karni hai.
const BASE_URL = "http://10.149.229.176:8000";

// Dropdown ke naam -> backend ke leave codes
// (CL pakka hai; SL aur AL backend ke policy.json se match kar lena)
const LEAVE_MAP = {
  "Casual Leave": "CL",
  "Sick Leave": "SL",
  "Annual Leave": "AL"
};

// /check se mila token yahan rakha jaata hai, /confirm me bhejne ke liye
let currentToken = null;

// List/text/object kuch bhi aaye, usko readable text bana deta hai
function toText(value) {
  if (value === undefined || value === null) return "";
  if (Array.isArray(value)) return value.map(toText).filter(Boolean).join(" ");
  if (typeof value === "object") return Object.values(value).map(toText).join(" ");
  return String(value);
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const confirmButton = document.getElementById("confirmRequest");

  // ====== SUBMIT: /check ======
  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const employeeId = form.querySelector('input[type="text"]').value.trim();
    const leaveType = form.querySelector("select").value;
    const dates = form.querySelectorAll('input[type="date"]');
    const startDate = dates[0].value;
    const endDate = dates[1].value;
    const reason = form.querySelector("textarea").value;

    if (!employeeId || !startDate || !endDate) {
      alert("Please fill Employee ID, Start Date and End Date.");
      return;
    }

    if (new Date(endDate) < new Date(startDate)) {
      alert("End Date cannot be before Start Date!");
      return;
    }

    // Request ka summary dikhao
    setText("resultEmployee", employeeId);
    setText("resultLeaveType", leaveType);
    setText("resultReason", reason);
    setText("resultStartDate", startDate);
    setText("resultEndDate", endDate);

    // Backend ko call
    let data;
    try {
      const res = await fetch(BASE_URL + "/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employee_id: employeeId,
          leave_type: LEAVE_MAP[leaveType] || leaveType,
          start_date: startDate,
          end_date: endDate,
          reason: reason
        })
      });

      if (!res.ok) {
        alert("Server error: " + res.status + ". Input check karo.");
        return;
      }
      data = await res.json();
    } catch (err) {
      console.error(err);
      alert("Server se connect nahi ho paya. Backend chalu hai aur same WiFi hai?");
      return;
    }

    currentToken = data.token || null;

    // Result dikhao
    setText(
      "leaveBalance",
      data.balance !== undefined ? data.balance + " days available" : "Employee ID not found"
    );
    setText("workingDays", (data.days ?? 0) + " working day(s)");
    setText("eligibilityStatus", data.eligible ? "Eligible" : "Not Eligible");
    setText(
      "policyExplanation",
      toText(data.problems) || "Policy rules satisfied."
    );
    setText(
      "alternativeSuggestions",
      toText(data.alternatives) || toText(data.notes) || "-"
    );

    // Confirm button tabhi chale jab eligible ho aur token mila ho
    if (confirmButton) {
      confirmButton.disabled = !(data.eligible && currentToken);
    }

    const target = document.getElementById("resultEmployee");
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  // ====== CONFIRM BUTTON: /confirm ======
  if (confirmButton) {
    confirmButton.addEventListener("click", async function () {
      if (!currentToken) {
        alert("Pehle eligibility check karo.");
        return;
      }

      try {
        const res = await fetch(BASE_URL + "/confirm", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: currentToken })
        });
        const d = await res.json();

        alert(toText(d.message) + (d.request_id ? " (ID: " + d.request_id + ")" : ""));

        // Ek token se ek hi baar confirm hoga
        currentToken = null;
        confirmButton.disabled = true;
      } catch (err) {
        console.error(err);
        alert("Server se connect nahi ho paya.");
      }
    });
  } else {
    console.error("Confirm button not found!");
  }
});