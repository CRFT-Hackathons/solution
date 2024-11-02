# api.PlayControllerApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**play_round**](PlayControllerApi.md#play_round) | **POST** /api/v1/play/round | Play a round
[**start_session**](PlayControllerApi.md#start_session) | **POST** /api/v1/session/start | Start a new session
[**stop_session**](PlayControllerApi.md#stop_session) | **POST** /api/v1/session/end | End the current session


# **play_round**
> DayResponse play_round(api_key, session_id, day_request)

Play a round

Play a round for the current session

### Example


```python
import api
from api.models.day_request import DayRequest
from api.models.day_response import DayResponse
from api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = api.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = api.PlayControllerApi(api_client)
    api_key = 'api_key_example' # str | 
    session_id = 'session_id_example' # str | 
    day_request = api.DayRequest() # DayRequest | 

    try:
        # Play a round
        api_response = api_instance.play_round(api_key, session_id, day_request)
        print("The response of PlayControllerApi->play_round:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PlayControllerApi->play_round: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key** | **str**|  | 
 **session_id** | **str**|  | 
 **day_request** | [**DayRequest**](DayRequest.md)|  | 

### Return type

[**DayResponse**](DayResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**409** | Conflict |  -  |
**500** | Internal Server Error |  -  |
**400** | Invalid data provided |  -  |
**404** | No active session found for this team |  -  |
**200** | Data was posted successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_session**
> str start_session(api_key)

Start a new session

Start a new session for the given API key

### Example


```python
import api
from api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = api.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = api.PlayControllerApi(api_client)
    api_key = 'api_key_example' # str | 

    try:
        # Start a new session
        api_response = api_instance.start_session(api_key)
        print("The response of PlayControllerApi->start_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PlayControllerApi->start_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**409** | An active session already exists for this team |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**200** | Session was initialized successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_session**
> DayResponse stop_session(api_key)

End the current session

End the current session for the given API key

### Example


```python
import api
from api.models.day_response import DayResponse
from api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = api.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = api.PlayControllerApi(api_client)
    api_key = 'api_key_example' # str | 

    try:
        # End the current session
        api_response = api_instance.stop_session(api_key)
        print("The response of PlayControllerApi->stop_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PlayControllerApi->stop_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_key** | **str**|  | 

### Return type

[**DayResponse**](DayResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**409** | Conflict |  -  |
**500** | Internal Server Error |  -  |
**400** | Bad Request |  -  |
**404** | No active session found for this team |  -  |
**200** | Session was ended successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

