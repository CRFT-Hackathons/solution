# DayRequest

The request to play a round

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**day** | **int** | The current day | [optional] 
**movements** | [**List[Movement]**](Movement.md) | The list of proposed movements | [optional] 

## Example

```python
from api.models.day_request import DayRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DayRequest from a JSON string
day_request_instance = DayRequest.from_json(json)
# print the JSON string representation of the object
print(DayRequest.to_json())

# convert the object into a dict
day_request_dict = day_request_instance.to_dict()
# create an instance of DayRequest from a dict
day_request_from_dict = DayRequest.from_dict(day_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


