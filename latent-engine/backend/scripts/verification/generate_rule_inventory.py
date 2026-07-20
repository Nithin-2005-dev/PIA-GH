import json
from pathlib import Path
import sys

# Add backend to path
backend_path = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, backend_path)

from app.causal.rules import (
    DocumentationRuleProvider,
    OwnershipRuleProvider,
    ReviewRuleProvider,
    ExpertiseRuleProvider,
    VelocityRuleProvider
)
from app.kernel.reasoning.rule_engine import create_single_point_of_failure_rule

def generate_inventory():
    inventory = []
    
    providers = [
        DocumentationRuleProvider(),
        OwnershipRuleProvider(),
        ReviewRuleProvider(),
        ExpertiseRuleProvider(),
        VelocityRuleProvider()
    ]
    
    for provider in providers:
        for rule in provider.rules():
            inventory.append({
                "rule_id": rule.id,
                "source_file": "app/causal/rules.py",
                "registry": "CausalRuleRegistry",
                "inputs": [rule.cause_node],
                "outputs": [rule.effect_node],
                "dependencies": [],
                "confidence_model": "static",
                "legacy_engine": "CausalEngine",
                "migration_status": "PENDING",
                "family": provider.name,
                "description": rule.description
            })
            
    # Add the single point of failure rule we found earlier
    kernel_rule = create_single_point_of_failure_rule()
    inventory.append({
        "rule_id": kernel_rule.id,
        "source_file": "app/kernel/reasoning/rule_engine.py",
        "registry": "kernel.RuleRegistry",
        "inputs": ["bus_factor"],
        "outputs": ["Knowledge Concentration Risk"],
        "dependencies": [],
        "confidence_model": "dynamic",
        "legacy_engine": "kernel.GraphEngine",
        "migration_status": "MIGRATED",
        "family": "risk",
        "description": kernel_rule.name
    })

    # Save to artifacts directory directly
    out_dir = Path(r"C:\Users\NITHIN\.gemini\antigravity-ide\brain\19a471b5-76a4-418f-b441-d6fb44f5cc9d")
    
    inventory_path = out_dir / "RuleInventory.json"
    inventory_path.write_text(json.dumps(inventory, indent=2))
    print(f"Generated RuleInventory.json with {len(inventory)} rules.")
    
    # Phase 2: Group into families
    families = {}
    for item in inventory:
        fam = item["family"]
        if fam not in families:
            families[fam] = []
        families[fam].append(item["rule_id"])
        
    families_path = out_dir / "RuleFamilies.json"
    families_path.write_text(json.dumps(families, indent=2))
    print(f"Generated RuleFamilies.json with {len(families)} families.")

if __name__ == "__main__":
    generate_inventory()
