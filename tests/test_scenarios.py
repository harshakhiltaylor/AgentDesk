"""
test_scenarios.py — Robust integration regression test suite for AgentDesk.
Dynamically spawns and executes test methods for 10 challenging scenarios.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest
from agents.graph import run_investigation

class TestAgentScenarios(unittest.TestCase):
    test_results = []
    scenarios_loaded = 0

    @classmethod
    def setUpClass(cls):
        print(f"\n Initiating AgentDesk Integration Evaluation Suite\n")

    @classmethod
    def tearDownClass(cls):
        # Print evaluation benchmark table at the end of the test suite
        print("\n" + "="*95)
        print("                        AGENTDESK REGRESSION EVALUATION BENCHMARK")
        print("="*95)
        print(f"{'ID':<3} | {'Query (Truncated)':<32} | {'Expected Plan':<30} | {'Complexity':<10} | {'Latency':<8} | {'Status':<6}")
        print("-"*95)
        
        passes = 0
        sorted_results = sorted(cls.test_results, key=lambda x: x["id"])
        for tr in sorted_results:
            q_trunc = tr["query"][:29] + "..." if len(tr["query"]) > 29 else tr["query"]
            status_str = " PASS" if tr["status"] == "PASS" else " FAIL"
            if tr["status"] == "PASS":
                passes += 1
            
            plan_str = ", ".join(tr["expected_plan"])
            if len(plan_str) > 27:
                plan_str = plan_str[:25] + "..."
            
            print(f"{tr['id']:<3} | {q_trunc:<32} | {plan_str:<30} | {tr['actual_complexity']:<10} | {tr['latency']:.2f}s   | {status_str:<6}")
        
        print("="*95)
        print(f"Overall Accuracy: {passes}/{len(cls.test_results)} ({(passes/len(cls.test_results))*100:.1f}%)")
        print("="*95 + "\n")

def make_test_function(scenario):
    def test(self):
        sid = scenario["id"]
        query = scenario["query"]
        cid = scenario["customer_id"]
        expected_plan = scenario["plan"]
        expected_escalated = scenario["escalated"]

        print(f" Running Test Scenario {sid}: '{query[:45]}...'")
        t0 = time.time()
        status = "PASS"
        err_msg = ""
        
        # Prevent API bursting by sleeping briefly before execution
        time.sleep(1)

        try:
            # Execute with exponential backoff on rate limits
            max_retries = 5
            retry_delay = 6.0
            res = None
            
            for attempt in range(max_retries):
                try:
                    res = run_investigation(query, cid)
                    break
                except Exception as e:
                    # Check if it is a rate limit error (status code 429 or text)
                    is_rate_limit = "rate_limit" in str(e).lower() or "429" in str(e)
                    if is_rate_limit and attempt < max_retries - 1:
                        print(f"⚠️ Groq rate limit hit (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5  # Exponential backoff
                    else:
                        raise e

            latency = time.time() - t0
            
            actual_plan = res.get("plan", []) if res else []
            actual_complexity = res.get("complexity", "medium") if res else "medium"
            actual_escalated = res.get("escalated", False) if res else False
            response = res.get("response", "") if res else ""

            # ── Assertions ────────────────────────────────────────────────
            # 1. Output content check
            self.assertTrue(len(response) > 0, f"Scenario {sid}: Synthesized response is empty!")
            
            # 2. Plan checking: All expected specialist agents must be triggered
            for agent in expected_plan:
                self.assertIn(
                    agent, actual_plan, 
                    f"Scenario {sid}: Missing expected specialist '{agent}' in plan {actual_plan}"
                )
            
            # 3. Escalated checking
            self.assertEqual(
                actual_escalated, expected_escalated, 
                f"Scenario {sid}: Escalation mismatch. Expected: {expected_escalated}, Got: {actual_escalated}"
            )
            
            # 4. Complexity validation
            self.assertIn(actual_complexity, ["low", "medium", "high"])

        except Exception as e:
            status = "FAIL"
            latency = time.time() - t0
            actual_complexity = "error"
            actual_escalated = False
            err_msg = str(e)
            print(f"Scenario {sid} failed: {err_msg}")
            raise e
        finally:
            self.test_results.append({
                "id": sid,
                "query": query,
                "expected_plan": expected_plan,
                "actual_complexity": actual_complexity,
                "actual_escalated": actual_escalated,
                "latency": latency,
                "status": status,
                "error": err_msg
            })
    return test

# Load scenarios and bind them dynamically as separate test cases
base_dir = os.path.dirname(os.path.dirname(__file__))
results_file = os.path.join(base_dir, "results", "query_results.json")
if os.path.exists(results_file):
    with open(results_file, "r") as f:
        data = json.load(f)
    scenarios = data.get("scenarios", [])
    TestAgentScenarios.scenarios_loaded = len(scenarios)
    for s in scenarios:
        test_func = make_test_function(s)
        test_func.__doc__ = f"Validate scenario {s['id']}: {s['query'][:50]}..."
        setattr(TestAgentScenarios, f"test_scenario_{s['id']}", test_func)

if __name__ == "__main__":
    unittest.main()
