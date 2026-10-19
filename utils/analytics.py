import pandas as pd
from utils.calculations import calculate_co2_avoided

def process_food_analytics(df: pd.DataFrame, emission_factor: float = 2.5):
    """Executes Pandas analytical queries on food surplus records."""
    if df.empty:
        return {
            "total_surplus_kg": 0, "total_donated_kg": 0, "total_discarded_kg": 0,
            "donation_rate_pct": 0, "waste_rate_pct": 0, "most_wasted_category": "N/A",
            "highest_waste_location": "N/A", "co2_avoided_kg": 0
        }

    total_surplus = float(df['quantity_kg'].sum())
    donated_df = df[df['status'] == 'Donated']
    discarded_df = df[df['status'] == 'Discarded']
    
    total_donated = float(donated_df['quantity_kg'].sum())
    total_discarded = float(discarded_df['quantity_kg'].sum())
    
    donation_rate = (total_donated / total_surplus * 100) if total_surplus > 0 else 0
    waste_rate = (total_discarded / total_surplus * 100) if total_surplus > 0 else 0

    # Most wasted food category
    cat_waste = discarded_df.groupby('food_type')['quantity_kg'].sum()
    most_wasted_cat = str(cat_waste.idxmax()) if not cat_waste.empty else "N/A"

    # Location with highest food surplus
    loc_waste = df.groupby('location')['quantity_kg'].sum()
    highest_waste_loc = str(loc_waste.idxmax()) if not loc_waste.empty else "N/A"

    co2_avoided = calculate_co2_avoided(total_donated, emission_factor)

    return {
        "total_surplus_kg": round(total_surplus, 1),
        "total_donated_kg": round(total_donated, 1),
        "total_discarded_kg": round(total_discarded, 1),
        "donation_rate_pct": round(donation_rate, 1),
        "waste_rate_pct": round(waste_rate, 1),
        "most_wasted_category": most_wasted_cat,
        "highest_waste_location": highest_waste_loc,
        "co2_avoided_kg": co2_avoided
    }