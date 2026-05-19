from src.workflow.crew_setup import get_financial_advice_crew

def test_crew():
    print("Testing CrewAI with Gemini...")
    query = "What is the difference between a Call and a Put option?"
    result = get_financial_advice_crew(query)
    print(f"\nCrew Output:\n{result}")

if __name__ == "__main__":
    test_crew()
