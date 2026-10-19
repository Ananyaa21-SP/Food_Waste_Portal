def calculate_co2_avoided(donated_quantity_kg: float, emission_factor: float = 2.5) -> float:
    """
    Calculates estimated greenhouse gas emission reductions in kg CO2e.
    Formula: CO2e Avoided (kg) = Diverted Food (kg) * Emission Factor
    """
    if donated_quantity_kg < 0 or emission_factor < 0:
        return 0.0
    return round(donated_quantity_kg * emission_factor, 2)

def calculate_equivalencies(co2_kg: float) -> dict:
    """Computes real-world environmental equivalencies."""
    return {
        "miles_driven_saved": round(co2_kg * 2.48, 1),
        "tree_seedlings_grown": int(co2_kg // 60)
    }