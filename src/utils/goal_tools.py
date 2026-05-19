from crewai.tools import tool

@tool("calculate_retirement_savings")
def calculate_retirement_savings(current_savings: float, monthly_contribution: float, annual_return: float, years: int) -> str:
    """
    Calculates the projected retirement savings based on current savings, monthly contributions, expected annual return, and time horizon.
    """
    try:
        monthly_return = (1 + annual_return/100)**(1/12) - 1
        months = years * 12
        future_value = current_savings * (1 + monthly_return)**months + \
                       monthly_contribution * (((1 + monthly_return)**months - 1) / monthly_return)
        
        return f"Projected retirement savings after {years} years: ${future_value:,.2f}"
    except Exception as e:
        return f"Error in calculation: {e}"

@tool("calculate_savings_goal")
def calculate_savings_goal(target_amount: float, current_savings: float, annual_return: float, years: int) -> str:
    """
    Calculates the required monthly contribution to reach a specific savings goal.
    """
    try:
        monthly_return = (1 + annual_return/100)**(1/12) - 1
        months = years * 12
        if monthly_return == 0:
            required_monthly = (target_amount - current_savings) / months
        else:
            required_monthly = (target_amount - current_savings * (1 + monthly_return)**months) * \
                               (monthly_return / ((1 + monthly_return)**months - 1))
        
        return f"To reach your goal of ${target_amount:,.2f} in {years} years, you need to save ${required_monthly:,.2f} per month."
    except Exception as e:
        return f"Error in calculation: {e}"
