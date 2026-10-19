import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_csv_files():
    """Generates 4 sector-specific CSV files for the team members."""
    os.makedirs('data', exist_ok=True)
    today = datetime.now()
    
    # Member 1: Canteen Waste
    canteens = ["North Campus Mess", "Central Dining Hall", "Engineering Canteen", "Hostel 3 Mess"]
    canteen_data = []
    for i in range(1, 51):
        added = today - timedelta(days=random.randint(0, 30))
        canteen_data.append({
            'id': f"CNT-{1000+i}",
            'donor_id': 1,
            'source_type': 'Canteen',
            'food_type': random.choice(['Cooked Meals', 'Bakery & Bread']),
            'quantity_kg': round(random.uniform(5.0, 45.0), 1),
            'date_added': added.strftime('%Y-%m-%d'),
            'expiry_date': (added + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d'),
            'location': random.choice(canteens),
            'status': random.choice(['Available', 'Donated', 'Discarded'])
        })
    pd.DataFrame(canteen_data).to_csv('data/canteen_waste.csv', index=False)

    # Member 2: Restaurant Waste
    restaurants = ["Bistro Bites", "Royal Spice Hotel", "Urban Cafe", "Grand Buffet"]
    restaurant_data = []
    for i in range(1, 51):
        added = today - timedelta(days=random.randint(0, 30))
        restaurant_data.append({
            'id': f"RST-{1000+i}",
            'donor_id': 2,
            'source_type': 'Restaurant',
            'food_type': random.choice(['Cooked Meals', 'Dairy Products']),
            'quantity_kg': round(random.uniform(3.0, 30.0), 1),
            'date_added': added.strftime('%Y-%m-%d'),
            'expiry_date': (added + timedelta(days=random.randint(1, 2))).strftime('%Y-%m-%d'),
            'location': random.choice(restaurants),
            'status': random.choice(['Available', 'Donated', 'Discarded'])
        })
    pd.DataFrame(restaurant_data).to_csv('data/restaurant_waste.csv', index=False)

    # Member 3: Supermarket Waste
    supermarkets = ["Fresh Mart", "City Hypermarket", "Green Grocers", "Value Supermarket"]
    supermarket_data = []
    for i in range(1, 51):
        added = today - timedelta(days=random.randint(0, 30))
        supermarket_data.append({
            'id': f"SPM-{1000+i}",
            'donor_id': 3,
            'source_type': 'Supermarket',
            'food_type': random.choice(['Fresh Produce', 'Packaged Items', 'Dairy Products']),
            'quantity_kg': round(random.uniform(10.0, 60.0), 1),
            'date_added': added.strftime('%Y-%m-%d'),
            'expiry_date': (added + timedelta(days=random.randint(2, 7))).strftime('%Y-%m-%d'),
            'location': random.choice(supermarkets),
            'status': random.choice(['Available', 'Donated', 'Discarded'])
        })
    pd.DataFrame(supermarket_data).to_csv('data/supermarket_waste.csv', index=False)

    # Member 4: Event Catering Waste
    events = ["Convention Center Hall A", "Grand Palace Banquets", "Community Center", "Royal Celebration Lawn"]
    event_data = []
    for i in range(1, 51):
        added = today - timedelta(days=random.randint(0, 30))
        event_data.append({
            'id': f"EVT-{1000+i}",
            'donor_id': 4,
            'source_type': 'Event Catering',
            'food_type': random.choice(['Cooked Meals', 'Bakery & Bread']),
            'quantity_kg': round(random.uniform(15.0, 80.0), 1),
            'date_added': added.strftime('%Y-%m-%d'),
            'expiry_date': (added + timedelta(days=random.randint(1, 2))).strftime('%Y-%m-%d'),
            'location': random.choice(events),
            'status': random.choice(['Available', 'Donated', 'Discarded'])
        })
    pd.DataFrame(event_data).to_csv('data/event_waste.csv', index=False)

    print("All 4 sector CSV files have been initialized successfully in /data!")

if __name__ == '__main__':
    generate_csv_files()