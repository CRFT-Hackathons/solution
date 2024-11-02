# Demand

The demand / order of a customer

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer_id** | **str** | The ID of the customer | [optional] 
**amount** | **int** | The amount requested | [optional] 
**post_day** | **int** | The day when the demand was posted | [optional] 
**start_day** | **int** | Delivery should happen no earlier than this day | [optional] 
**end_day** | **int** | Delivery should happen no later than this day | [optional] 

## Example

```python
from api.models.demand import Demand

# TODO update the JSON string below
json = "{}"
# create an instance of Demand from a JSON string
demand_instance = Demand.from_json(json)
# print the JSON string representation of the object
print(Demand.to_json())

# convert the object into a dict
demand_dict = demand_instance.to_dict()
# create an instance of Demand from a dict
demand_from_dict = Demand.from_dict(demand_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


