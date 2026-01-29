import random
from datetime import datetime, timedelta

def mask_email(email, role):
    if role == "reader":
        user, domain = email.split('@')
        return f"{user[:1]}****@{domain}"
    return email

def generate_mock_data(product_name, role="reader"):
    """
    Generates a list of mock records based on the product name.
    Masks sensitive data if role is 'reader'.
    """
    data = []
    
    if "risk" in product_name.lower():
        for i in range(1, 11):
            email = f"customer{i}@example.com"
            data.append({
                "id": f"R-{1000+i}",
                "customer_id": f"CUST-{random.randint(500, 999)}",
                "email": mask_email(email, role),
                "risk_score": random.randint(1, 100),
                "assessment_date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "status": random.choice(["Low", "Medium", "High", "Critical"])
            })
            
    elif "claim" in product_name.lower():
        for i in range(1, 11):
            email = f"claimant{i}@insurance.co"
            data.append({
                "claim_id": f"CLM-{202400+i}",
                "email": mask_email(email, role),
                "policy_id": f"POL-{random.randint(1000, 9999)}",
                "amount_eur": round(random.uniform(500.0, 50000.0), 2),
                "filing_date": (datetime.now() - timedelta(weeks=i)).strftime("%Y-%m-%d"),
                "status": random.choice(["Filed", "Investigating", "Settled", "Rejected"])
            })
            
    elif "policy" in product_name.lower():
        for i in range(1, 11):
            email = f"policyholder{i}@bafin.de"
            data.append({
                "policy_no": f"POL-{1000+i}",
                "holder_name": f"Customer {i}",
                "email": mask_email(email, role),
                "type": random.choice(["Auto", "Home", "Health", "Liability"]),
                "premium_eur": random.randint(200, 2000),
                "start_date": "2025-01-01",
                "active": True
            })
    else:
        # Generic data for unknown products
        for i in range(1, 6):
            data.append({
                "record_id": i,
                "info": f"Sample data for {product_name}",
                "timestamp": datetime.now().isoformat()
            })
            
    return data
