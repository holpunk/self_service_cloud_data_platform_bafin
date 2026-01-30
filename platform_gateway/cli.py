import click
import yaml
import os
import sys
from validator import PolicyValidator

POLICY_FILE = os.path.join(os.path.dirname(__file__), '../policies/compliance_rules.yaml')

@click.group()
def cli():
    """BaFin Compliant Self-Service Platform Gateway"""
    pass

@cli.command()
@click.option('--file', '-f', required=True, help='Path to the product definition YAML file.')
def create_product(file):
    """Request a new data product."""
    click.echo(f"Processing request from: {file}")
    
    try:
        with open(file, 'r') as f:
            request = yaml.safe_load(f)
    except Exception as e:
        click.echo(f"Error reading file: {e}")
        sys.exit(1)

    validator = PolicyValidator(POLICY_FILE)
    is_valid, errors = validator.validate_request(request)

    if not is_valid:
        click.echo(click.style("COMPLIANCE CHECK FAILED!", fg="red", bold=True))
        for err in errors:
            click.echo(f" - {err}")
        sys.exit(1)
    else:
        click.echo(click.style("Compliance Check Passed.", fg="green"))
        click.echo("Generating Terraform configuration...")
        
        # Simulation of Terraform Generation
        generate_terraform(request)

import json

def generate_terraform(request, output_dir='terraform'):
    """
    Updates the products.auto.tfvars.json file with the new product request.
    Returns the path to the updated file.
    """
    product_name = request['name']
    env = request['environment']
    
    # Ensure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tfvars_path = os.path.join(output_dir, "products.auto.tfvars.json")
    
    # Load existing data or initialize
    data = {"products": {}}
    if os.path.exists(tfvars_path):
        try:
            with open(tfvars_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass # Start fresh if corrupted
    
    # Key for the product map
    key = f"{product_name}_{env}"
    
    # Add/Update product definition
    data["products"][key] = {
        "name": product_name,
        "environment": env,
        "kms_key_arn": "arn:aws:kms:eu-central-1:123456789012:key/simulation-key"
    }
    
    # Write back to file
    with open(tfvars_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return tfvars_path

if __name__ == '__main__':
    cli()
