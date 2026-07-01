"""
contract_tools.py
-----------------
Mock tools for the Contract Agent.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from tools.tool_base import BaseTool, ToolResult
from data.extended_mock_data import get_all_contracts
CONTRACTS = get_all_contracts()
from data.mock_data import SUPPORT_TICKETS


class ContractTools(BaseTool):

    def lookup_contract(self, contract_id: str) -> ToolResult:
        def _inner():
            contract = CONTRACTS.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            return contract
        return self._call("lookup_contract", _inner)

    def get_contract_terms(self, contract_id: str) -> ToolResult:
        def _inner():
            contract = CONTRACTS.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            return {
                "sla_response_hours": contract["sla_response_hours"],
                "special_terms": contract.get("special_terms"),
                "start_date": contract["start_date"],
                "end_date": contract["end_date"],
            }
        return self._call("get_contract_terms", _inner)

    def validate_sla_compliance(self, contract_id: str, issue_date: str) -> ToolResult:
        def _inner():
            contract = CONTRACTS.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            sla_hours = contract["sla_response_hours"]
            try:
                issue_dt = datetime.fromisoformat(issue_date)
                now = datetime.now()
                hours_elapsed = (now - issue_dt).total_seconds() / 3600
                violated = hours_elapsed > sla_hours
                return {
                    "contract_id": contract_id,
                    "sla_hours": sla_hours,
                    "hours_elapsed": round(hours_elapsed, 1),
                    "violated": violated,
                    "severity": "critical" if violated and sla_hours <= 4 else ("high" if violated else "ok"),
                }
            except Exception as e:
                raise ValueError(f"Invalid issue_date format: {e}")
        return self._call("validate_sla_compliance", _inner)

    def get_included_features(self, contract_id: str) -> ToolResult:
        def _inner():
            contract = CONTRACTS.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            return contract.get("included_features", [])
        return self._call("get_included_features", _inner)
