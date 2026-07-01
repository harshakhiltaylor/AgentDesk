"""
feature_tools.py
----------------
Mock tools for the Feature Agent.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools.tool_base import BaseTool, ToolResult
from data.mock_data import FEATURE_MATRIX, FEATURE_DOCS


class FeatureTools(BaseTool):

    def get_feature_matrix(self) -> ToolResult:
        def _inner():
            return FEATURE_MATRIX
        return self._call("get_feature_matrix", _inner)

    def get_feature_documentation(self, feature_name: str) -> ToolResult:
        def _inner():
            doc = FEATURE_DOCS.get(feature_name)
            if not doc:
                return {"name": feature_name, "description": "No documentation found.", "setup": "Contact support."}
            return doc
        return self._call("get_feature_documentation", _inner)

    def validate_configuration(self, feature: str, plan: str) -> ToolResult:
        def _inner():
            plan_features = FEATURE_MATRIX.get(plan, {})
            available = plan_features.get(feature, False)
            return {
                "feature": feature,
                "plan": plan,
                "available": available,
                "message": f"'{feature}' is {'available' if available else 'NOT available'} on the {plan} plan.",
            }
        return self._call("validate_configuration", _inner)

    def check_feature_limits(self, feature: str, plan: str) -> ToolResult:
        def _inner():
            plan_features = FEATURE_MATRIX.get(plan, {})
            limit_key = f"{feature}_limit" if feature != "api" else "api_rate_limit"
            # Generic: return all limit-related keys
            limits = {k: v for k, v in plan_features.items() if "limit" in k}
            return {"feature": feature, "plan": plan, "limits": limits}
        return self._call("check_feature_limits", _inner)
