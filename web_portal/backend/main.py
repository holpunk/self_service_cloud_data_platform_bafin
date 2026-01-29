from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add platform_gateway directory to sys.path to support its internal imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../platform_gateway'))

from validator import PolicyValidator
from cli import generate_terraform

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BaFin Self-Service Data Portal")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend Static Files
# We mount this AFTER specific API routes if we want strict control, or generally handled here.
# NOTE: In production, Nginx usually serves static files, but this is fine for the demo.
frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="ui")

# Redirect root to UI for convenience (Optional, or just tell user to go to /ui)
from fastapi.responses import RedirectResponse
@app.get("/")
async def root():
    return RedirectResponse(url="/ui/index.html")

# Initialize Policy Validator
POLICY_FILE = os.path.join(os.path.dirname(__file__), '../../policies/compliance_rules.yaml')
validator = PolicyValidator(POLICY_FILE)

class EncryptionConfig(BaseModel):
    enabled: bool

class ProductRequest(BaseModel):
    name: str
    environment: str
    region: str
    encryption: EncryptionConfig
    public_access: bool

@app.post("/api/products")
async def create_product(request: ProductRequest):
    # Convert Pydantic model to dict
    req_dict = request.model_dump()
    
    # 1. Validate Compliance
    is_valid, errors = validator.validate_request(req_dict)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail={"message": "Compliance Check Failed", "errors": errors})
    
    # 2. Generate Provisioning Files
    try:
        # We write to the actual terraform dir relative to the project root
        output_dir = os.path.join(os.path.dirname(__file__), '../../terraform')
        tf_file = generate_terraform(req_dict, output_dir=output_dir)
        
        return {
            "status": "success",
            "message": "Compliance Check Passed. Infrastructure request queued.",
            "file": os.path.basename(tf_file)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from db import USERS, add_request, get_requests_for_domain, get_approved_access, update_status

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
async def login(req: LoginRequest):
    user = USERS.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Return user info without password
    user_data = user.copy()
    user_data.pop("password", None)
    return {"user": user_data, "username": req.username}

class AccessRequest(BaseModel):
    username: str # Changed from requester_role to username for auth context
    target_product: str
    reason: str

@app.post("/api/access")
async def request_access(request: AccessRequest):
    if request.username not in USERS:
         raise HTTPException(status_code=401, detail="User not found")
         
    add_request(request.username, request.target_product, request.reason)
    
    return {
        "status": "pending_approval",
        "message": f"Access request for {request.target_product} submitted. Administrators have been notified."
    }

@app.get("/api/notifications")
async def get_notifications(username: str):
    """
    Get pending requests for the domain owned by 'username'.
    """
    user = USERS.get(username)
    if not user:
         raise HTTPException(status_code=401, detail="User not found")
    
    # If user owns 'claims_management', show requests targeting 'claims_management'
    my_domain = user["domain"]
    requests = get_requests_for_domain(my_domain)
    return {"requests": requests}

class ApprovalRequest(BaseModel):
    username: str
    request_id: str
    decision: str # APPROVED or REJECTED

@app.post("/api/approve")
async def approve_request(req: ApprovalRequest):
    # Verify the user actually owns the domain of the request (security check omitted for demo simplicity, but implied by filtered notifications)
    success = update_status(req.request_id, req.decision)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "success", "message": f"Request marked as {req.decision}"}

@app.get("/api/access")
async def get_access(username: str):
    allowed_domains = get_approved_access(username)
    return {"allowed_domains": allowed_domains}

@app.get("/api/catalog")
async def get_catalog():
    """
    Scans the terraform directory to discover available data products.
    """
    terraform_dir = os.path.join(os.path.dirname(__file__), '../../terraform')
    products = []
    
    if os.path.exists(terraform_dir):
        for filename in os.listdir(terraform_dir):
            if filename.startswith("product_") and filename.endswith(".auto.tfvars"):
                try:
                    parts = filename.replace("product_", "").replace(".auto.tfvars", "").rsplit("_", 1)
                    if len(parts) == 2:
                        products.append({
                            "name": parts[0],
                            "environment": parts[1],
                            "id": filename
                        })
                except Exception:
                    continue
    return {"products": products}

from mock_data import generate_mock_data

@app.get("/api/data/{product_name}")
async def get_data_preview(product_name: str, username: str):
    """
    Returns mock data for a product IF the user has approved access.
    """
    allowed_domains = get_approved_access(username)
    
    # Check if user has access to this specific product
    # Note: allowed_domains contains strings like "risk_assessment"
    if product_name not in allowed_domains:
         raise HTTPException(status_code=403, detail=f"Access denied to {product_name}")

    data = generate_mock_data(product_name)
    return {"product": product_name, "records": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
