# Penalty

Penalty generated as a result of running the day / round

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**day** | **int** | The day when the penalty was issued | [optional] 
**type** | **str** | The type of the penalty | [optional] 
**message** | **str** | The message explaining the penalty | [optional] 
**cost** | **float** | The applied cost of the penalty | [optional] 
**co2** | **float** | The applied co2 of the penalty | [optional] 

## Example

```python
from api.models.penalty import Penalty

# TODO update the JSON string below
json = "{}"
# create an instance of Penalty from a JSON string
penalty_instance = Penalty.from_json(json)
# print the JSON string representation of the object
print(Penalty.to_json())

# convert the object into a dict
penalty_dict = penalty_instance.to_dict()
# create an instance of Penalty from a dict
penalty_from_dict = Penalty.from_dict(penalty_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


