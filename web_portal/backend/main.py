from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add parent directory to sys.path to import platform_gateway
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from platform_gateway.validator import PolicyValidator
from platform_gateway.cli import generate_terraform

app = FastAPI(title="BaFin Self-Service Data Portal")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
