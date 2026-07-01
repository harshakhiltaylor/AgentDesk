"""
extended_mock_data.py
---------------------
Bigger dataset — 20 customers across 5 industries, 3 plans.
Adds to the existing mock_data.py without replacing it.
All tools still read from mock_data.py — this file extends it.
"""

# ─────────────────────────────────────────────────────────────
# EXTENDED CUSTOMERS  (15 new, on top of existing 5)
# ─────────────────────────────────────────────────────────────
EXTENDED_CUSTOMERS = {

    # ── STARTER PLAN ─────────────────────────────────────────
    "CUST-006": {
        "customer_id": "CUST-006", "name": "Frank Nguyen", "email": "frank@designstudio.io",
        "company": "DesignStudio", "plan": "starter", "seats": 3, "seats_used": 2,
        "account_status": "active", "contract_id": "CONTRACT-006", "created_at": "2024-02-10",
        "features_enabled": ["basic_dashboard", "email_support", "dark_mode"], "mrr": 49.0,
        "industry": "Design",
    },
    "CUST-007": {
        "customer_id": "CUST-007", "name": "Grace Obi", "email": "grace@legaledge.com",
        "company": "LegalEdge LLP", "plan": "starter", "seats": 8, "seats_used": 8,
        "account_status": "active", "contract_id": "CONTRACT-007", "created_at": "2023-11-05",
        "features_enabled": ["basic_dashboard", "email_support"], "mrr": 49.0,
        "industry": "Legal",
    },
    "CUST-008": {
        "customer_id": "CUST-008", "name": "Henry Park", "email": "henry@retailco.com",
        "company": "RetailCo", "plan": "starter", "seats": 10, "seats_used": 12,  # Overage
        "account_status": "active", "contract_id": "CONTRACT-008", "created_at": "2024-01-01",
        "features_enabled": ["basic_dashboard", "email_support", "dark_mode"], "mrr": 49.0,
        "industry": "Retail",
    },
    "CUST-009": {
        "customer_id": "CUST-009", "name": "Iris Kowalski", "email": "iris@nonprofit.org",
        "company": "GreenEarth NGO", "plan": "starter", "seats": 5, "seats_used": 3,
        "account_status": "active", "contract_id": "CONTRACT-009", "created_at": "2023-08-20",
        "features_enabled": ["basic_dashboard", "email_support"], "mrr": 49.0,
        "industry": "Non-Profit",
    },
    "CUST-010": {
        "customer_id": "CUST-010", "name": "James Wu", "email": "james@edulearn.edu",
        "company": "EduLearn Academy", "plan": "starter", "seats": 6, "seats_used": 6,
        "account_status": "suspended",  # Suspended — interesting for escalation
        "contract_id": "CONTRACT-010", "created_at": "2022-05-15",
        "features_enabled": ["basic_dashboard"], "mrr": 49.0,
        "industry": "Education",
    },

    # ── PRO PLAN ──────────────────────────────────────────────
    "CUST-011": {
        "customer_id": "CUST-011", "name": "Karen Petrov", "email": "karen@healthtech.io",
        "company": "HealthTech Inc.", "plan": "pro", "seats": 25, "seats_used": 20,
        "account_status": "active", "contract_id": "CONTRACT-011", "created_at": "2023-03-12",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "mrr": 299.0, "industry": "Healthcare",
    },
    "CUST-012": {
        "customer_id": "CUST-012", "name": "Leo Santos", "email": "leo@fintech.io",
        "company": "FinTech Solutions", "plan": "pro", "seats": 40, "seats_used": 38,
        "account_status": "active", "contract_id": "CONTRACT-012", "created_at": "2022-09-01",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "mrr": 299.0, "industry": "Finance",
    },
    "CUST-013": {
        "customer_id": "CUST-013", "name": "Maya Sharma", "email": "maya@ecommerce.co",
        "company": "ShopEasy", "plan": "pro", "seats": 15, "seats_used": 15,
        "account_status": "active", "contract_id": "CONTRACT-013", "created_at": "2023-06-30",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","webhooks","dark_mode"],
        "mrr": 299.0, "industry": "E-Commerce",
    },
    "CUST-014": {
        "customer_id": "CUST-014", "name": "Nate Brooks", "email": "nate@mediaco.com",
        "company": "MediaCo", "plan": "pro", "seats": 30, "seats_used": 22,
        "account_status": "active", "contract_id": "CONTRACT-014", "created_at": "2021-12-20",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode"],
        "mrr": 299.0, "industry": "Media",
    },
    "CUST-015": {
        "customer_id": "CUST-015", "name": "Olivia Chen", "email": "olivia@logisticshub.com",
        "company": "LogisticsHub", "plan": "pro", "seats": 50, "seats_used": 49,
        "account_status": "active", "contract_id": "CONTRACT-015", "created_at": "2022-03-08",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","webhooks","dark_mode"],
        "mrr": 299.0, "industry": "Logistics",
    },

    # ── ENTERPRISE PLAN ───────────────────────────────────────
    "CUST-016": {
        "customer_id": "CUST-016", "name": "Paul Reeves", "email": "paul@globalbank.com",
        "company": "GlobalBank Corp", "plan": "enterprise", "seats": 500, "seats_used": 487,
        "account_status": "active", "contract_id": "CONTRACT-016", "created_at": "2020-01-15",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 4999.0, "industry": "Banking",
    },
    "CUST-017": {
        "customer_id": "CUST-017", "name": "Quinn Miles", "email": "quinn@pharmacorp.com",
        "company": "PharmaCorp", "plan": "enterprise", "seats": 200, "seats_used": 198,
        "account_status": "active", "contract_id": "CONTRACT-017", "created_at": "2019-07-22",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 2999.0, "industry": "Pharma",
    },
    "CUST-018": {
        "customer_id": "CUST-018", "name": "Rosa Delgado", "email": "rosa@govtech.gov",
        "company": "GovTech Agency", "plan": "enterprise", "seats": 300, "seats_used": 276,
        "account_status": "active", "contract_id": "CONTRACT-018", "created_at": "2021-09-01",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 3499.0, "industry": "Government",
    },
    "CUST-019": {
        "customer_id": "CUST-019", "name": "Sam Thornton", "email": "sam@manufact.com",
        "company": "PrecisionMFG", "plan": "enterprise", "seats": 150, "seats_used": 150,  # Full
        "account_status": "active", "contract_id": "CONTRACT-019", "created_at": "2020-11-03",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 2499.0, "industry": "Manufacturing",
    },
    "CUST-020": {
        "customer_id": "CUST-020", "name": "Tina Walsh", "email": "tina@insureco.com",
        "company": "InsureCo", "plan": "enterprise", "seats": 250, "seats_used": 201,
        "account_status": "active", "contract_id": "CONTRACT-020", "created_at": "2018-04-10",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 3999.0, "industry": "Insurance",
    },
}

# ─────────────────────────────────────────────────────────────
# EXTENDED BILLING HISTORY
# ─────────────────────────────────────────────────────────────
EXTENDED_BILLING = {
    "CUST-006": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-6001"}],
    "CUST-007": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-7001"},
                 {"date": "2024-02-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-7000"}],
    "CUST-008": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-8001"}],
    "CUST-009": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-9001"}],
    "CUST-010": [{"date": "2024-03-01", "amount": 49.0,   "status": "failed", "invoice": "INV-10001"},
                 {"date": "2024-02-01", "amount": 49.0,   "status": "failed", "invoice": "INV-10000"}],
    "CUST-011": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-11001"},
                 {"date": "2024-02-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-11000"}],
    "CUST-012": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-12001"},
                 {"date": "2024-02-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-12000"},
                 {"date": "2024-01-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-11999"}],
    "CUST-013": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-13001"}],
    "CUST-014": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-14001"}],
    "CUST-015": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-15001"}],
    "CUST-016": [{"date": "2024-03-01", "amount": 4999.0, "status": "paid",   "invoice": "INV-16001"},
                 {"date": "2024-02-01", "amount": 4999.0, "status": "paid",   "invoice": "INV-16000"}],
    "CUST-017": [{"date": "2024-03-01", "amount": 2999.0, "status": "paid",   "invoice": "INV-17001"}],
    "CUST-018": [{"date": "2024-03-01", "amount": 3499.0, "status": "paid",   "invoice": "INV-18001"}],
    "CUST-019": [{"date": "2024-03-01", "amount": 2499.0, "status": "paid",   "invoice": "INV-19001"},
                 {"date": "2024-02-01", "amount": 2499.0, "status": "paid",   "invoice": "INV-19000"}],
    "CUST-020": [{"date": "2024-03-01", "amount": 3999.0, "status": "paid",   "invoice": "INV-20001"}],
}

# ─────────────────────────────────────────────────────────────
# EXTENDED CONTRACTS
# ─────────────────────────────────────────────────────────────
EXTENDED_CONTRACTS = {
    "CONTRACT-006": {
        "contract_id": "CONTRACT-006", "customer_id": "CUST-006", "plan": "starter",
        "start_date": "2024-02-10", "end_date": "2026-02-10", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support", "dark_mode"],
        "seats": 3, "special_terms": None,
    },
    "CONTRACT-007": {
        "contract_id": "CONTRACT-007", "customer_id": "CUST-007", "plan": "starter",
        "start_date": "2023-11-05", "end_date": "2025-11-05", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support"],
        "seats": 8, "special_terms": "Legal sector discount applied — 10% off renewal.",
    },
    "CONTRACT-008": {
        "contract_id": "CONTRACT-008", "customer_id": "CUST-008", "plan": "starter",
        "start_date": "2024-01-01", "end_date": "2026-01-01", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support", "dark_mode"],
        "seats": 10, "special_terms": None,
    },
    "CONTRACT-009": {
        "contract_id": "CONTRACT-009", "customer_id": "CUST-009", "plan": "starter",
        "start_date": "2023-08-20", "end_date": "2025-08-20", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support"],
        "seats": 5, "special_terms": "NGO pricing — 20% nonprofit discount.",
    },
    "CONTRACT-010": {
        "contract_id": "CONTRACT-010", "customer_id": "CUST-010", "plan": "starter",
        "start_date": "2022-05-15", "end_date": "2025-05-15", "sla_response_hours": 72,
        "included_features": ["basic_dashboard"],
        "seats": 6, "special_terms": "Account suspended: 2 consecutive failed payments.",
    },
    "CONTRACT-011": {
        "contract_id": "CONTRACT-011", "customer_id": "CUST-011", "plan": "pro",
        "start_date": "2023-03-12", "end_date": "2026-03-12", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "seats": 25, "special_terms": "Healthcare compliance addendum attached.",
    },
    "CONTRACT-012": {
        "contract_id": "CONTRACT-012", "customer_id": "CUST-012", "plan": "pro",
        "start_date": "2022-09-01", "end_date": "2025-09-01", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "seats": 40, "special_terms": "Financial data processing addendum. SOC2 compliance required.",
    },
    "CONTRACT-013": {
        "contract_id": "CONTRACT-013", "customer_id": "CUST-013", "plan": "pro",
        "start_date": "2023-06-30", "end_date": "2025-06-30", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","webhooks","dark_mode"],
        "seats": 15, "special_terms": None,
    },
    "CONTRACT-014": {
        "contract_id": "CONTRACT-014", "customer_id": "CUST-014", "plan": "pro",
        "start_date": "2021-12-20", "end_date": "2024-12-20", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode"],
        "seats": 30, "special_terms": "Contract up for renewal Dec 2024.",
    },
    "CONTRACT-015": {
        "contract_id": "CONTRACT-015", "customer_id": "CUST-015", "plan": "pro",
        "start_date": "2022-03-08", "end_date": "2025-03-08", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","webhooks","dark_mode"],
        "seats": 50, "special_terms": None,
    },
    "CONTRACT-016": {
        "contract_id": "CONTRACT-016", "customer_id": "CUST-016", "plan": "enterprise",
        "start_date": "2020-01-15", "end_date": "2027-01-15", "sla_response_hours": 2,  # 2-hour SLA!
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 500, "special_terms": "Premium SLA: 2-hour response. Violation = 15% MRR credit/day. Dedicated TAM assigned.",
        "sla_violation_penalty": "15% MRR per day",
    },
    "CONTRACT-017": {
        "contract_id": "CONTRACT-017", "customer_id": "CUST-017", "plan": "enterprise",
        "start_date": "2019-07-22", "end_date": "2026-07-22", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 200, "special_terms": "HIPAA BAA signed. PHI data handling restrictions apply.",
        "sla_violation_penalty": "10% MRR per day",
    },
    "CONTRACT-018": {
        "contract_id": "CONTRACT-018", "customer_id": "CUST-018", "plan": "enterprise",
        "start_date": "2021-09-01", "end_date": "2026-09-01", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 300, "special_terms": "Government FedRAMP compliance required. No data outside US region.",
    },
    "CONTRACT-019": {
        "contract_id": "CONTRACT-019", "customer_id": "CUST-019", "plan": "enterprise",
        "start_date": "2020-11-03", "end_date": "2025-11-03", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 150, "special_terms": "Manufacturing OT/IT integration support included.",
        "sla_violation_penalty": "10% MRR per day",
    },
    "CONTRACT-020": {
        "contract_id": "CONTRACT-020", "customer_id": "CUST-020", "plan": "enterprise",
        "start_date": "2018-04-10", "end_date": "2026-04-10", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 250, "special_terms": "Insurance regulatory compliance addendum. Audit log retention 7 years.",
        "sla_violation_penalty": "10% MRR per day",
    },
}

# ─────────────────────────────────────────────────────────────
# INDUSTRY-SPECIFIC SUPPORT TICKETS
# ─────────────────────────────────────────────────────────────
EXTENDED_TICKETS = {
    "TICKET-1001": {
        "ticket_id": "TICKET-1001", "customer_id": "CUST-016", "contract_id": "CONTRACT-016",
        "created_at": "2024-03-10T08:00:00", "issue": "SSO login broken for all 500 users — production down",
        "priority": "critical", "status": "open", "last_response_at": None,
        "sla_hours": 2, "sla_breached": True,
    },
    "TICKET-1002": {
        "ticket_id": "TICKET-1002", "customer_id": "CUST-012", "contract_id": "CONTRACT-012",
        "created_at": "2024-03-08T14:00:00", "issue": "API returning 401 errors — trading system affected",
        "priority": "high", "status": "open", "last_response_at": "2024-03-09T10:00:00",
        "sla_hours": 24, "sla_breached": True,
    },
    "TICKET-1003": {
        "ticket_id": "TICKET-1003", "customer_id": "CUST-017", "contract_id": "CONTRACT-017",
        "created_at": "2024-03-11T09:00:00", "issue": "Patient data analytics dashboard not loading",
        "priority": "high", "status": "open", "last_response_at": None,
        "sla_hours": 4, "sla_breached": True,
    },
}


# ─────────────────────────────────────────────────────────────
# EXTRA 5 CUSTOMERS (CUST-021 to CUST-025) — edge cases
# ─────────────────────────────────────────────────────────────
EXTRA_CUSTOMERS = {
    "CUST-021": {
        "customer_id": "CUST-021", "name": "Uma Patel", "email": "uma@startupx.io",
        "company": "StartupX", "plan": "starter", "seats": 2, "seats_used": 2,
        "account_status": "active", "contract_id": "CONTRACT-021", "created_at": "2024-03-01",
        "features_enabled": ["basic_dashboard"], "mrr": 49.0, "industry": "SaaS",
    },
    "CUST-022": {
        "customer_id": "CUST-022", "name": "Victor Huang", "email": "victor@cybersec.io",
        "company": "CyberShield", "plan": "pro", "seats": 20, "seats_used": 20,
        "account_status": "active", "contract_id": "CONTRACT-022", "created_at": "2023-01-10",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","webhooks","priority_support","dark_mode"],
        "mrr": 299.0, "industry": "Cybersecurity",
    },
    "CUST-023": {
        "customer_id": "CUST-023", "name": "Wendy Osei", "email": "wendy@agritech.co",
        "company": "AgriTech Co.", "plan": "starter", "seats": 7, "seats_used": 9,
        "account_status": "active", "contract_id": "CONTRACT-023", "created_at": "2023-09-15",
        "features_enabled": ["basic_dashboard", "email_support"], "mrr": 49.0, "industry": "Agriculture",
    },
    "CUST-024": {
        "customer_id": "CUST-024", "name": "Xander Novak", "email": "xander@realestate.com",
        "company": "PropMgmt Inc.", "plan": "enterprise", "seats": 80, "seats_used": 80,
        "account_status": "active", "contract_id": "CONTRACT-024", "created_at": "2022-06-01",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 1999.0, "industry": "Real Estate",
    },
    "CUST-025": {
        "customer_id": "CUST-025", "name": "Yara Mansour", "email": "yara@travelco.com",
        "company": "TravelCo Global", "plan": "pro", "seats": 35, "seats_used": 12,
        "account_status": "suspended", "contract_id": "CONTRACT-025", "created_at": "2021-05-20",
        "features_enabled": ["basic_dashboard", "api_access"], "mrr": 299.0, "industry": "Travel",
    },
}

EXTRA_BILLING = {
    "CUST-021": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-21001"}],
    "CUST-022": [{"date": "2024-03-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-22001"},
                 {"date": "2024-02-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-22000"}],
    "CUST-023": [{"date": "2024-03-01", "amount": 49.0,   "status": "paid",   "invoice": "INV-23001"}],
    "CUST-024": [{"date": "2024-03-01", "amount": 1999.0, "status": "paid",   "invoice": "INV-24001"},
                 {"date": "2024-02-01", "amount": 1999.0, "status": "paid",   "invoice": "INV-24000"}],
    "CUST-025": [{"date": "2024-03-01", "amount": 299.0,  "status": "failed", "invoice": "INV-25001"},
                 {"date": "2024-02-01", "amount": 299.0,  "status": "failed", "invoice": "INV-25000"},
                 {"date": "2024-01-01", "amount": 299.0,  "status": "paid",   "invoice": "INV-24999"}],
}

EXTRA_CONTRACTS = {
    "CONTRACT-021": {
        "contract_id": "CONTRACT-021", "customer_id": "CUST-021", "plan": "starter",
        "start_date": "2024-03-01", "end_date": "2026-03-01", "sla_response_hours": 72,
        "included_features": ["basic_dashboard"], "seats": 2, "special_terms": None,
    },
    "CONTRACT-022": {
        "contract_id": "CONTRACT-022", "customer_id": "CUST-022", "plan": "pro",
        "start_date": "2023-01-10", "end_date": "2026-01-10", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","webhooks","priority_support","dark_mode"],
        "seats": 20, "special_terms": "Cybersecurity audit logs must be retained for 3 years.",
    },
    "CONTRACT-023": {
        "contract_id": "CONTRACT-023", "customer_id": "CUST-023", "plan": "starter",
        "start_date": "2023-09-15", "end_date": "2025-09-15", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support"], "seats": 7, "special_terms": None,
    },
    "CONTRACT-024": {
        "contract_id": "CONTRACT-024", "customer_id": "CUST-024", "plan": "enterprise",
        "start_date": "2022-06-01", "end_date": "2027-06-01", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 80, "special_terms": "Real estate data compliance. MLS integration support included.",
        "sla_violation_penalty": "10% MRR per day",
    },
    "CONTRACT-025": {
        "contract_id": "CONTRACT-025", "customer_id": "CUST-025", "plan": "pro",
        "start_date": "2021-05-20", "end_date": "2025-05-20", "sla_response_hours": 24,
        "included_features": ["basic_dashboard", "api_access"],
        "seats": 35, "special_terms": "Account suspended: 2 failed payments. Reactivation requires Finance approval.",
    },
}

# ─────────────────────────────────────────────────────────────
# HELPER — merged view (all 25 customers)
# ─────────────────────────────────────────────────────────────
def get_all_customers():
    from data.mock_data import CUSTOMERS
    return {**CUSTOMERS, **EXTENDED_CUSTOMERS, **EXTRA_CUSTOMERS}

def get_all_billing():
    from data.mock_data import BILLING_HISTORY
    return {**BILLING_HISTORY, **EXTENDED_BILLING, **EXTRA_BILLING}

def get_all_contracts():
    from data.mock_data import CONTRACTS
    return {**CONTRACTS, **EXTENDED_CONTRACTS, **EXTRA_CONTRACTS}

