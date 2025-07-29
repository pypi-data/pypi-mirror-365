from datetime import date, timedelta
from typing import Optional

def next_weekday_date(target_weekday: str, reference_date: Optional[date] = None) -> date:
    """
    Find the next future date (including today) for a given weekday, returning only date components.
    
    Args:
        target_weekday: The weekday to find (e.g., 'Monday', 'Tuesday', etc.)
        reference_date: The date to search from (defaults to current date)
    
    Returns:
        The next date with the specified weekday as a date object (year, month, day only)
    """
    # Weekday mapping
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Validate input
    target_weekday = target_weekday.capitalize()
    if target_weekday not in weekdays:
        raise ValueError(f"Invalid weekday. Must be one of: {weekdays}")
    
    # Use current date if no reference date provided
    if reference_date is None:
        reference_date = date.today()
    
    # Get numeric values (Monday=0, Sunday=6)
    target_num = weekdays.index(target_weekday)
    current_num = reference_date.weekday()
    
    # Calculate days needed to reach the target weekday
    days_until = (target_num - current_num) % 7
    # If today is the target day and we want to include today, keep days_until as 0
    
    # Calculate the next date
    next_date = reference_date + timedelta(days=days_until)
    
    return next_date.isoformat()

# Example usage
if __name__ == "__main__":
    # Find next Wednesday (including today if it's Wednesday)
    print("Next Wednesday:", next_weekday_date("Wednesday"))
    
    # Find next Sunday from a specific date
    test_date = date(2023, 11, 15)  # This was a Wednesday
    print("Next Sunday from Nov 15, 2023:", next_weekday_date("Sunday", test_date))
    
    # Find next Friday
    print(f"Next Friday: {next_weekday_date('Friday')}")
    
    # Example showing it includes today if it matches
    today_weekday = date.today().strftime("%A")
    print(f"Next {today_weekday} (includes today): {next_weekday_date(today_weekday)}")