"""
account_tools.py
----------------
Mock tools that the Account Agent calls.
All data comes from mock_data.py — no real DB needed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.tool_base import BaseTool, ToolResult
from data.extended_mock_data import get_all_customers, get_all_billing
CUSTOMERS = get_all_customers()
BILLING_HISTORY = get_all_billing()


class AccountTools(BaseTool):

    def lookup_customer(self, customer_id: str) -> ToolResult:
        def _inner():
            customer = CUSTOMERS.get(customer_id)
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            return customer
        return self._call("lookup_customer", _inner)

    def get_billing_history(self, customer_id: str) -> ToolResult:
        def _inner():
            history = BILLING_HISTORY.get(customer_id, [])
            if not history:
                raise ValueError(f"No billing history for {customer_id}")
            return history
        return self._call("get_billing_history", _inner)

    def check_account_status(self, customer_id: str) -> ToolResult:
        def _inner():
            customer = CUSTOMERS.get(customer_id)
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            return {
                "status": customer["account_status"],
                "plan": customer["plan"],
                "seats": customer["seats"],
                "seats_used": customer["seats_used"],
            }
        return self._call("check_account_status", _inner)

    def list_enabled_features(self, customer_id: str) -> ToolResult:
        def _inner():
            customer = CUSTOMERS.get(customer_id)
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
            return customer["features_enabled"]
        return self._call("list_enabled_features", _inner)
