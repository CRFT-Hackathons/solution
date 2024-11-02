from queue import PriorityQueue
import pandas as pd

import api
import api.models.movement
from api.rest import ApiException
import api.models
import logging

logging.basicConfig(
    filename="stats.log",
    filemode="a",
    format="%(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


def calculate_priority_score(demand, current_day, w1=1, w2=0.005, w3=1):
    # Urgency Score: Inverse of days until end_delivery_day
    days_until_end = demand.end_day - current_day + 1
    urgency_score = 1 / days_until_end if days_until_end > 0 else 0

    # Quantity Score: Proportional to the quantity
    quantity_score = demand.amount

    # Lead Time Score: Inverse of lead time
    lead_time = demand.end_day - demand.start_day + 1
    lead_time_score = 1 / lead_time if lead_time > 0 else 0

    # Calculate the total Priority Score
    priority_score = w1 * urgency_score + w2 * quantity_score + w3 * lead_time_score

    return priority_score


config = api.Configuration(
    host="http://localhost:8080", api_key="7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"
)

# Load the data
connections = pd.read_csv("resources/connections.csv", engine="pyarrow", sep=";")
customers = pd.read_csv("resources/customers.csv", engine="pyarrow", sep=";")
demands = pd.read_csv("resources/demands.csv", engine="pyarrow", sep=";")
refineries = pd.read_csv("resources/refineries.csv", engine="pyarrow", sep=";")
tanks = pd.read_csv("resources/tanks.csv", engine="pyarrow", sep=";")

sorted_connections = connections[connections["connection_type"] == "TRUCK"].sort_values(
    "distance"
)

mid_index = sorted_connections.shape[0] // 2

tier1 = sorted_connections.iloc[mid_index:][["id"]]
tier2 = sorted_connections.iloc[:mid_index][["id"]]

shortest_distances = (
    sorted_connections[sorted_connections["id"].isin(tier2["id"])]
    .groupby("to_id")
    .apply(lambda x: x.nsmallest(1, "distance"))
    .reset_index(drop=True)
)

scheduler = PriorityQueue()

# List for movements
movements = [[] for i in range(42)]

# Rename the column "initial_stock" to "stock"
refineries = refineries.rename(columns={"initial_stock": "stock"})
tanks = tanks.rename(columns={"initial_stock": "stock"})

with api.ApiClient(config) as api_client:
    client = api.PlayControllerApi(api_client)

    try:
        session_id = client.start_session(config.api_key)
        day_0 = client.play_round(
            config.api_key, session_id, api.models.DayRequest(day=0, movements=[])
        )

        for demand in day_0.demand:
            priority_score = calculate_priority_score(demand, 0)
            scheduler.put((-priority_score, demand))

        for current_day in range(1, 42):
            logging.info(f"DAY {current_day}")
            # ---- DAY INITIALIZATION ----
            # 1. Update stocks from finalized movements
            for movement in movements[current_day]:
                connection_id = movement.connection_id
                amount = movement.amount

                # Fetch connection details
                connection = connections[connections["id"] == connection_id].iloc[0]
                from_id, to_id = connection["from_id"], connection["to_id"]

                # Update stocks at the destination
                if to_id in tanks["id"].values:
                    tanks.loc[tanks["id"] == to_id, "stock"] += amount
                elif to_id in customers["id"].values:
                    # Any stock update logic for customer-specific handling here
                    pass
            movements[current_day] = []

            # 2. Produce stock in refineries
            refineries["stock"] += refineries["production"]

            # ---- SCHEDULER EXECUTION ----
            # Process demands in the scheduler
            while not scheduler.empty():
                _, demand = scheduler.get()

                customer_id = demand.customer_id
                quantity_needed = demand.amount

                # Find the best available tank for this customer
                available_tanks = shortest_distances[
                    shortest_distances["to_id"] == customer_id
                ]

                if available_tanks.empty:
                    continue  # No tank available for this customer

                best_tank_info = available_tanks.iloc[0]
                best_tank_id = best_tank_info["from_id"]
                best_tank = tanks[tanks["id"] == best_tank_id].iloc[0]

                # Check if tank has enough stock and capacity
                available_stock = best_tank["stock"]
                if available_stock >= quantity_needed:
                    # Full quantity can be moved
                    tanks.loc[tanks["id"] == best_tank_id, "stock"] -= quantity_needed
                    if current_day + best_tank_info["lead_time_days"] < len(movements):
                        movements[
                            current_day + best_tank_info["lead_time_days"]
                        ].append(
                            api.models.Movement(
                                connectionId=best_tank_info["id"],
                                amount=quantity_needed,
                            )
                        )
                else:
                    # Partial quantity is moved due to stock or capacity limits
                    max_quantity = min(available_stock, best_tank["max_output"])
                    tanks.loc[tanks["id"] == best_tank_id, "stock"] -= max_quantity
                    movements[current_day + best_tank_info["lead_time_days"]].append(
                        api.models.Movement(
                            connectionId=best_tank_info["id"], amount=max_quantity
                        )
                    )
                    # Requeue remaining demand with updated quantity
                    remaining_quantity = quantity_needed - max_quantity
                    scheduler.put(
                        (
                            -calculate_priority_score(demand, current_day),
                            {**demand, "quantity": remaining_quantity},
                        )
                    )

            # ---- END OF DAY UPDATES ----
            # Fetch and add new demands to the scheduler
            round_res = client.play_round(
                config.api_key,
                session_id,
                api.models.DayRequest(
                    day=current_day,
                    movements=movements[current_day],
                ),
            )
            logging.info(round_res.penalties)
            new_demands = round_res.demand
            for new_demand in new_demands:
                priority_score = calculate_priority_score(new_demand, current_day)
                scheduler.put((-priority_score, new_demand))

    except ApiException as e:
        logging.info("Exception when calling PlayControllerApi->play_round: %s\n" % e)
        res = client.stop_session(config.api_key)
        logging.info(res)
