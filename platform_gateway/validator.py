import yaml
import os

class PolicyValidator:
    def __init__(self, policy_file):
        with open(policy_file, 'r') as f:
            self.policies = yaml.safe_load(f)

    def validate_request(self, request):
        """
        Validates a user request against the platform policies.
        Returns a tuple (bool, list_of_errors).
        """
        errors = []
        
        # 1. Environment Check
        allowed_envs = self.policies['general']['allowed_environments']
        if request.get('environment') not in allowed_envs:
            errors.append(f"Invalid environment '{request.get('environment')}'. Allowed: {allowed_envs}")

        # 2. Region Check (Data Residency)
        required_region = self.policies['aws']['region']
        if request.get('region') != required_region:
            errors.append(f"Invalid region '{request.get('region')}'. Compliance requires: {required_region}")

        # 3. Encryption Check
        if not request.get('encryption', {}).get('enabled'):
             errors.append("Encryption must be enabled for all data products.")
        
        # 4. Network Exposure Check
        if request.get('public_access', False):
            errors.append("Public access is strictly prohibited by BaFin regulations. Use PrivateLink.")

        return len(errors) == 0, errors
