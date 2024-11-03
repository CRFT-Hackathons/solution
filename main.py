from queue import PriorityQueue
import uuid
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
connections["blocked"] = False
customers = pd.read_csv("resources/customers.csv", engine="pyarrow", sep=";")
# demands = pd.read_csv("resources/demands.csv", engine="pyarrow", sep=";")
refineries = pd.read_csv("resources/refineries.csv", engine="pyarrow", sep=";")
tanks = pd.read_csv("resources/tanks.csv", engine="pyarrow", sep=";")

sorted_connections = connections[connections["connection_type"] == "TRUCK"].sort_values(
    "distance"
)

mid_index = sorted_connections.shape[0] // 2

tier1 = sorted_connections.iloc[mid_index:][["id"]]
tier2 = sorted_connections.iloc[:mid_index][["id"]]

# luam toate conexiunile de tip truck, le grupam dupa to_id, care este sigur un customer,
# si din fiecare grup luam conexiunea cu distanta minima; asta e lista t2-t3, t2 = t2_t3["from_id"]

# TODO sort by distance and volume
t2_t3_connections = (
    connections[connections["connection_type"] == "TRUCK"]
    .sort_values("distance")
    .groupby("to_id")
    .agg(
        {
            "distance": "min",
            "from_id": "first",
            "max_capacity": "first",
            "lead_time_days": "first",
            "id": "first",
        }
    )
    .reset_index()
)

t2 = t2_t3_connections["from_id"]
t3 = t2_t3_connections["to_id"]

t1_t2_connections = connections[
    (connections["connection_type"] == "PIPELINE")
    & (connections["to_id"].isin(t2))
    & (~connections["from_id"].isin(t3))
]
t1 = t1_t2_connections["from_id"]

t0 = refineries["id"]
t0_t1_connections = connections[
    (connections["from_id"].isin(t0)) & (connections["to_id"].isin(t1))
]

dispatchers_connections = (
    sorted_connections[sorted_connections["id"].isin(tier2["id"])]
    .groupby("to_id")
    .agg({"distance": "min", "from_id": "first"})
    .reset_index(drop=True)
)

scheduler = PriorityQueue()

# List for movements
ending_movements = [[] for i in range(42)]

# Rename the column "initial_stock" to "stock"
refineries = refineries.rename(columns={"initial_stock": "stock"})
tanks = tanks.rename(columns={"initial_stock": "stock"})

demands_amounts = pd.DataFrame({}, columns=["demand_id", "delta"])

with api.ApiClient(config) as api_client:
    client = api.PlayControllerApi(api_client)

    try:
        session_id = client.start_session(config.api_key)
        day_0 = client.play_round(
            config.api_key, session_id, api.models.DayRequest(day=0, movements=[])
        )

        for demand in day_0.demand:
            demand.id = str(uuid.uuid4())
            priority_score = calculate_priority_score(demand, 0)
            scheduler.put((-priority_score, demand))
            demands_amounts.loc[len(demands_amounts.index)] = {
                "demand_id": demand.id,
                "delta": demand.amount,
            }

        for current_day in range(1, 42):
            logging.info(f"DAY {current_day}")
            print(f"DAY {current_day}")
            # ---- DAY INITIALIZATION ----
            # 1. Update stocks from finalized movements
            for movement in ending_movements[current_day]:
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
                connections.loc[connections["id"] == connection_id, "blocked"] = False

            # 2. Produce stock in refineries
            refineries["stock"] += refineries["production"]

            movements: list[api.models.Movement] = []

            # ---- SCHEDULER EXECUTION ----
            # Process demands in the scheduler
            while not scheduler.empty():
                _, demand = scheduler.get()
                demand_amount = demands_amounts[
                    demands_amounts["demand_id"] == demand.id
                ].iloc[0]

                upstream_connection = connections[
                    (connections["to_id"] == demand.customer_id)
                    & (connections["connection_type"] == "TRUCK")
                    & (~connections["blocked"])
                ]
                if upstream_connection.empty:
                    continue

                upstream_connection = upstream_connection.iloc[0]
                t2_id = upstream_connection["from_id"]
                t2_tank = tanks[tanks["id"] == t2_id].iloc[0]
                t3_customer = customers[
                    customers["id"] == upstream_connection["to_id"]
                ].iloc[0]

                t2_stock = t2_tank["stock"]
                max_delivery = min(
                    upstream_connection["max_capacity"],
                    t2_tank["max_output"],
                    t3_customer["max_input"],
                    demand_amount["delta"],
                )

                if t2_stock >= max_delivery > 0 and (
                    demand.end_day
                    >= (current_day + upstream_connection["lead_time_days"])
                    > demand.start_day
                ):
                    print(f"PIPING {max_delivery} into {upstream_connection["id"]}")
                    movements.append(
                        api.models.Movement(
                            connectionId=upstream_connection["id"],
                            amount=int(max_delivery),
                        )
                    )
                    connections.loc[
                        connections["id"] == upstream_connection["id"], "blocked"
                    ] = True
                    demands_amounts.loc[
                        demands_amounts["demand_id"] == demand.id, "delta"
                    ] -= int(max_delivery)

                    # scheduler.put(
                    #     (
                    #         -1 * calculate_priority_score(demand, current_day),
                    #         api.models.Demand(
                    #             id=demand.id,
                    #             customerId=demand.customer_id,
                    #             amount=int(
                    #                 demands_amounts.loc[
                    #                     demands_amounts["demand_id"] == demand.id,
                    #                     "delta",
                    #                 ]
                    #             ),
                    #             postDay=demand.post_day,
                    #             startDay=demand.start_day,
                    #             endDay=demand.end_day,
                    #         ),
                    #         # ),
                    #     )
                    # )

            t1_final = tanks[tanks["id"].isin(t1)].copy()
            t2_final = tanks[tanks["id"].isin(t2)].copy()

            # schedule movements for filling t2
            tanks["stock_percentage"] = tanks["stock"] / tanks["capacity"] * 100
            for idx, tank in (
                tanks[tanks["id"].isin(t1)].sort_values("stock_percentage").iterrows()
            ):
                downstream_connections = t1_t2_connections[
                    (t1_t2_connections["from_id"] == tank["id"])
                    & (~t1_t2_connections["blocked"])
                ]
                t2_tanks = t2_final[
                    t2_final["id"].isin(downstream_connections["to_id"])
                ]
                t2_max_deliveries = min(
                    downstream_connections["max_capacity"].values[0],
                    t2_tanks["max_output"].values[0],
                    t2_tanks["capacity"].values[0] - t2_tanks["stock"].values[0],
                )
                downstream_total = t2_max_deliveries
                downstream_weights = pd.DataFrame(
                    {
                        "weight": t2_max_deliveries / downstream_total,
                        "max_delivery": t2_max_deliveries,
                    },
                    index=downstream_connections.index,
                )

                downstream_connections = downstream_connections.reset_index()
                downstream_connections = downstream_connections.merge(
                    downstream_weights, left_index=True, right_index=True
                )
                for idx, data in downstream_connections.iterrows():
                    amount = min(data["weight"] * tank["stock"], data["max_delivery"])
                    movements.append(
                        api.models.Movement(connectionId=data["id"], amount=amount)
                    )
                    t1_final.loc[t1_final["id"] == data["from_id"], "stock"] -= amount
                    t2_final.loc[t2_final["id"] == data["to_id"], "stock"] += amount
                    connections.loc[connections["id"] == data["id"], "blocked"] = True

            # schedule movements for filling t1
            for idx, tank in (
                tanks[tanks["id"].isin(t0)].sort_values("stock_percentage").iterrows()
            ):
                downstream_connections = t0_t1_connections[
                    (t0_t1_connections["from_id"] == tank["id"])
                    & (~t0_t1_connections["blocked"])
                ]
                t1_tanks = t1_final[
                    t1_final["id"].isin(downstream_connections["to_id"])
                ]
                t1_max_deliveries = min(
                    downstream_connections["max_capacity"].values[0],
                    t1_tanks["max_output"].values[0],
                    t1_tanks["capacity"].values[0] - t1_tanks["stock"].values[0],
                )
                downstream_total = t1_max_deliveries
                downstream_weights = pd.DataFrame(
                    {
                        "weight": t1_max_deliveries / downstream_total,
                        "max_delivery": t1_max_deliveries,
                    },
                    index=downstream_connections.index,
                )

                downstream_data = downstream_connections.insert(
                    {"weight": downstream_weights, "max_delivery": t1_max_deliveries}
                )
                for data in downstream_connections.merge(downstream_weights):
                    amount = data["max_delivery"]
                    # amount = min(data["weight"] * tank["stock"], data["max_delivery"])
                    movements.append(
                        api.models.Movement(connectionId=data["id"], amount=amount)
                    )
                    refineries["stock"] -= amount
                    t1_final[data["to_id"]] += amount
                    connections.loc[connections["id"] == data["id"], "blocked"] = True

            for movement in movements:
                # TODO verifica cand mai multe transporturi in desfasurare se acumuleaza si dau overflow
                ending_movements[
                    current_day
                    + connections[connections["id"] == movement.connection_id].iloc[0][
                        "lead_time_days"
                    ]
                ].append(movement)

            # ---- END OF DAY UPDATES ----
            # Fetch and add new demands to the scheduler
            round_res = client.play_round(
                config.api_key,
                session_id,
                api.models.DayRequest(
                    day=current_day,
                    movements=movements,
                ),
            )
            logging.info(round_res.penalties)
            logging.info(round_res.total_kpis)
            new_demands = round_res.demand
            for new_demand in new_demands:
                new_demand.id = str(uuid.uuid4())
                priority_score = calculate_priority_score(new_demand, current_day)
                scheduler.put((-priority_score, new_demand))
                demands_amounts.loc[len(demands_amounts.index)] = {
                    "demand_id": new_demand.id,
                    "delta": new_demand.amount,
                }

    except ApiException as e:
        logging.info("Exception when calling PlayControllerApi->play_round: %s\n" % e)
        res = client.stop_session(config.api_key)
        logging.info(res)
