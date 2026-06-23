from app.agent.reasoning_agent import (
    ReasoningAgent,
)


def main():

    agent = ReasoningAgent()

    questions = [

        # Risk
        "Which modules are risky?",
        "Why is payments.py risky?",
        "Which modules have weak coverage?",
        "Which modules have dangerous concentration?",

        # Forecast
        "Which modules are deteriorating?",
        "What will be the riskiest module in 3 months?",
        "Show me future risks",

        # Intervention
        "How can we improve payments.py?",
        "What should we do next quarter?",
        "Which action has highest impact?",
        "Who should take over auth.py?",

        # Simulation
        "What happens if Alice leaves?",
        "What if David leaves payments.py?",
        "Which departure hurts most?",

        # Future capabilities
        "Who should take over payments.py?",
        "Which developer should we train next?",
        "Where should we invest knowledge transfer?",
        "Who is the best mentor?",
        "Who is the best successor?",
        "Which team is overloaded?",
        "What is the best intervention for the whole organization?",
    ]

    print("\n=== AGENT STRESS TEST ===\n")

    for q in questions:

        print(f"\nQ: {q}")

        try:

            response = agent.answer(q)

            print(f"Intent: {response.intent}")
            print(f"Route: {response.route}")
            print(f"Summary:\n{response.summary}")

        except Exception as e:

            print(f"FAILED: {e}")

        print("-" * 60)


if __name__ == "__main__":
    main()