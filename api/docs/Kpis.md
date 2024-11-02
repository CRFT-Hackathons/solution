# Kpis

The KPIs that are the metrics of the simulation

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**day** | **int** | The reference day | [optional] 
**cost** | **float** | the cost | [optional] 
**co2** | **float** | the co2 value | [optional] 

## Example

```python
from api.models.kpis import Kpis

# TODO update the JSON string below
json = "{}"
# create an instance of Kpis from a JSON string
kpis_instance = Kpis.from_json(json)
# print the JSON string representation of the object
print(Kpis.to_json())

# convert the object into a dict
kpis_dict = kpis_instance.to_dict()
# create an instance of Kpis from a dict
kpis_from_dict = Kpis.from_dict(kpis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


