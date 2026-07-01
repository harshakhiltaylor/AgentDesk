"""
test_tools.py — Unit tests for all tool classes
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from tools.account_tools import AccountTools
from tools.feature_tools import FeatureTools
from tools.contract_tools import ContractTools
from tools.escalation_tools import EscalationTools


class TestAccountTools(unittest.TestCase):
    def setUp(self):
        self.tools = AccountTools()
        # Disable random failures for tests
        self.tools.FAILURE_RATE = 0.0

    def test_lookup_known_customer(self):
        result = self.tools.lookup_customer("CUST-001")
        self.assertTrue(result.success)
        self.assertEqual(result.data["plan"], "starter")

    def test_lookup_unknown_customer(self):
        result = self.tools.lookup_customer("CUST-999")
        self.assertFalse(result.success)

    def test_billing_history(self):
        result = self.tools.get_billing_history("CUST-002")
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, list)

    def test_account_status(self):
        result = self.tools.check_account_status("CUST-005")
        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "suspended")

    def test_enabled_features(self):
        result = self.tools.list_enabled_features("CUST-003")
        self.assertTrue(result.success)
        self.assertIn("sso", result.data)


class TestFeatureTools(unittest.TestCase):
    def setUp(self):
        self.tools = FeatureTools()
        self.tools.FAILURE_RATE = 0.0

    def test_feature_matrix(self):
        result = self.tools.get_feature_matrix()
        self.assertTrue(result.success)
        self.assertIn("starter", result.data)
        self.assertIn("pro", result.data)
        self.assertIn("enterprise", result.data)

    def test_starter_no_api(self):
        result = self.tools.validate_configuration("api_access", "starter")
        self.assertTrue(result.success)
        self.assertFalse(result.data["available"])

    def test_pro_has_api(self):
        result = self.tools.validate_configuration("api_access", "pro")
        self.assertTrue(result.success)
        self.assertTrue(result.data["available"])

    def test_dark_mode_docs(self):
        result = self.tools.get_feature_documentation("dark_mode")
        self.assertTrue(result.success)
        self.assertIn("Settings", result.data["setup"])

    def test_api_rate_limit_pro(self):
        result = self.tools.check_feature_limits("api_access", "pro")
        self.assertTrue(result.success)
        self.assertEqual(result.data["limits"].get("api_rate_limit"), 1000)


class TestContractTools(unittest.TestCase):
    def setUp(self):
        self.tools = ContractTools()
        self.tools.FAILURE_RATE = 0.0

    def test_lookup_contract(self):
        result = self.tools.lookup_contract("CONTRACT-003")
        self.assertTrue(result.success)
        self.assertEqual(result.data["sla_response_hours"], 4)

    def test_sla_violation(self):
        # Issue date far in the past → definitely violated
        result = self.tools.validate_sla_compliance("CONTRACT-003", "2020-01-01T00:00:00")
        self.assertTrue(result.success)
        self.assertTrue(result.data["violated"])

    def test_get_features(self):
        result = self.tools.get_included_features("CONTRACT-002")
        self.assertTrue(result.success)
        self.assertIn("api_access", result.data)


class TestEscalationTools(unittest.TestCase):
    def setUp(self):
        self.tools = EscalationTools()
        self.tools.FAILURE_RATE = 0.0

    def test_create_ticket(self):
        result = self.tools.create_escalation_ticket(
            "SLA violated", "P1", {"session": "test-123"}
        )
        self.assertTrue(result.success)
        self.assertIn("ticket_id", result.data)
        self.assertTrue(result.data["ticket_id"].startswith("ESC-"))

    def test_routing(self):
        result = self.tools.get_escalation_routing("sla_violation")
        self.assertTrue(result.success)
        self.assertEqual(result.data["team"], "Customer Success")
        self.assertEqual(result.data["priority"], "P1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
