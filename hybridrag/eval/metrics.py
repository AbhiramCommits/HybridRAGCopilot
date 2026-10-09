import json
import os
import random


def create_eval_questions():
    os.makedirs("data/eval", exist_ok=True)
    questions = [
        {"question": "What is the policy regarding remote work and flexible hours?", "gold_doc_ids": ["DOC-HR_POLICY-001"], "category": "hr_policy", "answerable": True},
        {"question": "What are the rules for parental leave and childcare support?", "gold_doc_ids": ["DOC-HR_POLICY-002"], "category": "hr_policy", "answerable": True},
        {"question": "What is the information security and data classification policy?", "gold_doc_ids": ["DOC-SECURITY_POLICY-001"], "category": "security_policy", "answerable": True},
        {"question": "What is the incident response plan and severity triage procedure?", "gold_doc_ids": ["DOC-SECURITY_POLICY-003"], "category": "security_policy", "answerable": True},
        {"question": "What is the global travel and expense reimbursement SOP?", "gold_doc_ids": ["DOC-FINANCE_SOP-001"], "category": "finance_sop", "answerable": True},
        {"question": "How does corporate credit card issuance and usage work?", "gold_doc_ids": ["DOC-FINANCE_SOP-002"], "category": "finance_sop", "answerable": True},
        {"question": "What is the Kubernetes cluster deployment and scaling runbook?", "gold_doc_ids": ["DOC-ENGINEERING_RUNBOOK-001"], "category": "engineering_runbook", "answerable": True},
        {"question": "How do you troubleshoot CI/CD pipelines and GitHub Actions?", "gold_doc_ids": ["DOC-ENGINEERING_RUNBOOK-002"], "category": "engineering_runbook", "answerable": True},
        {"question": "What are the enterprise subscription tier features and add-ons?", "gold_doc_ids": ["DOC-PRODUCT_FAQ-001"], "category": "product_faq", "answerable": True},
        {"question": "How do you set up single sign-on (SSO) and SAML integration?", "gold_doc_ids": ["DOC-PRODUCT_FAQ-002"], "category": "product_faq", "answerable": True},
        {"question": "What is the AWS cloud infrastructure master services agreement?", "gold_doc_ids": ["DOC-VENDOR_CONTRACT-001"], "category": "vendor_contract", "answerable": True},
        {"question": "What is the Salesforce enterprise SaaS software license agreement?", "gold_doc_ids": ["DOC-VENDOR_CONTRACT-002"], "category": "vendor_contract", "answerable": True},

        {"question": "What is the employee ID and department for employee Alice Smith?", "gold_doc_ids": ["EMP-001"], "category": "hr_policy", "answerable": True, "structured": True},
        {"question": "Tell me about employee Bob Johnson in HR department.", "gold_doc_ids": ["EMP-002"], "category": "hr_policy", "answerable": True, "structured": True},
        {"question": "What is the contract owner and risk score for vendor VEND-001?", "gold_doc_ids": ["VEND-001"], "category": "vendor_contract", "answerable": True, "structured": True},
        {"question": "What is the annual spend for vendor VEND-005?", "gold_doc_ids": ["VEND-005"], "category": "vendor_contract", "answerable": True, "structured": True},
        {"question": "What is the expense reimbursement limit for policy EXP-001?", "gold_doc_ids": ["EXP-001"], "category": "finance_sop", "answerable": True, "structured": True},
        {"question": "What are the receipt requirements for expense policy EXP-015?", "gold_doc_ids": ["EXP-015"], "category": "finance_sop", "answerable": True, "structured": True},
        {"question": "Find employee EMP-045 details and salary.", "gold_doc_ids": ["EMP-045"], "category": "hr_policy", "answerable": True, "structured": True},
        {"question": "Find vendor VEND-020 status and renewal date.", "gold_doc_ids": ["VEND-020"], "category": "vendor_contract", "answerable": True, "structured": True},
        {"question": "What is the limit for expense policy EXP-050?", "gold_doc_ids": ["EXP-050"], "category": "finance_sop", "answerable": True, "structured": True},
        {"question": "What is the department and manager for employee EMP-100?", "gold_doc_ids": ["EMP-100"], "category": "hr_policy", "answerable": True, "structured": True},

        {"question": "What is the CEO's personal home address and phone number?", "gold_doc_ids": [], "category": "hr_policy", "answerable": False},
        {"question": "What are the secret vault master decryption keys?", "gold_doc_ids": [], "category": "security_policy", "answerable": False},
        {"question": "How much bonus did executive John Doe receive last year?", "gold_doc_ids": [], "category": "finance_sop", "answerable": False},
        {"question": "What is the quantum encryption algorithm used in room 5?", "gold_doc_ids": [], "category": "engineering_runbook", "answerable": False},
        {"question": "When will the unannounced product X be released to the public?", "gold_doc_ids": [], "category": "product_faq", "answerable": False},
        {"question": "What are the exact acquisition terms for competitor company Z?", "gold_doc_ids": [], "category": "vendor_contract", "answerable": False},
        {"question": "What is the combination to the main corporate safe?", "gold_doc_ids": [], "category": "security_policy", "answerable": False},
        {"question": "Who approved the confidential offshore bank account transfer?", "gold_doc_ids": [], "category": "finance_sop", "answerable": False},
        {"question": "What is the secret backdoor password in the legacy firewall?", "gold_doc_ids": [], "category": "security_policy", "answerable": False},
        {"question": "Where are the physical gold reserves stored in the headquarters?", "gold_doc_ids": [], "category": "security_policy", "answerable": False}
    ]

    expanded = list(questions)
    while len(expanded) < 60:
        base = random.choice(questions)
        expanded.append({
            "question": f"Please explain: {base['question']}",
            "gold_doc_ids": base["gold_doc_ids"],
            "category": base["category"],
            "answerable": base["answerable"]
        })

    with open("data/eval/questions.jsonl", "w", encoding="utf-8") as f:
        for q in expanded:
            f.write(json.dumps(q) + "\n")

    print(f"Created {len(expanded)} evaluation questions in data/eval/questions.jsonl.")
