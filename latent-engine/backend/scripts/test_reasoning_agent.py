from app.agent.reasoning_agent import (
    ReasoningAgent,
)


def main():

    agent = (
        ReasoningAgent()
    )

    questions = [

        "Which modules are risky?",

        "Which modules are deteriorating?",

        "How can we improve payments.py?",

        "What happens if Alice leaves?",
    ]

    print(
        "\n=== REASONING AGENT ===\n"
    )

    for question in questions:

        response = (
            agent.answer(
                question
            )
        )

        print(
            f"Question: {question}"
        )

        print(
            f"Intent: "
            f"{response.intent}"
        )

        print(
            f"Route: "
            f"{response.route}"
        )

        print(
            f"Summary: "
            f"{response.summary}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()