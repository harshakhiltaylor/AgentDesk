"""
AgentDesk Mock Dataset
----------------------
Realistic mock data for AgentDesk SaaS platform.
"""

CUSTOMERS = {
    "CUST-001": {
        "customer_id": "CUST-001", "name": "Alice Johnson", "email": "alice@startupco.io",
        "company": "StartupCo", "plan": "starter", "seats": 5, "seats_used": 5,
        "account_status": "active", "contract_id": "CONTRACT-001", "created_at": "2023-06-01",
        "features_enabled": ["basic_dashboard", "email_support", "dark_mode"], "mrr": 49.0,
    },
    "CUST-002": {
        "customer_id": "CUST-002", "name": "Bob Martinez", "email": "bob@techfirm.com",
        "company": "TechFirm Inc.", "plan": "pro", "seats": 20, "seats_used": 18,
        "account_status": "active", "contract_id": "CONTRACT-002", "created_at": "2022-11-15",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "mrr": 299.0,
    },
    "CUST-003": {
        "customer_id": "CUST-003", "name": "Carol Smith", "email": "carol@enterprise.org",
        "company": "Enterprise Corp", "plan": "enterprise", "seats": 100, "seats_used": 97,
        "account_status": "active", "contract_id": "CONTRACT-003", "created_at": "2021-03-10",
        "features_enabled": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "mrr": 1499.0,
    },
    "CUST-004": {
        "customer_id": "CUST-004", "name": "David Lee", "email": "david@newco.io",
        "company": "NewCo", "plan": "starter", "seats": 10, "seats_used": 15,
        "account_status": "active", "contract_id": "CONTRACT-004", "created_at": "2024-01-20",
        "features_enabled": ["basic_dashboard", "email_support"], "mrr": 49.0,
    },
    "CUST-005": {
        "customer_id": "CUST-005", "name": "Eve Chen", "email": "eve@legacytech.com",
        "company": "LegacyTech", "plan": "pro", "seats": 30, "seats_used": 28,
        "account_status": "suspended", "contract_id": "CONTRACT-005", "created_at": "2020-08-01",
        "features_enabled": ["basic_dashboard", "api_access"], "mrr": 299.0,
    },
}

BILLING_HISTORY = {
    "CUST-001": [
        {"date": "2024-03-01", "amount": 49.0, "status": "paid", "invoice": "INV-1001"},
        {"date": "2024-02-01", "amount": 49.0, "status": "paid", "invoice": "INV-1000"},
    ],
    "CUST-002": [
        {"date": "2024-03-01", "amount": 299.0, "status": "paid", "invoice": "INV-2001"},
        {"date": "2024-02-01", "amount": 299.0, "status": "paid", "invoice": "INV-2000"},
    ],
    "CUST-003": [
        {"date": "2024-03-01", "amount": 1499.0, "status": "paid", "invoice": "INV-3001"},
        {"date": "2024-02-01", "amount": 1499.0, "status": "paid", "invoice": "INV-3000"},
    ],
    "CUST-004": [
        {"date": "2024-03-01", "amount": 49.0, "status": "paid", "invoice": "INV-4001"},
    ],
    "CUST-005": [
        {"date": "2024-03-01", "amount": 299.0, "status": "failed", "invoice": "INV-5001"},
        {"date": "2024-02-01", "amount": 299.0, "status": "paid", "invoice": "INV-5000"},
    ],
}

FEATURE_MATRIX = {
    "starter": {
        "basic_dashboard": True, "dark_mode": True, "email_support": True,
        "api_access": False, "advanced_analytics": False, "webhooks": False,
        "priority_support": False, "sso": False, "custom_roles": False,
        "dedicated_support": False, "api_rate_limit": None, "seats_limit": 10,
    },
    "pro": {
        "basic_dashboard": True, "dark_mode": True, "email_support": True,
        "api_access": True, "advanced_analytics": True, "webhooks": True,
        "priority_support": True, "sso": False, "custom_roles": False,
        "dedicated_support": False, "api_rate_limit": 1000, "seats_limit": 50,
    },
    "enterprise": {
        "basic_dashboard": True, "dark_mode": True, "email_support": True,
        "api_access": True, "advanced_analytics": True, "webhooks": True,
        "priority_support": True, "sso": True, "custom_roles": True,
        "dedicated_support": True, "api_rate_limit": None, "seats_limit": None,
    },
}

FEATURE_DOCS = {
    "dark_mode": {
        "name": "Dark Mode",
        "description": "Switch the interface to a dark color scheme.",
        "setup": "Go to Settings -> Appearance -> Theme -> Select 'Dark'. Available on all plans.",
        "plans": ["starter", "pro", "enterprise"],
    },
    "api_access": {
        "name": "API Access",
        "description": "Programmatic access to AgentDesk via REST API.",
        "setup": "Generate an API key in Settings -> Developer -> API Keys.",
        "plans": ["pro", "enterprise"],
        "note": "Marketing docs incorrectly stated 'unlimited' for Pro. Actual limit is 1,000 calls/month on Pro. Enterprise is truly unlimited.",
    },
    "advanced_analytics": {
        "name": "Advanced Analytics",
        "description": "Deep-dive dashboards with custom reports.",
        "setup": "Access via Analytics tab. Available on Pro and Enterprise.",
        "plans": ["pro", "enterprise"],
    },
    "sso": {
        "name": "Single Sign-On (SSO)",
        "description": "SAML/OIDC-based SSO integration.",
        "setup": "Configure in Settings -> Security -> SSO. Enterprise only.",
        "plans": ["enterprise"],
    },
    "webhooks": {
        "name": "Webhooks",
        "description": "Real-time event notifications via HTTP POST.",
        "setup": "Configure in Settings -> Developer -> Webhooks.",
        "plans": ["pro", "enterprise"],
    },
}

CONTRACTS = {
    "CONTRACT-001": {
        "contract_id": "CONTRACT-001", "customer_id": "CUST-001", "plan": "starter",
        "start_date": "2023-06-01", "end_date": "2025-06-01", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support", "dark_mode"],
        "seats": 5, "special_terms": None,
    },
    "CONTRACT-002": {
        "contract_id": "CONTRACT-002", "customer_id": "CUST-002", "plan": "pro",
        "start_date": "2022-11-15", "end_date": "2025-11-15", "sla_response_hours": 24,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks"],
        "seats": 20, "special_terms": "API rate limit: 1,000 calls/month as per standard Pro plan.",
    },
    "CONTRACT-003": {
        "contract_id": "CONTRACT-003", "customer_id": "CUST-003", "plan": "enterprise",
        "start_date": "2021-03-10", "end_date": "2026-03-10", "sla_response_hours": 4,
        "included_features": ["basic_dashboard","advanced_analytics","api_access","priority_support","dark_mode","webhooks","sso","custom_roles","dedicated_support"],
        "seats": 100, "special_terms": "Dedicated CSM. SLA violation = 10% MRR credit per day.",
        "sla_violation_penalty": "10% MRR per day",
    },
    "CONTRACT-004": {
        "contract_id": "CONTRACT-004", "customer_id": "CUST-004", "plan": "starter",
        "start_date": "2024-01-20", "end_date": "2026-01-20", "sla_response_hours": 72,
        "included_features": ["basic_dashboard", "email_support"],
        "seats": 10, "special_terms": None,
    },
    "CONTRACT-005": {
        "contract_id": "CONTRACT-005", "customer_id": "CUST-005", "plan": "pro",
        "start_date": "2020-08-01", "end_date": "2025-08-01", "sla_response_hours": 24,
        "included_features": ["basic_dashboard", "api_access"],
        "seats": 30, "special_terms": "Account suspended due to non-payment.",
    },
}

SUPPORT_TICKETS = {
    "TICKET-9901": {
        "ticket_id": "TICKET-9901", "customer_id": "CUST-003", "contract_id": "CONTRACT-003",
        "created_at": "2024-03-01T09:00:00", "issue": "Critical production outage — API returning 500 errors",
        "priority": "critical", "status": "open", "last_response_at": None,
        "sla_hours": 4, "sla_breached": True,
    },
}
