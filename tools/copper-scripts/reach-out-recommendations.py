#!/usr/bin/env python3
"""Generate daily reach-out recommendations based on contact frequency."""

import json
import random
from pathlib import Path
from datetime import datetime

def load_contacts():
    # Determine paths dynamically
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data' / 'contacts'

    contacts_file = data_dir / 'contacts.json'
    if not contacts_file.exists():
        raise FileNotFoundError(f"Contacts file not found: {contacts_file}\nRun parse-contacts.py first.")

    with open(contacts_file) as f:
        return json.load(f)

def get_recommendations(contacts, count=5):
    """Get contacts to reach out to today."""
    recommendations = []
    
    # Priority 1: Warm contacts (maintain relationship)
    warm = [c for c in contacts if c['frequency'] == 'warm' and c['category'] == 'business']
    if warm:
        recommendations.extend(random.sample(warm, min(2, len(warm))))
    
    # Priority 2: Cold business contacts (re-engage)
    cold_biz = [c for c in contacts if c['frequency'] in ['cold', 'dormant'] 
                and c['category'] == 'business' 
                and (c.get('email') or (c.get('phones') and len(c['phones']) > 0))]
    if cold_biz:
        recommendations.extend(random.sample(cold_biz, min(2, len(cold_biz))))
    
    # Priority 3: Personal contacts (stay in touch)
    personal = [c for c in contacts if c['category'] == 'personal' 
                and (c.get('email') or (c.get('phones') and len(c['phones']) > 0))]
    if personal:
        recommendations.extend(random.sample(personal, min(1, len(personal))))
    
    return recommendations[:count]

def format_recommendation(contact):
    """Format a contact recommendation."""
    phone = contact['phones'][0]['number'] if contact.get('phones') else None
    
    return {
        'name': contact['name'],
        'category': contact['category'],
        'frequency': contact['frequency'],
        'email': contact.get('email'),
        'phone': phone,
        'organization': contact.get('organization'),
        'suggested_action': 'Quick check-in message' if contact['category'] == 'personal' 
                          else 'Follow up on business opportunity'
    }

def generate_daily_recommendations():
    """Generate and save daily recommendations."""
    contacts = load_contacts()
    recs = get_recommendations(contacts)

    formatted = [format_recommendation(c) for c in recs]

    # Save to file
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data' / 'contacts'

    output = {
        'date': datetime.now().isoformat(),
        'recommendations': formatted
    }

    with open(data_dir / 'daily-recommendations.json', 'w') as f:
        json.dump(output, f, indent=2)

    return formatted

if __name__ == '__main__':
    print("🎯 DAILY REACH-OUT RECOMMENDATIONS")
    print("=" * 50)
    
    recs = generate_daily_recommendations()
    
    for i, r in enumerate(recs, 1):
        print(f"\n{i}. {r['name']}")
        print(f"   Category: {r['category']} | Frequency: {r['frequency']}")
        if r['phone']:
            print(f"   📱 {r['phone']}")
        if r['email']:
            print(f"   📧 {r['email']}")
        if r['organization']:
            print(f"   🏢 {r['organization']}")
        print(f"   💡 {r['suggested_action']}")
    
    print(f"\nSaved to data/contacts/daily-recommendations.json")
