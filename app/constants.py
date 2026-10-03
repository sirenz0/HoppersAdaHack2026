from datetime import time

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TIME_PERIODS = {
    "morning": (time(9, 0), time(12, 0)),
    "afternoon": (time(12, 0), time(17, 0)),
    "evening": (time(17, 0), time(20, 0)),
}


def format_time_range(start_time, end_time):
    return f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"


NEED_CATEGORIES = [
    ("Protein", "need_protein_pct"),
    ("Carbs", "need_carbs_pct"),
    ("Fats", "need_fats_pct"),
    ("Fiber", "need_fiber_pct"),
    ("Fruits and Veg", "need_fruit_veg_pct"),
    ("Tinned Goods", "need_tinned_goods_pct"),
]

DONATION_ITEMS = [
    "Pasta",
    "Rice",
    "Tinned Beans",
    "Tinned Soup",
    "UHT Milk",
    "Cereal",
    "Baby Formula",
    "Nappies",
    "Toiletries",
    "Tinned Fish",
    "Pasta Sauce",
    "Long-life Juice",
]
