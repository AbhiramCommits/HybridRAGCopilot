import os

import yaml

CATEGORIES = {
    "hr_policy": [
        ("Remote Work and Flexible Hours Policy", "HR", "PeopleOps", "2025-01-15", "Jane Doe", "internal"),
        ("Parental Leave and Childcare Support", "HR", "Benefits Team", "2024-11-01", "Sarah Connor", "internal"),
        ("Annual Performance Review and Promotion Guidelines", "HR", "Talent Management", "2024-06-10", "Michael Scott", "internal"),
        ("Employee Wellness and Mental Health Support", "HR", "PeopleOps", "2025-02-01", "Jane Doe", "public"),
        ("Code of Conduct and Workplace Ethics", "HR", "Legal & HR", "2023-01-01", "Alice Smith", "public"),
        ("Professional Development and Tuition Reimbursement", "HR", "Learning & Dev", "2024-03-15", "Bob Ross", "internal"),
        ("Internal Mobility and Transfer Guidelines", "HR", "Talent Acquisition", "2024-08-20", "Charlie Brown", "internal"),
        ("Grievance Resolution and Anti-Harassment Policy", "HR", "Legal", "2023-05-12", "Alice Smith", "confidential"),
        ("Employee Onboarding and Offboarding Standard", "HR", "PeopleOps", "2024-01-10", "Jane Doe", "internal"),
        ("Relocation Assistance and Expatriate Policy", "HR", "Global Mobility", "2024-09-01", "David Miller", "confidential"),
        ("Overtime and Compensatory Time Policy", "HR", "Payroll", "2024-04-05", "Emma Watson", "internal"),
        ("Temporary Disability and Leave of Absence", "HR", "Benefits Team", "2024-07-11", "Sarah Connor", "internal"),
        ("Employee Recognition and Bonus Structure", "HR", "Compensation", "2024-10-01", "Frank Castle", "confidential"),
        ("Substance Abuse and Drug-Free Workplace", "HR", "Legal & HR", "2023-02-15", "Alice Smith", "internal"),
        ("Volunteer Day and Community Engagement Policy", "HR", "CSR", "2024-05-20", "Grace Hopper", "public"),
        ("Executive Compensation and Retention Framework", "HR", "Compensation", "2024-12-01", "Frank Castle", "restricted"),
        ("Part-Time and Job-Sharing Guidelines", "HR", "PeopleOps", "2024-03-22", "Jane Doe", "internal"),
        ("Employee Safety and Ergonomic Assessment Standards", "HR", "Facilities", "2024-06-15", "Hank Pym", "internal"),
        ("Whistleblower Protection and Reporting Protocol", "HR", "Legal", "2023-04-10", "Alice Smith", "confidential"),
        ("Internship and Fellowship Program Framework", "HR", "University Recruiting", "2024-11-15", "Charlie Brown", "public"),
    ],
    "security_policy": [
        ("Information Security and Data Classification Policy", "Security", "SecOps", "2025-01-10", "Null Byte", "confidential"),
        ("Password Complexity and Multi-Factor Authentication Standard", "Security", "Identity Team", "2024-09-12", "Cipher Smith", "internal"),
        ("Incident Response Plan and Severity Triage", "Security", "SOC", "2024-08-01", "Root User", "restricted"),
        ("Vendor Security Assessment and Third-Party Risk Management", "Security", "GRC", "2024-05-19", "Firewall Phil", "confidential"),
        ("Vulnerability Disclosure and Bug Bounty Program", "Security", "AppSec", "2024-03-30", "Hacker Harry", "public"),
        ("Access Control and Principle of Least Privilege", "Security", "Identity Team", "2024-02-14", "Cipher Smith", "internal"),
        ("Mobile Device Management and BYOD Policy", "Security", "Endpoint Sec", "2024-07-08", "Shield Sarah", "internal"),
        ("Data Loss Prevention and Cloud Storage Security", "Security", "CloudSec", "2024-10-05", "Null Byte", "confidential"),
        ("Secure Software Development Lifecycle (SSDLC)", "Security", "AppSec", "2024-04-18", "Hacker Harry", "internal"),
        ("Network Perimeter Firewall and VPN Standard", "Security", "NetSec", "2024-01-25", "Firewall Phil", "internal"),
        ("Phishing Simulation and Security Awareness Training", "Security", "SecOps", "2024-06-01", "Root User", "public"),
        ("Cryptographic Key Management Policy", "Security", "Crypto Team", "2024-08-15", "Cipher Smith", "restricted"),
        ("Endpoint Detection and Response (EDR) Deployment Standard", "Security", "Endpoint Sec", "2024-09-20", "Shield Sarah", "internal"),
        ("Physical Security and Data Center Access Control", "Security", "Facilities & Sec", "2023-11-10", "Guard Gary", "confidential"),
        ("API Security and OAuth Token Management", "Security", "AppSec", "2024-10-12", "Hacker Harry", "internal"),
        ("Secure File Transfer and Data Sanitization Standard", "Security", "CloudSec", "2024-02-28", "Null Byte", "internal"),
        ("Business Continuity and Disaster Recovery Plan", "Security", "Resilience Team", "2024-04-01", "Root User", "restricted"),
        ("Privileged Access Management (PAM) Protocol", "Security", "Identity Team", "2024-07-19", "Cipher Smith", "restricted"),
        ("Server Hardening and Baseline Configuration Standard", "Security", "Infrastructure", "2024-03-05", "Firewall Phil", "internal"),
        ("External Audit Compliance and SOC2 Type II Framework", "Security", "GRC", "2024-11-30", "GRC Lead", "confidential"),
    ],
    "finance_sop": [
        ("Global Travel and Expense Reimbursement SOP", "Finance", "Accounting", "2025-01-05", "Penny Cents", "internal"),
        ("Corporate Credit Card Issuance and Usage Policy", "Finance", "Treasury", "2024-10-15", "Richie Rich", "internal"),
        ("Procurement and Vendor Purchase Order Workflow", "Finance", "Procurement", "2024-08-10", "Buyer Bill", "internal"),
        ("Annual Budget Planning and Capital Expenditure Approval", "Finance", "FP&A", "2024-07-01", "CFO Office", "confidential"),
        ("Client Entertainment and Gift Reporting Guidelines", "Finance", "Compliance", "2024-03-12", "Penny Cents", "internal"),
        ("Invoice Processing and Accounts Payable Standard", "Finance", "AP Team", "2024-02-20", "Ledger Larry", "internal"),
        ("Revenue Recognition and Contract Billing SOP", "Finance", "Revenue Ops", "2024-05-08", "CFO Office", "restricted"),
        ("Fixed Asset Management and Inventory Audit", "Finance", "Accounting", "2024-06-18", "Asset Ann", "internal"),
        ("Tax Compliance and Transfer Pricing Policy", "Finance", "Tax Team", "2024-01-20", "Tax Tom", "restricted"),
        ("Petty Cash Management and Reconciliation Standard", "Finance", "Accounting", "2024-04-15", "Penny Cents", "internal"),
        ("Currency Hedging and Foreign Exchange Risk Management", "Finance", "Treasury", "2024-09-05", "Richie Rich", "restricted"),
        ("Stock Option Exercise and Equity Administration SOP", "Finance", "Equity Ops", "2024-11-10", "Shareholder Sam", "confidential"),
        ("Charitable Donations and Corporate Sponsorship Approval", "Finance", "CSR", "2024-02-10", "Penny Cents", "public"),
        ("Accounts Receivable Collection and Credit Risk Policy", "Finance", "AR Team", "2024-07-25", "Credit Chris", "internal"),
        ("Month-End Close and Financial Reporting Checklist", "Finance", "Accounting", "2024-03-01", "Ledger Larry", "internal"),
        ("Mergers and Acquisitions Financial Due Diligence SOP", "Finance", "M&A Team", "2024-12-05", "CFO Office", "restricted"),
        ("Internal Audit Charter and Control Testing Procedure", "Finance", "Internal Audit", "2024-08-22", "Auditor Amy", "confidential"),
        ("Subsidiary Intercompany Billing and Settlement Policy", "Finance", "Accounting", "2024-04-30", "Tax Tom", "restricted"),
        ("Emergency Funds and Liquidity Reserves Management", "Finance", "Treasury", "2024-01-15", "Richie Rich", "restricted"),
        ("Royalty and Intellectual Property Revenue Accounting", "Finance", "Revenue Ops", "2024-10-20", "Ledger Larry", "confidential"),
    ],
    "engineering_runbook": [
        ("Kubernetes Cluster Deployment and Scaling Runbook", "Engineering", "Platform Ops", "2025-01-20", "Kube King", "internal"),
        ("CI/CD Pipeline Troubleshooting and GitHub Actions Maintenance", "Engineering", "DevEx", "2024-10-10", "Pipeline Pete", "internal"),
        ("Database Migration and PostgreSQL Failover Runbook", "Engineering", "DBA Team", "2024-08-14", "Postgres Paul", "restricted"),
        ("Microservice Observability, Tracing, and Alerting Playbook", "Engineering", "SRE Team", "2024-07-05", "Monitor Mary", "internal"),
        ("Zero-Downtime Blue-Green Deployment Runbook", "Engineering", "Platform Ops", "2024-06-20", "Kube King", "internal"),
        ("Kafka Event Streaming Architecture and Consumer Lag Resolution", "Engineering", "Data Platform", "2024-05-11", "Stream Sam", "internal"),
        ("Production Debugging and Core Dump Analysis Guide", "Engineering", "Core Eng", "2024-03-19", "Debugger Dave", "confidential"),
        ("Redis Cache Invalidation and Memory Exhaustion Mitigation", "Engineering", "Cache Team", "2024-02-11", "Cache Carl", "internal"),
        ("Load Balancer Configuration and SSL Certificate Renewal", "Engineering", "Network Eng", "2024-01-30", "Cert Chris", "internal"),
        ("Multi-Region Failover and Route53 DNS Recovery Runbook", "Engineering", "SRE Team", "2024-09-15", "Monitor Mary", "restricted"),
        ("Container Security Scanning and Image Patching Protocol", "Engineering", "AppSec Eng", "2024-04-22", "Secure Steve", "internal"),
        ("Elasticsearch Cluster Reindexing and Shard Optimization", "Engineering", "Search Team", "2024-08-05", "Search Sue", "internal"),
        ("GraphQL Gateway Federation and Rate Limiting Runbook", "Engineering", "API Team", "2024-11-01", "Gateway Gary", "internal"),
        ("Prometheus Metrics Exporter Development and Alert Rules", "Engineering", "SRE Team", "2024-02-25", "Monitor Mary", "internal"),
        ("Python Dependency Management and Poetry Upgrade Runbook", "Engineering", "DevEx", "2024-06-10", "Pipeline Pete", "internal"),
        ("GPU Node Provisioning for Machine Learning Workloads", "Engineering", "AI Platform", "2024-12-10", "Tensor Tim", "internal"),
        ("Secret Rotation and HashiCorp Vault Integration Runbook", "Engineering", "Security Eng", "2024-07-30", "Vault Vicki", "restricted"),
        ("Distributed Tracing with OpenTelemetry Best Practices", "Engineering", "SRE Team", "2024-03-15", "Monitor Mary", "internal"),
        ("Legacy Monolith Strangler Fig Migration Playbook", "Engineering", "Architecture", "2024-10-25", "Arch Andy", "confidential"),
        ("WebSocket Connection Storms and Scaling Strategies", "Engineering", "Realtime Team", "2024-05-30", "Socket Stan", "internal"),
    ],
    "product_faq": [
        ("Enterprise Subscription Tier Features and Add-Ons FAQ", "Product", "Product Management", "2025-01-12", "PM Pam", "public"),
        ("Single Sign-On (SSO) Setup and SAML Integration FAQ", "Product", "Integrations", "2024-11-20", "Sammy SAML", "public"),
        ("API Rate Limits, Quotas, and Versioning Policy FAQ", "Product", "API Platform", "2024-09-08", "Rate Rita", "public"),
        ("Data Residency, Regional Hosting, and GDPR Compliance FAQ", "Product", "Privacy Team", "2024-08-18", "GDPR Greg", "public"),
        ("User Role Permissions and Granular Access Control FAQ", "Product", "UX Design", "2024-06-25", "Role Ron", "public"),
        ("Custom Branding, White-Labeling, and Domain Setup FAQ", "Product", "Growth", "2024-05-14", "Brand Brenda", "public"),
        ("Billing Cycles, Invoicing, and Payment Methods FAQ", "Product", "Billing Ops", "2024-04-02", "Bill Barry", "public"),
        ("SLA Guarantees, Uptime Metrics, and Support Tiers FAQ", "Product", "Customer Success", "2024-03-20", "Support Sue", "public"),
        ("Data Export, Backup Recovery, and Account Deletion FAQ", "Product", "Data Team", "2024-07-12", "Backup Bob", "public"),
        ("Mobile App Companion Features and Push Notifications FAQ", "Product", "Mobile Team", "2024-10-02", "App Andy", "public"),
        ("Webhook Integration and Event Payload Delivery FAQ", "Product", "Integrations", "2024-01-18", "Webhook Wendy", "public"),
        ("Sandbox Environment and Staging Instance Provisioning FAQ", "Product", "QA Team", "2024-02-15", "Sandbox Stan", "public"),
        ("Audit Logs and Compliance Reporting Features FAQ", "Product", "Enterprise PM", "2024-09-22", "Audit Audrey", "public"),
        ("Localization, Language Support, and Currency Display FAQ", "Product", "Globalization", "2024-06-05", "Local Larry", "public"),
        ("AI Copilot Capabilities and Token Usage Limits FAQ", "Product", "AI Product", "2024-12-01", "AI Arthur", "public"),
        ("Third-Party Marketplace App Installation and Security FAQ", "Product", "Ecosystem", "2024-04-20", "Market Mark", "public"),
        ("Customer Feedback Portal and Feature Request Roadmap FAQ", "Product", "Product Ops", "2024-03-10", "Roadmap Ray", "public"),
        ("On-Premises Air-Gapped Deployment Architecture FAQ", "Product", "Enterprise Solutions", "2024-11-12", "Airgap Alice", "confidential"),
        ("Embedded Analytics and BI Dashboard Embedding FAQ", "Product", "Analytics", "2024-05-25", "Chart Charlie", "public"),
        ("Migration Wizard and Bulk Data Import FAQ", "Product", "Customer Onboarding", "2024-08-30", "Migrate Mike", "public"),
    ],
    "vendor_contract": [
        ("Cloud Infrastructure Master Services Agreement (AWS)", "Procurement", "Legal Counsel", "2025-01-01", "Legal Lead", "confidential"),
        ("Enterprise SaaS Software License Agreement (Salesforce)", "Procurement", "IT Procurement", "2024-10-12", "Buyer Bill", "confidential"),
        ("Cybersecurity Penetration Testing and Advisory Contract", "Security", "SecOps", "2024-09-01", "Firewall Phil", "confidential"),
        ("Global Payroll and Employer of Record Services Agreement", "HR", "Global HR", "2024-08-15", "Jane Doe", "confidential"),
        ("Data Center Colocation and Managed Hosting Contract", "Engineering", "Infrastructure", "2024-07-01", "Kube King", "restricted"),
        ("Customer Support Outsourcing Master Agreement", "Product", "Support Ops", "2024-06-10", "Support Sue", "confidential"),
        ("Legal Counsel and Regulatory Advisory Retainer", "Legal", "Executive", "2024-01-10", "Alice Smith", "restricted"),
        ("Corporate Health Insurance and Benefits Broker Contract", "HR", "Benefits Team", "2024-05-05", "Sarah Connor", "confidential"),
        ("Marketing Agency Retainer and Brand Strategy Contract", "Marketing", "CMO Office", "2024-04-20", "Market Mark", "internal"),
        ("Logistics and Courier Services Master Agreement", "Operations", "Facilities", "2024-03-15", "Guard Gary", "internal"),
        ("Enterprise ERP Software Maintenance and Support Contract", "Finance", "IT Finance", "2024-02-10", "Ledger Larry", "confidential"),
        ("Translation and Localization Services Agreement", "Product", "Globalization", "2024-06-22", "Local Larry", "internal"),
        ("Background Check and Screening Services Contract", "HR", "Talent Acquisition", "2024-01-25", "Charlie Brown", "confidential"),
        ("Office Leasing and Facilities Management Agreement", "Operations", "Real Estate", "2023-12-01", "Facility Frank", "restricted"),
        ("Printers and Copier Fleet Managed Services Contract", "Operations", "IT Operations", "2024-03-01", "Print Pat", "internal"),
        ("Corporate Travel Booking and Management Agreement", "Finance", "Travel Ops", "2024-07-15", "Penny Cents", "internal"),
        ("Diversity and Inclusion Consulting Retainer Contract", "HR", "CSR", "2024-04-10", "Grace Hopper", "internal"),
        ("Executive Search and Recruitment Agency Master Agreement", "HR", "Talent Acquisition", "2024-09-10", "Michael Scott", "confidential"),
        ("Network Transit and Fiber Optic Connectivity Contract", "Engineering", "Network Eng", "2024-02-28", "Cert Chris", "restricted"),
        ("Insurances (D&O, General Liability, Cyber) Master Policy", "Finance", "Risk Management", "2024-11-01", "Risk Rita", "restricted"),
    ]
}

def generate_document_text(category, title, owner, effective_date):
    sections = [
        f"# {title}",
        f"**Effective Date:** {effective_date} | **Owner:** {owner} | **Category:** {category}",
        "\n## 1. Overview and Purpose",
        f"This document defines the official enterprise policy and operating guidelines for {title.lower()}. Compliance is mandatory across all departments. The primary objective is to maintain operational excellence, regulatory compliance, and security standards.",
        "\n## 2. Scope and Applicability",
        "This policy applies to all full-time employees, contractors, and third-party vendors associated with the company. Exceptions must be approved in writing by the department head and legal counsel. Thresholds and limits defined herein supersede all prior versions.",
        "\n## 3. Core Guidelines and Procedures",
        "- **Policy Threshold:** The standard operating limit is set at $5,000 for standard transactions, with a maximum allowable cap of $25,000 under exceptional executive approval.",
        f"- **Timeline and SLA:** All requests must be submitted within 14 business days of occurrence. Review cycles are completed within 5 business days by {owner}.",
        "- **Compliance & Penalty:** Non-compliance results in formal administrative review, potential revocation of privileges, and possible disciplinary action up to termination.",
        "\n## 4. Exceptions and Escalation",
        f"For urgent escalations or special accommodations, contact {owner} directly via internal channels. Escalation tickets are triaged within 24 hours. Version identifier: v2.4-RELEASE.",
        "\n## 5. Document Control and Revision History",
        f"Reviewed quarterly by the compliance committee. Last audit conducted on {effective_date}. Next scheduled review is exactly 365 days from issuance."
    ]
    return "\n\n".join(sections)

def create_corpus():
    os.makedirs("data/corpus", exist_ok=True)
    count = 0
    for cat, docs in CATEGORIES.items():
        for title, dept, subdept, eff_date, owner, sensitivity in docs:
            doc_id = f"DOC-{cat.upper()}-{count+1:03d}"
            front_matter = {
                "doc_id": doc_id,
                "title": title,
                "category": cat,
                "department": dept,
                "effective_date": eff_date,
                "owner": owner,
                "sensitivity": sensitivity
            }
            body = generate_document_text(cat, title, owner, eff_date)
            content = f"---\n{yaml.dump(front_matter)}---\n\n{body}"
            file_path = os.path.join("data/corpus", f"{doc_id}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            count += 1
    print(f"Generated {count} unstructured documents across 6 categories.")

if __name__ == "__main__":
    create_corpus()
