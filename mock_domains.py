import sys
import os

# Add platform_gateway to path
sys.path.append(os.path.join(os.getcwd(), 'platform_gateway'))

from cli import generate_terraform

domains = [
    {
        "name": "claims_management",
        "environment": "prod",
        "region": "eu-central-1",
        "encryption": {"enabled": True}, 
        "public_access": False
    },
    {
        "name": "policy_administration",
        "environment": "prod",
        "region": "eu-central-1",
        "encryption": {"enabled": True}, 
        "public_access": False
    },
    {
        "name": "risk_assessment",
        "environment": "prod",
        "region": "eu-central-1",
        "encryption": {"enabled": True}, 
        "public_access": False
    }
]

print("Generating Mock Domains...")
for d in domains:
    # Use the existing logic to generate the tfvars
    # We output to the 'terraform' directory
    output_file = generate_terraform(d, output_dir='terraform')
    print(f" - Created Domain: {d['name']} -> {output_file}")
