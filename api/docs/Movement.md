# Movement

The proposed movement of amount units, using the connection with the given ID

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_id** | **str** | The ID of the connection to be used | [optional] 
**amount** | **int** | The number of units to be moved | [optional] 

## Example

```python
from api.models.movement import Movement

# TODO update the JSON string below
json = "{}"
# create an instance of Movement from a JSON string
movement_instance = Movement.from_json(json)
# print the JSON string representation of the object
print(Movement.to_json())

# convert the object into a dict
movement_dict = movement_instance.to_dict()
# create an instance of Movement from a dict
movement_from_dict = Movement.from_dict(movement_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


