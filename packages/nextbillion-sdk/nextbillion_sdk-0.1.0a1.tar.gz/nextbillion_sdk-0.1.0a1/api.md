# Fleetify

## Routes

Types:

```python
from nextbillion_sdk.types.fleetify import Routing, RouteCreateResponse, RouteRedispatchResponse
```

Methods:

- <code title="post /fleetify/routes">client.fleetify.routes.<a href="./src/nextbillion_sdk/resources/fleetify/routes/routes.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/fleetify/route_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/route_create_response.py">RouteCreateResponse</a></code>
- <code title="post /fleetify/routes/{routeID}/redispatch">client.fleetify.routes.<a href="./src/nextbillion_sdk/resources/fleetify/routes/routes.py">redispatch</a>(route_id, \*\*<a href="src/nextbillion_sdk/types/fleetify/route_redispatch_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/route_redispatch_response.py">RouteRedispatchResponse</a></code>

### Steps

Types:

```python
from nextbillion_sdk.types.fleetify.routes import (
    DocumentSubmission,
    RouteStepCompletionMode,
    RouteStepGeofenceConfig,
    RouteStepsRequest,
    RouteStepsResponse,
    StepCreateResponse,
    StepUpdateResponse,
    StepDeleteResponse,
)
```

Methods:

- <code title="post /fleetify/routes/{routeID}/steps">client.fleetify.routes.steps.<a href="./src/nextbillion_sdk/resources/fleetify/routes/steps.py">create</a>(route_id, \*\*<a href="src/nextbillion_sdk/types/fleetify/routes/step_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/routes/step_create_response.py">StepCreateResponse</a></code>
- <code title="put /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillion_sdk/resources/fleetify/routes/steps.py">update</a>(step_id, \*, route_id, \*\*<a href="src/nextbillion_sdk/types/fleetify/routes/step_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/routes/step_update_response.py">StepUpdateResponse</a></code>
- <code title="delete /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillion_sdk/resources/fleetify/routes/steps.py">delete</a>(step_id, \*, route_id, \*\*<a href="src/nextbillion_sdk/types/fleetify/routes/step_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/routes/step_delete_response.py">StepDeleteResponse</a></code>
- <code title="patch /fleetify/routes/{routeID}/steps/{stepID}">client.fleetify.routes.steps.<a href="./src/nextbillion_sdk/resources/fleetify/routes/steps.py">complete</a>(step_id, \*, route_id, \*\*<a href="src/nextbillion_sdk/types/fleetify/routes/step_complete_params.py">params</a>) -> None</code>

## DocumentTemplates

Types:

```python
from nextbillion_sdk.types.fleetify import (
    DocumentTemplateContentRequest,
    DocumentTemplateContentResponse,
    DocumentTemplateCreateResponse,
    DocumentTemplateRetrieveResponse,
    DocumentTemplateUpdateResponse,
    DocumentTemplateListResponse,
    DocumentTemplateDeleteResponse,
)
```

Methods:

- <code title="post /fleetify/document_templates">client.fleetify.document_templates.<a href="./src/nextbillion_sdk/resources/fleetify/document_templates.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/fleetify/document_template_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/document_template_create_response.py">DocumentTemplateCreateResponse</a></code>
- <code title="get /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillion_sdk/resources/fleetify/document_templates.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/fleetify/document_template_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/document_template_retrieve_response.py">DocumentTemplateRetrieveResponse</a></code>
- <code title="put /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillion_sdk/resources/fleetify/document_templates.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/fleetify/document_template_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/document_template_update_response.py">DocumentTemplateUpdateResponse</a></code>
- <code title="get /fleetify/document_templates">client.fleetify.document_templates.<a href="./src/nextbillion_sdk/resources/fleetify/document_templates.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/fleetify/document_template_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/document_template_list_response.py">DocumentTemplateListResponse</a></code>
- <code title="delete /fleetify/document_templates/{id}">client.fleetify.document_templates.<a href="./src/nextbillion_sdk/resources/fleetify/document_templates.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/fleetify/document_template_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/fleetify/document_template_delete_response.py">DocumentTemplateDeleteResponse</a></code>

# Skynet

Types:

```python
from nextbillion_sdk.types import SkynetSubscribeResponse
```

Methods:

- <code title="post /skynet/subscribe">client.skynet.<a href="./src/nextbillion_sdk/resources/skynet/skynet.py">subscribe</a>(\*\*<a href="src/nextbillion_sdk/types/skynet_subscribe_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet_subscribe_response.py">SkynetSubscribeResponse</a></code>

## Asset

Types:

```python
from nextbillion_sdk.types.skynet import (
    MetaData,
    SimpleResp,
    AssetCreateResponse,
    AssetRetrieveResponse,
    AssetRetrieveListResponse,
)
```

Methods:

- <code title="post /skynet/asset">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/asset_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset_create_response.py">AssetCreateResponse</a></code>
- <code title="get /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset_retrieve_response.py">AssetRetrieveResponse</a></code>
- <code title="put /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="delete /skynet/asset/{id}">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/asset/list">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">retrieve_list</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/asset_retrieve_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset_retrieve_list_response.py">AssetRetrieveListResponse</a></code>
- <code title="post /skynet/asset/{id}/track">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">track</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset_track_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="put /skynet/asset/{id}/attributes">client.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/asset/asset.py">update_attributes</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset_update_attributes_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>

### Event

Types:

```python
from nextbillion_sdk.types.skynet.asset import EventRetrieveListResponse
```

Methods:

- <code title="get /skynet/asset/{id}/event/list">client.skynet.asset.event.<a href="./src/nextbillion_sdk/resources/skynet/asset/event.py">retrieve_list</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset/event_retrieve_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset/event_retrieve_list_response.py">EventRetrieveListResponse</a></code>

### Location

Types:

```python
from nextbillion_sdk.types.skynet.asset import (
    TrackLocation,
    LocationRetrieveLastResponse,
    LocationRetrieveListResponse,
)
```

Methods:

- <code title="get /skynet/asset/{id}/location/last">client.skynet.asset.location.<a href="./src/nextbillion_sdk/resources/skynet/asset/location.py">retrieve_last</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset/location_retrieve_last_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset/location_retrieve_last_response.py">LocationRetrieveLastResponse</a></code>
- <code title="get /skynet/asset/{id}/location/list">client.skynet.asset.location.<a href="./src/nextbillion_sdk/resources/skynet/asset/location.py">retrieve_list</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/asset/location_retrieve_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/asset/location_retrieve_list_response.py">LocationRetrieveListResponse</a></code>

## Monitor

Types:

```python
from nextbillion_sdk.types.skynet import (
    Metadata,
    Monitor,
    Pagination,
    MonitorCreateResponse,
    MonitorRetrieveResponse,
    MonitorRetrieveListResponse,
)
```

Methods:

- <code title="post /skynet/monitor">client.skynet.monitor.<a href="./src/nextbillion_sdk/resources/skynet/monitor.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/monitor_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/monitor_create_response.py">MonitorCreateResponse</a></code>
- <code title="get /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillion_sdk/resources/skynet/monitor.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/monitor_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/monitor_retrieve_response.py">MonitorRetrieveResponse</a></code>
- <code title="put /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillion_sdk/resources/skynet/monitor.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/monitor_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="delete /skynet/monitor/{id}">client.skynet.monitor.<a href="./src/nextbillion_sdk/resources/skynet/monitor.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/monitor_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/monitor/list">client.skynet.monitor.<a href="./src/nextbillion_sdk/resources/skynet/monitor.py">retrieve_list</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/monitor_retrieve_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/monitor_retrieve_list_response.py">MonitorRetrieveListResponse</a></code>

## Trip

Types:

```python
from nextbillion_sdk.types.skynet import (
    Asset,
    TripStop,
    TripRetrieveResponse,
    TripRetrieveSummaryResponse,
    TripStartResponse,
)
```

Methods:

- <code title="get /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/trip_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/trip_retrieve_response.py">TripRetrieveResponse</a></code>
- <code title="put /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/trip_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="delete /skynet/trip/{id}">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/trip_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="post /skynet/trip/end">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">end</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/trip_end_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/trip/{id}/summary">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">retrieve_summary</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/trip_retrieve_summary_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/trip_retrieve_summary_response.py">TripRetrieveSummaryResponse</a></code>
- <code title="post /skynet/trip/start">client.skynet.trip.<a href="./src/nextbillion_sdk/resources/skynet/trip.py">start</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/trip_start_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/trip_start_response.py">TripStartResponse</a></code>

## NamespacedApikeys

Types:

```python
from nextbillion_sdk.types.skynet import (
    NamespacedApikeyDeleteNamespacedApikeysResponse,
    NamespacedApikeyNamespacedApikeysResponse,
)
```

Methods:

- <code title="delete /skynet/namespaced-apikeys">client.skynet.namespaced_apikeys.<a href="./src/nextbillion_sdk/resources/skynet/namespaced_apikeys.py">delete_namespaced_apikeys</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/namespaced_apikey_delete_namespaced_apikeys_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/namespaced_apikey_delete_namespaced_apikeys_response.py">NamespacedApikeyDeleteNamespacedApikeysResponse</a></code>
- <code title="post /skynet/namespaced-apikeys">client.skynet.namespaced_apikeys.<a href="./src/nextbillion_sdk/resources/skynet/namespaced_apikeys.py">namespaced_apikeys</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/namespaced_apikey_namespaced_apikeys_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/namespaced_apikey_namespaced_apikeys_response.py">NamespacedApikeyNamespacedApikeysResponse</a></code>

## Config

Types:

```python
from nextbillion_sdk.types.skynet import ConfigListResponse, ConfigTestwebhookResponse
```

Methods:

- <code title="put /skynet/config">client.skynet.config.<a href="./src/nextbillion_sdk/resources/skynet/config.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/config_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /skynet/config">client.skynet.config.<a href="./src/nextbillion_sdk/resources/skynet/config.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/config_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/config_list_response.py">ConfigListResponse</a></code>
- <code title="post /skynet/config/testwebhook">client.skynet.config.<a href="./src/nextbillion_sdk/resources/skynet/config.py">testwebhook</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/config_testwebhook_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/config_testwebhook_response.py">ConfigTestwebhookResponse</a></code>

## Search

Types:

```python
from nextbillion_sdk.types.skynet import SearchResponse
```

Methods:

- <code title="get /skynet/search/around">client.skynet.search.<a href="./src/nextbillion_sdk/resources/skynet/search/search.py">retrieve_around</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/search_retrieve_around_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/search_response.py">SearchResponse</a></code>
- <code title="get /skynet/search/bound">client.skynet.search.<a href="./src/nextbillion_sdk/resources/skynet/search/search.py">retrieve_bound</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/search_retrieve_bound_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/search_response.py">SearchResponse</a></code>

### Polygon

Methods:

- <code title="post /skynet/search/polygon">client.skynet.search.polygon.<a href="./src/nextbillion_sdk/resources/skynet/search/polygon.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/search/polygon_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/search_response.py">SearchResponse</a></code>
- <code title="get /skynet/search/polygon">client.skynet.search.polygon.<a href="./src/nextbillion_sdk/resources/skynet/search/polygon.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/skynet/search/polygon_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/search_response.py">SearchResponse</a></code>

## Skynet

### Asset

Methods:

- <code title="post /skynet/skynet/asset/{id}/bind">client.skynet.skynet.asset.<a href="./src/nextbillion_sdk/resources/skynet/skynet_/asset.py">bind</a>(id, \*\*<a href="src/nextbillion_sdk/types/skynet/skynet_/asset_bind_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>

# Geocode

Types:

```python
from nextbillion_sdk.types import (
    Access,
    Address,
    Categories,
    ContactObject,
    Contacts,
    MapView,
    Position,
    GeocodeRetrieveResponse,
    GeocodeBatchCreateResponse,
    GeocodeStructuredRetrieveResponse,
)
```

Methods:

- <code title="get /geocode">client.geocode.<a href="./src/nextbillion_sdk/resources/geocode.py">retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/geocode_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geocode_retrieve_response.py">GeocodeRetrieveResponse</a></code>
- <code title="post /geocode/batch">client.geocode.<a href="./src/nextbillion_sdk/resources/geocode.py">batch_create</a>(\*\*<a href="src/nextbillion_sdk/types/geocode_batch_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geocode_batch_create_response.py">GeocodeBatchCreateResponse</a></code>
- <code title="get /geocode/structured">client.geocode.<a href="./src/nextbillion_sdk/resources/geocode.py">structured_retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/geocode_structured_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geocode_structured_retrieve_response.py">GeocodeStructuredRetrieveResponse</a></code>

# Optimization

Types:

```python
from nextbillion_sdk.types import PostResponse, OptimizationComputeResponse
```

Methods:

- <code title="get /optimization/json">client.optimization.<a href="./src/nextbillion_sdk/resources/optimization/optimization.py">compute</a>(\*\*<a href="src/nextbillion_sdk/types/optimization_compute_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/optimization_compute_response.py">OptimizationComputeResponse</a></code>
- <code title="post /optimization/re_optimization">client.optimization.<a href="./src/nextbillion_sdk/resources/optimization/optimization.py">re_optimize</a>(\*\*<a href="src/nextbillion_sdk/types/optimization_re_optimize_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/post_response.py">PostResponse</a></code>

## DriverAssignment

Types:

```python
from nextbillion_sdk.types.optimization import Location, Vehicle, DriverAssignmentAssignResponse
```

Methods:

- <code title="post /optimization/driver-assignment/v1">client.optimization.driver_assignment.<a href="./src/nextbillion_sdk/resources/optimization/driver_assignment.py">assign</a>(\*\*<a href="src/nextbillion_sdk/types/optimization/driver_assignment_assign_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/optimization/driver_assignment_assign_response.py">DriverAssignmentAssignResponse</a></code>

## V2

Types:

```python
from nextbillion_sdk.types.optimization import Job, Shipment, V2RetrieveResultResponse
```

Methods:

- <code title="get /optimization/v2/result">client.optimization.v2.<a href="./src/nextbillion_sdk/resources/optimization/v2.py">retrieve_result</a>(\*\*<a href="src/nextbillion_sdk/types/optimization/v2_retrieve_result_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/optimization/v2_retrieve_result_response.py">V2RetrieveResultResponse</a></code>
- <code title="post /optimization/v2">client.optimization.v2.<a href="./src/nextbillion_sdk/resources/optimization/v2.py">submit</a>(\*\*<a href="src/nextbillion_sdk/types/optimization/v2_submit_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/post_response.py">PostResponse</a></code>

# Geofence

Types:

```python
from nextbillion_sdk.types import (
    Geofence,
    GeofenceEntityCreate,
    GeofenceCreateResponse,
    GeofenceRetrieveResponse,
    GeofenceListResponse,
    GeofenceContainsResponse,
)
```

Methods:

- <code title="post /geofence">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/geofence_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence_create_response.py">GeofenceCreateResponse</a></code>
- <code title="get /geofence/{id}">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/geofence_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence_retrieve_response.py">GeofenceRetrieveResponse</a></code>
- <code title="put /geofence/{id}">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/geofence_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /geofence/list">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/geofence_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence_list_response.py">GeofenceListResponse</a></code>
- <code title="delete /geofence/{id}">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/geofence_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /geofence/contain">client.geofence.<a href="./src/nextbillion_sdk/resources/geofence/geofence.py">contains</a>(\*\*<a href="src/nextbillion_sdk/types/geofence_contains_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence_contains_response.py">GeofenceContainsResponse</a></code>

## Console

Types:

```python
from nextbillion_sdk.types.geofence import (
    PolygonGeojson,
    ConsolePreviewResponse,
    ConsoleSearchResponse,
)
```

Methods:

- <code title="post /geofence/console/preview">client.geofence.console.<a href="./src/nextbillion_sdk/resources/geofence/console.py">preview</a>(\*\*<a href="src/nextbillion_sdk/types/geofence/console_preview_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence/console_preview_response.py">ConsolePreviewResponse</a></code>
- <code title="get /geofence/console/search">client.geofence.console.<a href="./src/nextbillion_sdk/resources/geofence/console.py">search</a>(\*\*<a href="src/nextbillion_sdk/types/geofence/console_search_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence/console_search_response.py">ConsoleSearchResponse</a></code>

## Batch

Types:

```python
from nextbillion_sdk.types.geofence import BatchCreateResponse, BatchQueryResponse
```

Methods:

- <code title="post /geofence/batch">client.geofence.batch.<a href="./src/nextbillion_sdk/resources/geofence/batch.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/geofence/batch_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="delete /geofence/batch">client.geofence.batch.<a href="./src/nextbillion_sdk/resources/geofence/batch.py">delete</a>(\*\*<a href="src/nextbillion_sdk/types/geofence/batch_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/skynet/simple_resp.py">SimpleResp</a></code>
- <code title="get /geofence/batch">client.geofence.batch.<a href="./src/nextbillion_sdk/resources/geofence/batch.py">query</a>(\*\*<a href="src/nextbillion_sdk/types/geofence/batch_query_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/geofence/batch_query_response.py">BatchQueryResponse</a></code>

# Discover

Types:

```python
from nextbillion_sdk.types import DiscoverListResponse
```

Methods:

- <code title="get /discover">client.discover.<a href="./src/nextbillion_sdk/resources/discover.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/discover_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/discover_list_response.py">DiscoverListResponse</a></code>

# Browse

Types:

```python
from nextbillion_sdk.types import BrowseSearchResponse
```

Methods:

- <code title="get /browse">client.browse.<a href="./src/nextbillion_sdk/resources/browse.py">search</a>(\*\*<a href="src/nextbillion_sdk/types/browse_search_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/browse_search_response.py">BrowseSearchResponse</a></code>

# Mdm

Types:

```python
from nextbillion_sdk.types import (
    MdmCreateDistanceMatrixResponse,
    MdmGetDistanceMatrixStatusResponse,
)
```

Methods:

- <code title="post /mdm/create">client.mdm.<a href="./src/nextbillion_sdk/resources/mdm.py">create_distance_matrix</a>(\*\*<a href="src/nextbillion_sdk/types/mdm_create_distance_matrix_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/mdm_create_distance_matrix_response.py">MdmCreateDistanceMatrixResponse</a></code>
- <code title="get /mdm/status">client.mdm.<a href="./src/nextbillion_sdk/resources/mdm.py">get_distance_matrix_status</a>(\*\*<a href="src/nextbillion_sdk/types/mdm_get_distance_matrix_status_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/mdm_get_distance_matrix_status_response.py">MdmGetDistanceMatrixStatusResponse</a></code>

# Isochrone

Types:

```python
from nextbillion_sdk.types import IsochroneComputeResponse
```

Methods:

- <code title="get /isochrone/json">client.isochrone.<a href="./src/nextbillion_sdk/resources/isochrone.py">compute</a>(\*\*<a href="src/nextbillion_sdk/types/isochrone_compute_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/isochrone_compute_response.py">IsochroneComputeResponse</a></code>

# Restrictions

Types:

```python
from nextbillion_sdk.types import (
    RichGroupDtoRequest,
    RichGroupDtoResponse,
    RestrictionListResponse,
    RestrictionDeleteResponse,
    RestrictionListPaginatedResponse,
)
```

Methods:

- <code title="post /restrictions/{restriction_type}">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">create</a>(restriction_type, \*\*<a href="src/nextbillion_sdk/types/restriction_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/rich_group_dto_response.py">RichGroupDtoResponse</a></code>
- <code title="get /restrictions/{id}">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">retrieve</a>(id, \*\*<a href="src/nextbillion_sdk/types/restriction_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/rich_group_dto_response.py">RichGroupDtoResponse</a></code>
- <code title="patch /restrictions/{id}">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">update</a>(id, \*\*<a href="src/nextbillion_sdk/types/restriction_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/rich_group_dto_response.py">RichGroupDtoResponse</a></code>
- <code title="get /restrictions">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/restriction_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/restriction_list_response.py">RestrictionListResponse</a></code>
- <code title="delete /restrictions/{id}">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">delete</a>(id, \*\*<a href="src/nextbillion_sdk/types/restriction_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/restriction_delete_response.py">RestrictionDeleteResponse</a></code>
- <code title="get /restrictions/list">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">list_paginated</a>(\*\*<a href="src/nextbillion_sdk/types/restriction_list_paginated_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/restriction_list_paginated_response.py">RestrictionListPaginatedResponse</a></code>
- <code title="put /restrictions/{id}/state">client.restrictions.<a href="./src/nextbillion_sdk/resources/restrictions.py">set_state</a>(id, \*\*<a href="src/nextbillion_sdk/types/restriction_set_state_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/rich_group_dto_response.py">RichGroupDtoResponse</a></code>

# RestrictionsItems

Types:

```python
from nextbillion_sdk.types import RestrictionsItemListResponse
```

Methods:

- <code title="get /restrictions_items">client.restrictions_items.<a href="./src/nextbillion_sdk/resources/restrictions_items.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/restrictions_item_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/restrictions_item_list_response.py">RestrictionsItemListResponse</a></code>

# Distancematrix

## Json

Types:

```python
from nextbillion_sdk.types.distancematrix import JsonRetrieveResponse
```

Methods:

- <code title="post /distancematrix/json">client.distancematrix.json.<a href="./src/nextbillion_sdk/resources/distancematrix/json.py">create</a>() -> None</code>
- <code title="get /distancematrix/json">client.distancematrix.json.<a href="./src/nextbillion_sdk/resources/distancematrix/json.py">retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/distancematrix/json_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/distancematrix/json_retrieve_response.py">JsonRetrieveResponse</a></code>

# Autocomplete

Types:

```python
from nextbillion_sdk.types import AutocompleteSuggestResponse
```

Methods:

- <code title="get /autocomplete">client.autocomplete.<a href="./src/nextbillion_sdk/resources/autocomplete.py">suggest</a>(\*\*<a href="src/nextbillion_sdk/types/autocomplete_suggest_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/autocomplete_suggest_response.py">AutocompleteSuggestResponse</a></code>

# Navigation

Types:

```python
from nextbillion_sdk.types import NavigationRetrieveRouteResponse
```

Methods:

- <code title="get /navigation/json">client.navigation.<a href="./src/nextbillion_sdk/resources/navigation.py">retrieve_route</a>(\*\*<a href="src/nextbillion_sdk/types/navigation_retrieve_route_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/navigation_retrieve_route_response.py">NavigationRetrieveRouteResponse</a></code>

# Map

Methods:

- <code title="post /map/segments">client.map.<a href="./src/nextbillion_sdk/resources/map.py">create_segment</a>() -> None</code>

# Autosuggest

Types:

```python
from nextbillion_sdk.types import AutosuggestSuggestResponse
```

Methods:

- <code title="get /autosuggest">client.autosuggest.<a href="./src/nextbillion_sdk/resources/autosuggest.py">suggest</a>(\*\*<a href="src/nextbillion_sdk/types/autosuggest_suggest_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/autosuggest_suggest_response.py">AutosuggestSuggestResponse</a></code>

# Directions

Types:

```python
from nextbillion_sdk.types import DirectionComputeRouteResponse
```

Methods:

- <code title="post /directions/json">client.directions.<a href="./src/nextbillion_sdk/resources/directions.py">compute_route</a>(\*\*<a href="src/nextbillion_sdk/types/direction_compute_route_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/direction_compute_route_response.py">DirectionComputeRouteResponse</a></code>

# Batch

Types:

```python
from nextbillion_sdk.types import BatchCreateResponse, BatchRetrieveResponse
```

Methods:

- <code title="post /batch">client.batch.<a href="./src/nextbillion_sdk/resources/batch.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/batch_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batch">client.batch.<a href="./src/nextbillion_sdk/resources/batch.py">retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/batch_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/batch_retrieve_response.py">BatchRetrieveResponse</a></code>

# Multigeocode

Types:

```python
from nextbillion_sdk.types import MultigeocodeSearchResponse
```

Methods:

- <code title="post /multigeocode/search">client.multigeocode.<a href="./src/nextbillion_sdk/resources/multigeocode/multigeocode.py">search</a>(\*\*<a href="src/nextbillion_sdk/types/multigeocode_search_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/multigeocode_search_response.py">MultigeocodeSearchResponse</a></code>

## Place

Types:

```python
from nextbillion_sdk.types.multigeocode import (
    PlaceItem,
    PlaceCreateResponse,
    PlaceRetrieveResponse,
    PlaceUpdateResponse,
    PlaceDeleteResponse,
)
```

Methods:

- <code title="post /multigeocode/place">client.multigeocode.place.<a href="./src/nextbillion_sdk/resources/multigeocode/place.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/multigeocode/place_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/multigeocode/place_create_response.py">PlaceCreateResponse</a></code>
- <code title="get /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillion_sdk/resources/multigeocode/place.py">retrieve</a>(doc_id, \*\*<a href="src/nextbillion_sdk/types/multigeocode/place_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/multigeocode/place_retrieve_response.py">PlaceRetrieveResponse</a></code>
- <code title="put /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillion_sdk/resources/multigeocode/place.py">update</a>(doc_id, \*\*<a href="src/nextbillion_sdk/types/multigeocode/place_update_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/multigeocode/place_update_response.py">PlaceUpdateResponse</a></code>
- <code title="delete /multigeocode/place/{docId}">client.multigeocode.place.<a href="./src/nextbillion_sdk/resources/multigeocode/place.py">delete</a>(doc_id, \*\*<a href="src/nextbillion_sdk/types/multigeocode/place_delete_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/multigeocode/place_delete_response.py">PlaceDeleteResponse</a></code>

# Revgeocode

Types:

```python
from nextbillion_sdk.types import RevgeocodeRetrieveResponse
```

Methods:

- <code title="get /revgeocode">client.revgeocode.<a href="./src/nextbillion_sdk/resources/revgeocode.py">retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/revgeocode_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/revgeocode_retrieve_response.py">RevgeocodeRetrieveResponse</a></code>

# RouteReport

Types:

```python
from nextbillion_sdk.types import RouteReportCreateResponse
```

Methods:

- <code title="post /route_report">client.route_report.<a href="./src/nextbillion_sdk/resources/route_report.py">create</a>(\*\*<a href="src/nextbillion_sdk/types/route_report_create_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/route_report_create_response.py">RouteReportCreateResponse</a></code>

# SnapToRoads

Types:

```python
from nextbillion_sdk.types import SnapToRoadSnapResponse
```

Methods:

- <code title="get /snapToRoads/json">client.snap_to_roads.<a href="./src/nextbillion_sdk/resources/snap_to_roads.py">snap</a>(\*\*<a href="src/nextbillion_sdk/types/snap_to_road_snap_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/snap_to_road_snap_response.py">SnapToRoadSnapResponse</a></code>

# Postalcode

Types:

```python
from nextbillion_sdk.types import PostalcodeRetrieveCoordinatesResponse
```

Methods:

- <code title="post /postalcode">client.postalcode.<a href="./src/nextbillion_sdk/resources/postalcode.py">retrieve_coordinates</a>(\*\*<a href="src/nextbillion_sdk/types/postalcode_retrieve_coordinates_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/postalcode_retrieve_coordinates_response.py">PostalcodeRetrieveCoordinatesResponse</a></code>

# Areas

Types:

```python
from nextbillion_sdk.types import AreaListResponse
```

Methods:

- <code title="get /areas">client.areas.<a href="./src/nextbillion_sdk/resources/areas.py">list</a>(\*\*<a href="src/nextbillion_sdk/types/area_list_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/area_list_response.py">AreaListResponse</a></code>

# Lookup

Types:

```python
from nextbillion_sdk.types import LookupRetrieveResponse
```

Methods:

- <code title="get /lookup">client.lookup.<a href="./src/nextbillion_sdk/resources/lookup.py">retrieve</a>(\*\*<a href="src/nextbillion_sdk/types/lookup_retrieve_params.py">params</a>) -> <a href="./src/nextbillion_sdk/types/lookup_retrieve_response.py">LookupRetrieveResponse</a></code>
