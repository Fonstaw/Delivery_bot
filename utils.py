import re
from typing import Optional, Tuple

def extract_numbers_from_text(text: str) -> Tuple[bool, int, float]:
    """
    Extract numbers from food description and calculate total
    Returns: (success, total_items, total_price)
    """
    numbers = re.findall(r'\b[1-9]\b', text)
    if not numbers:
        return False, 0, 0.0
    
    total_items = sum(int(num) for num in numbers)
    total_price = total_items * 6.65  # Price per item
    return True, total_items, total_price

def validate_place_input(place: str) -> bool:
    """Validate place input contains Main, Agri, or Tecno"""
    place_lower = place.lower()
    return any(keyword in place_lower for keyword in ['main', 'agri', 'tecno'])

def get_channel_for_order(gender: str, place: str) -> str:
    """Determine which channel to post order based on gender and place"""
    place_lower = place.lower()
    
    if 'agri' in place_lower:
        return 'agri'
    elif 'main' in place_lower:
        if gender.upper() == 'F':
            return 'female_main'
        else:
            return 'male_main'
    elif 'tecno' in place_lower:
        if gender.upper() == 'F':
            return 'female_tecno'
        else:
            return 'male_tecno'
    else:
        return 'male_main'  # Default fallback

def format_order_preview(order_data: dict) -> str:
    """Format order preview message"""
    return f"""ውድ ደንበኛች ያስገቡት መረጃ ከስር ያለውን ይመስላል⬇️

👩‍🍳Cafe: {order_data['cafe']}
📄Name: {order_data['name']}
🧒Gender: {order_data['gender']}
☎️Phone: {order_data['phone']}
⏰Time: {order_data['time']}
🍜Food: {order_data['food']}
🏢Place: {order_data['place']}
💰Total: {order_data['total_price']:.2f} ETB
📦Order #: {order_data['order_number']}"""