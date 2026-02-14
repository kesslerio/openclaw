#!/usr/bin/env python3
"""Analyze email history to determine contact frequency and categorize contacts."""

import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

def get_email_history(days=90, page_size=500):
    """Fetch email history from Himalaya."""
    # Check if himalaya is available
    check_cmd = 'which himalaya'
    check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

    if check_result.returncode != 0:
        print("Warning: Himalaya email client not found.")
        print("Install with: cargo install himalaya")
        print("Skipping email analysis - using existing contact data only.")
        return []

    cmd = f'himalaya envelope list --page-size {page_size} --output json 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Warning: Could not fetch emails: {result.stderr}")
        print("Skipping email analysis - using existing contact data only.")
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Warning: Error parsing email JSON")
        print("Skipping email analysis - using existing contact data only.")
        return []

def extract_email_contacts(emails):
    """Extract unique contacts from email history with frequency."""
    contact_freq = defaultdict(lambda: {'count': 0, 'last_date': None, 'subjects': []})
    cutoff = datetime.now() - timedelta(days=90)
    
    for email in emails:
        # Get sender info
        sender = email.get('from', {}) or {}
        addr = (sender.get('addr') or '').lower().strip()
        name = (sender.get('name') or '').strip()
        date_str = email.get('date', '')
        subject = email.get('subject', '')
        
        if not addr:
            continue
            
        # Skip automated/system emails
        skip_domains = ['google.com', 'skool.com', 'sprinto.com', 'amazon.com', 
                       'intuit.com', 'chase.com', 'capitalone.com', 'docusign',
                       'noreply', 'no-reply', 'notification']
        if any(skip in addr for skip in skip_domains):
            continue
        
        contact_freq[addr]['count'] += 1
        contact_freq[addr]['name'] = name
        contact_freq[addr]['last_date'] = date_str
        if len(contact_freq[addr]['subjects']) < 3:
            contact_freq[addr]['subjects'].append(subject)
    
    return dict(contact_freq)

def match_contacts(contacts, email_freq):
    """Match email frequency data with contacts."""
    matched = 0
    
    for contact in contacts:
        email = (contact.get('email') or '').lower().strip()
        
        if email and email in email_freq:
            freq_data = email_freq[email]
            contact['contact_count_90d'] = freq_data['count']
            contact['last_contacted'] = freq_data['last_date']
            
            # Categorize by frequency
            if freq_data['count'] >= 10:
                contact['frequency'] = 'hot'
            elif freq_data['count'] >= 3:
                contact['frequency'] = 'warm'
            elif freq_data['count'] >= 1:
                contact['frequency'] = 'cold'
            else:
                contact['frequency'] = 'dormant'
            
            matched += 1
        else:
            contact['frequency'] = 'dormant'
            contact['contact_count_90d'] = 0
    
    return contacts, matched

def categorize_by_domain(contacts):
    """Auto-categorize business vs personal based on email domain."""
    business_indicators = ['copperdigital', 'coppermobile', 'copper', 
                          'healthcare', 'health', 'medical', 'consulting']
    
    for contact in contacts:
        email = (contact.get('email') or '').lower()
        
        # Already categorized
        if contact['category'] != 'unknown':
            continue
        
        # Check email domain
        if '@' in email:
            domain = email.split('@')[1]
            
            # Personal email domains
            if any(d in domain for d in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']):
                contact['category'] = 'personal'
            # Copper team
            elif 'copper' in domain:
                contact['category'] = 'team'
            # Business
            else:
                contact['category'] = 'business'
    
    return contacts

def generate_report(contacts, email_freq):
    """Generate summary report."""
    # Frequency breakdown
    freq_counts = defaultdict(int)
    cat_counts = defaultdict(int)
    
    for c in contacts:
        freq_counts[c['frequency']] += 1
        cat_counts[c['category']] += 1
    
    # Top contacts by frequency
    top_contacts = sorted(
        [c for c in contacts if c['contact_count_90d'] > 0],
        key=lambda x: x['contact_count_90d'],
        reverse=True
    )[:20]
    
    # Contacts needing attention (warm going cold)
    needs_attention = [c for c in contacts if c['frequency'] == 'warm']
    
    return {
        'frequency_breakdown': dict(freq_counts),
        'category_breakdown': dict(cat_counts),
        'top_contacts': [{'name': c['name'], 'count': c['contact_count_90d'], 'email': c['email']} for c in top_contacts],
        'needs_attention_count': len(needs_attention)
    }

if __name__ == '__main__':
    # Determine paths dynamically
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data' / 'contacts'

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run parse-contacts.py first to create the contacts database.")
        exit(1)
    
    # Load contacts
    print("Loading contacts...")
    with open(data_dir / 'contacts.json') as f:
        contacts = json.load(f)
    
    print(f"Loaded {len(contacts)} contacts")
    
    # Get email history
    print("Fetching email history (last 90 days)...")
    emails = get_email_history(days=90, page_size=500)
    print(f"Fetched {len(emails)} emails")
    
    # Extract email contacts with frequency
    print("Analyzing contact frequency...")
    email_freq = extract_email_contacts(emails)
    print(f"Found {len(email_freq)} unique email contacts")
    
    # Match with contacts
    print("Matching with contact database...")
    contacts, matched = match_contacts(contacts, email_freq)
    print(f"Matched {matched} contacts with email history")
    
    # Auto-categorize
    print("Auto-categorizing contacts...")
    contacts = categorize_by_domain(contacts)
    
    # Generate report
    print("Generating report...")
    report = generate_report(contacts, email_freq)
    
    # Save updated contacts
    with open(data_dir / 'contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)
    
    # Save report
    with open(data_dir / 'report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("CONTACT FREQUENCY ANALYSIS")
    print("="*50)
    
    print("\n📊 FREQUENCY BREAKDOWN:")
    for freq, count in report['frequency_breakdown'].items():
        emoji = {'hot': '🔥', 'warm': '🌡️', 'cold': '❄️', 'dormant': '💀', 'unknown': '❓'}.get(freq, '•')
        print(f"  {emoji} {freq.capitalize()}: {count}")
    
    print("\n📁 CATEGORY BREAKDOWN:")
    for cat, count in report['category_breakdown'].items():
        emoji = {'business': '💼', 'personal': '👨‍👩‍👧', 'team': '👥', 'network': '🤝', 'unknown': '❓'}.get(cat, '•')
        print(f"  {emoji} {cat.capitalize()}: {count}")
    
    print("\n🔥 TOP CONTACTS (Last 90 days):")
    for i, c in enumerate(report['top_contacts'][:10], 1):
        print(f"  {i}. {c['name']} - {c['count']} emails")
    
    print(f"\n⚠️ Contacts needing attention: {report['needs_attention_count']}")
