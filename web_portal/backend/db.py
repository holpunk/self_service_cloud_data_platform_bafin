import json
import os
import uuid
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'db.json')

# Mock Users Config
USERS = {
    "alice": {"name": "Alice Admin", "role": "claims_management", "domain": "claims_management", "password": "password"},
    "bob": {"name": "Bob Manager", "role": "policy_administration", "domain": "policy_administration", "password": "password"},
    "charlie": {"name": "Charlie Risk", "role": "risk_assessment", "domain": "risk_assessment", "password": "password"}
}

def init_db():
    if not os.path.exists(DB_FILE):
        data = {"requests": []}
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)

def load_db():
    init_db()
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_request(requester, target_product, reason):
    db = load_db()
    new_req = {
        "id": str(uuid.uuid4()),
        "requester": requester,
        "role": USERS.get(requester, {}).get("role", "unknown"),
        "target_product": target_product,
        "reason": reason,
        "status": "PENDING",
        "timestamp": datetime.now().isoformat()
    }
    db["requests"].append(new_req)
    save_db(db)
    return new_req

def get_requests_for_domain(domain):
    db = load_db()
    # Return requests WHERE target_product == my domain AND status == PENDING
    return [r for r in db["requests"] if r["target_product"] == domain and r["status"] == "PENDING"]

def get_approved_access(user):
    db = load_db()
    # Return requests WHERE requester == user AND status == APPROVED
    # Also include their own domain by default? Yes.
    approved = [r["target_product"] for r in db["requests"] if r["requester"] == user and r["status"] == "APPROVED"]
    
    # Add implicit access to their own domain
    user_domain = USERS.get(user, {}).get("domain")
    if user_domain and user_domain not in approved:
        approved.append(user_domain)
        
    return approved

def update_status(request_id, status):
    db = load_db()
    for r in db["requests"]:
        if r["id"] == request_id:
            r["status"] = status
            save_db(db)
            return True
    return False
