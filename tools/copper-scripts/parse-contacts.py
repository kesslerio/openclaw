#!/usr/bin/env python3
"""Parse Google Contacts CSV and build contact management database."""

import csv
import json
from collections import defaultdict
from pathlib import Path

def parse_contacts(csv_path):
    contacts = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Build name
            first = row.get('First Name', '').strip()
            middle = row.get('Middle Name', '').strip()
            last = row.get('Last Name', '').strip()
            name_parts = [p for p in [first, middle, last] if p]
            full_name = ' '.join(name_parts) if name_parts else None
            
            # Get organization
            org = row.get('Organization Name', '').strip() or None
            title = row.get('Organization Title', '').strip() or None
            
            # Get primary email
            email = row.get('E-mail 1 - Value', '').strip() or None
            
            # Get all phones
            phones = []
            for i in range(1, 10):  # Check first 9 phone fields
                phone = row.get(f'Phone {i} - Value', '').strip()
                label = row.get(f'Phone {i} - Label', '').strip()
                if phone:
                    phones.append({'number': phone, 'label': label})
            
            # Get labels
            labels = row.get('Labels', '').strip()
            label_list = [l.strip() for l in labels.split(' ::: ')] if labels else []
            
            # Skip if no useful info
            if not full_name and not org and not email and not phones:
                continue
            
            contact = {
                'name': full_name or org or email or (phones[0]['number'] if phones else 'Unknown'),
                'first_name': first or None,
                'last_name': last or None,
                'organization': org,
                'title': title,
                'email': email,
                'phones': phones,
                'labels': label_list,
                # CRM fields (to be populated)
                'category': 'unknown',  # business, personal, team, network
                'frequency': 'unknown',  # hot, warm, cold, dormant
                'last_contacted': None,
                'contact_count_90d': 0,
                'notes': None
            }
            contacts.append(contact)
    
    return contacts

def categorize_by_labels(contacts):
    """Auto-categorize based on existing Google labels."""
    for c in contacts:
        labels_lower = [l.lower() for l in c['labels']]
        
        # Check for family
        if 'family' in labels_lower:
            c['category'] = 'personal'
        # Check for business indicators
        elif any(l in labels_lower for l in ['work', 'business', 'client', 'vendor']):
            c['category'] = 'business'
        # Check organization domain for business
        elif c['organization']:
            c['category'] = 'business'
    
    return contacts

def generate_summary(contacts):
    """Generate summary statistics."""
    total = len(contacts)
    with_phone = sum(1 for c in contacts if c['phones'])
    with_email = sum(1 for c in contacts if c['email'])
    with_org = sum(1 for c in contacts if c['organization'])
    
    # Category breakdown
    categories = defaultdict(int)
    for c in contacts:
        categories[c['category']] += 1
    
    return {
        'total': total,
        'with_phone': with_phone,
        'with_email': with_email,
        'with_organization': with_org,
        'categories': dict(categories)
    }

if __name__ == '__main__':
    import sys

    # Determine paths dynamically
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    output_dir = project_dir / 'data' / 'contacts'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get CSV path from command line or use default
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    else:
        # Try to find most recent CSV in common locations
        home = Path.home()
        search_paths = [
            home / '.clawdbot' / 'media' / 'inbound',
            project_dir / 'data' / 'contacts',
            Path.cwd()
        ]

        csv_path = None
        for search_dir in search_paths:
            if search_dir.exists():
                csv_files = list(search_dir.glob('*.csv'))
                if csv_files:
                    # Get most recent CSV
                    csv_path = max(csv_files, key=lambda p: p.stat().st_mtime)
                    break

        if not csv_path:
            print("Error: No CSV file found.")
            print("Usage: python parse-contacts.py [path-to-contacts.csv]")
            sys.exit(1)

    print(f"Using CSV: {csv_path}")
    
    print("Parsing contacts...")
    contacts = parse_contacts(csv_path)
    
    print("Auto-categorizing...")
    contacts = categorize_by_labels(contacts)
    
    print("Generating summary...")
    summary = generate_summary(contacts)
    
    # Save full database
    with open(output_dir / 'contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)
    
    # Save summary
    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n=== CONTACTS SUMMARY ===")
    print(f"Total contacts: {summary['total']}")
    print(f"With phone: {summary['with_phone']}")
    print(f"With email: {summary['with_email']}")
    print(f"With organization: {summary['with_organization']}")
    print(f"\nCategories:")
    for cat, count in summary['categories'].items():
        print(f"  {cat}: {count}")
    
    # Sample output
    print(f"\n=== SAMPLE CONTACTS ===")
    for c in contacts[:10]:
        phones = ', '.join([p['number'] for p in c['phones'][:2]]) if c['phones'] else 'N/A'
        print(f"  {c['name']} | {c['email'] or 'N/A'} | {phones}")
