from datetime import datetime

def get_today_str() -> str:
    """Current date in human readable format"""
    return datetime.now().strftime("%Y-%m-%d")

# date = get_today_str()
# print(date)