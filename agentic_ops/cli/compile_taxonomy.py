import re
import sys

import yaml


def parse_markdown_table(filepath):
    risks = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|') or line.startswith('| :---'):
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 17:
                continue
                
            # parts[0] is empty, parts[1] is N°, parts[2] is ID...
            # Example: | **1** | `INFRA-001` | 1.1 | **Base de données indisponible** | Disponibilité | 5 | 3 | 2 | **30** (Faible) | ... | Vague | Testé ? | Statut | Réponse |
            
            raw_id = parts[2]
            risk_id_match = re.search(r'`([A-Z]+-\d+)`', raw_id)
            if not risk_id_match:
                continue
                
            risk_id = risk_id_match.group(1)
            
            # Clean title
            title = parts[4].replace('**', '').strip()
            
            # Parse gravity and detectability
            try:
                grav = int(parts[6])
                det = int(parts[8])
            except ValueError:
                continue
                
            # Extract vague
            vague = parts[16]
            # Extract tested
            tested = parts[17]
            
            if '1' in vague or '[x]' in tested or grav == 5:
                risks.append({
                    'id': risk_id,
                    'title': title,
                    'severity': grav,
                    'detectability': det,
                    'blast_radius': 2,
                    'allowed_actions': ['investigate', 'create_issue']
                })
                
    return risks

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compile_taxonomy.py <input.md> <output.yaml>")
        sys.exit(1)
        
    risks = parse_markdown_table(sys.argv[1])
    
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        yaml.dump(risks, f, default_flow_style=False, allow_unicode=True)
        
    print(f"Compiled {len(risks)} risks into {sys.argv[2]}")
