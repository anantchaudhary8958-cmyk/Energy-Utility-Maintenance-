"""
validation.py
Validation rules and input sanitization for utility records.
Ensures data integrity before saving to the SQLite database.
"""

from typing import Any, Dict, List, Optional, Tuple
from database import MONTH_NAMES, check_duplicate_record


def validate_record_input(
    data: Dict[str, Any],
    exclude_id: Optional[int] = None,
    allow_duplicate: bool = False
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validate and clean input fields for a utility record.

    Returns:
        (is_valid, error_list, cleaned_dict)
    """
    errors: List[str] = []
    cleaned: Dict[str, Any] = {}

    # 1. Year validation
    try:
        year = int(data.get("year", 0))
        if year < 2000 or year > 2100:
            errors.append("Year must be between 2000 and 2100.")
        else:
            cleaned["year"] = year
    except (ValueError, TypeError):
        errors.append("Year must be a valid integer.")

    # 2. Month validation
    month = str(data.get("month", "")).strip()
    if month not in MONTH_NAMES:
        errors.append(f"Month must be one of: {', '.join(MONTH_NAMES)}.")
    else:
        cleaned["month"] = month

    # 3. Utility System validation
    system = str(data.get("utility_system", "")).strip()
    if not system:
        errors.append("Utility System is required.")
    else:
        cleaned["utility_system"] = system

    # 4. Numeric fields validation
    numeric_fields = [
        ("total_energy_kwh", "Total Energy Consumption (kWh)", 0.0, 100000000.0),
        ("energy_per_unit_kwh", "Energy Consumption per Unit (kWh)", 0.0, 10000.0),
        ("downtime_hours", "Utility Downtime (Hours)", 0.0, 744.0),  # Max hours in a month is 744
        ("energy_cost_per_unit", "Energy Cost per Unit Produced", 0.0, 100000.0),
        ("peak_demand_kw", "Peak Energy Demand (kW)", 0.0, 1000000.0),
        ("equipment_availability", "Utility Equipment Availability", 0.0, 100.0),
        ("energy_efficiency_ratio", "Energy Efficiency Ratio", 0.0, 10.0),
        ("water_per_unit_liters", "Water Consumption per Unit Produced (Liters)", 0.0, 100000.0),
        ("energy_loss_pct", "Energy Loss / Waste", 0.0, 100.0),
        ("maintenance_cost", "Maintenance Cost", 0.0, 100000000.0),
    ]

    for key, label, min_val, max_val in numeric_fields:
        val = data.get(key)
        if val is None or str(val).strip() == "":
            errors.append(f"{label} is required.")
            continue
        try:
            num = float(val)
            if num < min_val:
                errors.append(f"{label} cannot be negative (min {min_val}).")
            elif num > max_val:
                errors.append(f"{label} exceeds realistic limit ({max_val}).")
            else:
                # Normalize percentages: if user entered > 1.0 (e.g. 95%), convert to 0-1 decimal
                if key in ("equipment_availability", "energy_loss_pct"):
                    if num > 1.0:
                        num = round(num / 100.0, 4)
                    else:
                        num = round(num, 4)
                cleaned[key] = num
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid number.")

    # 5. Duplicate period check
    if not allow_duplicate and "year" in cleaned and "month" in cleaned and "utility_system" in cleaned:
        if check_duplicate_record(cleaned["year"], cleaned["month"], cleaned["utility_system"], exclude_id=exclude_id):
            errors.append(
                f"A record for {cleaned['utility_system']} in {cleaned['month']} {cleaned['year']} already exists. "
                "Update the existing record or choose a different month/year."
            )

    cleaned["notes"] = str(data.get("notes", "")).strip()

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned
