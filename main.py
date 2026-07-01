"""
main.py — CLI entry point
Usage:
  python main.py --scenario 1
  python main.py --query "How do I enable dark mode?" --customer CUST-001
"""
import argparse, json, os, sys
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

sys.path.insert(0, os.path.dirname(__file__))
from agents.graph import run_investigation

SCENARIOS = {
    1: ("How do I enable dark mode in my account?",                                                            "CUST-001"),
    2: ("I'm on the Starter plan but need API access for my automation. What are my options?",                 "CUST-001"),
    3: ("Docs say Pro has unlimited API calls but I'm getting rate limited after 1000. My account shows Pro.", "CUST-002"),
    4: ("Waiting 10 days for support on a critical issue. 24h SLA contract. Costing $500/day. Escalate now.", "CUST-003"),
    5: ("Migrated from competitor. 15 users but plan shows 10 seats. Help me set up everyone.",                "CUST-004"),
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query",    "-q")
    p.add_argument("--customer", "-c", default=None)
    p.add_argument("--scenario", "-s", type=int, choices=range(1,6))
    p.add_argument("--json",     action="store_true")
    args = p.parse_args()

    if args.scenario:
        query, cid = SCENARIOS[args.scenario]
        cid = args.customer or cid
        print(f"\n🎬 Scenario {args.scenario} | Customer: {cid}")
    elif args.query:
        query, cid = args.query, args.customer
    else:
        p.print_help(); sys.exit(1)

    result = run_investigation(query, cid)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"SESSION : {result['session_id']}")
        print(f"PLAN    : {' → '.join(result['plan'])}")
        print(f"ELAPSED : {result['elapsed_s']}s")
        print(f"\n💬 RESPONSE:\n{result['response']}")
        if result["escalated"]:
            t = result.get("escalation_ticket", {})
            print(f"\n🚨 ESCALATED — Ticket: {t.get('ticket_id')} | Priority: {t.get('priority')}")
        print("="*60)

if __name__ == "__main__":
    main()
