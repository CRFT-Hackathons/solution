# DayResponse

The success response to a round

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**round** | **int** | The current day / round | [optional] 
**demand** | [**List[Demand]**](Demand.md) | The list of posted customer demands (orders) on the current day. It can be empty or missing. | [optional] 
**penalties** | [**List[Penalty]**](Penalty.md) | The list of generated penalties as a result of running the day / round. Penalties can be also generated for the wrong state of the network. | [optional] 
**delta_kpis** | [**Kpis**](Kpis.md) |  | [optional] 
**total_kpis** | [**Kpis**](Kpis.md) |  | [optional] 

## Example

```python
from api.models.day_response import DayResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DayResponse from a JSON string
day_response_instance = DayResponse.from_json(json)
# print the JSON string representation of the object
print(DayResponse.to_json())

# convert the object into a dict
day_response_dict = day_response_instance.to_dict()
# create an instance of DayResponse from a dict
day_response_from_dict = DayResponse.from_dict(day_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


