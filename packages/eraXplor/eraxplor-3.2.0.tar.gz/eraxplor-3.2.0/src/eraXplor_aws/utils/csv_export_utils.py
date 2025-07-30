"""Module for exporting AWS cost data to CSV format."""

import csv
from typing import Any, Dict, List


def csv_export(
    results: List[Dict[str, Any]],
    filename: str
    ) -> None:
    """Exports AWS cost data to a CSV file with standardized formatting.

    Takes the output from monthly_account_cost_export() _(i.e. depends handle by main)_
    and writes it to a CSV file with consistent column headers and proper formatting.
    The CSV will contain the time period, Account/Service/Purchase_type/Usage_type,
    and associated costs.

    Args:
        fetch_monthly_account_cost_usage (list): List of cost data dictionaries as returned
            by monthly_account_cost_export(). Each dictionary should contain:
            - time_period (dict): With 'Start' and 'End' keys
            - ID : AWS account ID, service name, purchase type name, usage type name.
            - GROUPBY_FILTER (str): Grouping filter used in the query, e.g., 'Account', 'Service', etc.
            - COST (float): The cost associated with the ID for the given time period.
            
        filename (str, optional): Output filename for the CSV. Defaults to 'cost_report.csv'.

    Returns:
        None: Writes directly to file but doesn't return any value.
    """
    # Create a CSV file with write mode
    with open(filename, mode="w", newline="", encoding="utf-8") as _csvfile:
        writer = csv.writer(_csvfile)
        writer.writerow(
            [
                "Start Date",
                "End Date",
                "ID",
                "GROUPBY_FILTER",
                "Cost",
            ]
        )
        for _row in results:
            time_period = _row["TIME_PERIOD"]
            ID = _row.get("ID")
            groupby = _row.get("GROUPBY_FILTER")
            cost = _row.get("COST")
            writer.writerow([time_period["Start"], time_period["End"], ID, groupby, cost])
    print(f"\n✅ Data exported to {filename}")
    
