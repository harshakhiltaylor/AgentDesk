"""
test_memory.py — Tests for SharedContext and StateManager
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from memory.shared_context import SharedContext
from memory.state_manager import StateManager


class TestSharedContext(unittest.TestCase):
    def setUp(self):
        self.ctx = SharedContext(session_id="TEST-001", customer_id="CUST-001")
        self.ctx.query = "Test query"

    def test_add_finding(self):
        self.ctx.add_finding("AccountAgent", "Plan is starter", {"plan": "starter"})
        self.assertEqual(len(self.ctx.agent_findings), 1)
        self.assertEqual(self.ctx.agent_findings[0].agent, "AccountAgent")

    def test_add_decision(self):
        self.ctx.add_decision("plan", "escalate", "SLA violated", "ContractAgent")
        self.assertEqual(len(self.ctx.decisions), 1)

    def test_conflict_tracking(self):
        self.ctx.add_conflict("docs", "system", "Rate limit mismatch", "Trust system")
        self.assertEqual(len(self.ctx.conflicts), 1)

    def test_mark_agents(self):
        self.ctx.mark_agent_complete("AccountAgent")
        self.ctx.mark_agent_failed("FeatureAgent", "timeout")
        self.assertIn("AccountAgent", self.ctx.completed_agents)
        self.assertIn("FeatureAgent", self.ctx.failed_agents)

    def test_get_findings_by_agent(self):
        self.ctx.add_finding("AccountAgent", "finding 1")
        self.ctx.add_finding("FeatureAgent", "finding 2")
        acct_findings = self.ctx.get_findings_by_agent("AccountAgent")
        self.assertEqual(len(acct_findings), 1)

    def test_summary_structure(self):
        summary = self.ctx.get_summary()
        self.assertIn("session_id", summary)
        self.assertIn("should_escalate", summary)
        self.assertIn("conflicts", summary)


class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.sm = StateManager()

    def test_create_session(self):
        ctx = self.sm.create_session("CUST-001")
        self.assertIsNotNone(ctx.session_id)
        self.assertTrue(ctx.session_id.startswith("SIQ-"))

    def test_retrieve_session(self):
        ctx = self.sm.create_session("CUST-002")
        retrieved = self.sm.get_session(ctx.session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.customer_id, "CUST-002")

    def test_missing_session(self):
        result = self.sm.get_session("NONEXISTENT")
        self.assertIsNone(result)

    def test_delete_session(self):
        ctx = self.sm.create_session()
        self.sm.delete_session(ctx.session_id)
        self.assertIsNone(self.sm.get_session(ctx.session_id))


if __name__ == "__main__":
    unittest.main(verbosity=2)
