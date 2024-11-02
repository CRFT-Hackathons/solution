import pandas as pd
from pprint import pprint

import api
from api.rest import ApiException
import api.models

config = api.Configuration(
    host="http://localhost:8080", api_key="7bcd6334-bc2e-4cbf-b9d4-61cb9e868869"
)

# Load the data
connections = pd.read_csv("resources/connections.csv", engine="pyarrow")
customers = pd.read_csv("resources/customers.csv", engine="pyarrow")
demands = pd.read_csv("resources/demands.csv", engine="pyarrow")
refineries = pd.read_csv("resources/refineries.csv", engine="pyarrow")
tanks = pd.read_csv("resources/tanks.csv", engine="pyarrow")


with api.ApiClient(config) as api_client:
    client = api.PlayControllerApi(api_client)

    try:
        session_id = client.start_session(config.api_key)
        day_0 = client.play_round(
            config.api_key, session_id, api.models.DayRequest(day=0, movements=[])
        )
        # WRITE CODE
        pprint(day_0.model_dump())

        res = client.stop_session(config.api_key)
        pprint(res)
    except ApiException as e:
        print("Exception when calling PlayControllerApi->play_round: %s\n" % e)
