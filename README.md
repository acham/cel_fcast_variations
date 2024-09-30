# National Weather Service Forecast Variations

This code illustrates a scenario in which both a background
task and a client-facing API can be provided in a single container
supported by FastAPI.

A background task queries hourly forecast data for coordinates provided
by the user at regular intervals, stores them in a local database, and
the main application provides an API to query this data.

The application code is in `/app`, and it consists of a FastAPI
application that uses SQLAlchemy to interface with a SQLite instance.

A Docker image for the app is defined by the Dockerfile, and the
`.env` file in the top-level directory allows the user to control the
application at runtime using environments variables that are passed
into the running container.  The variables include the desired
latitude and longitude to use for the NWS retrieval, a retrieval
interval in minutes defaulting to 60, NWS base URLs, and a flag that
specifies whether to run the background retrieval at all; if this flag
is set to False, the container can be used as an API only.

Building the image:
```
$ docker build -t fcast_variations .
```

The script `docker_run.sh` runs the container, mapping both the
environment file and the database volume into the container.

SQLite was chosen due to its simplicity and its ability
to use local storage. For
larger-scale forecast data, a dedicated time series database such as
TimescaleDB would be a more adequate choice.

The API endpoint to retrieve a forecast range requires a JSON request
body with the following fields: 
  - latitude: float 
  - longitude: float 
  - fc_date: date string in format YYYY-MM-DD 
  - hour of day: int, from 0 to 23

Example: 
``` 
{ 
    "latitude": 37.927877, 
    "longitude": -122.579370,
    "fc_date": "2024-09-25", 
    "hour_of_day": 3 
} 
```

The payload for this endpoint includes all fields in the database
for the min and max temperature points, including NWS metadata.

For a long-running application, older records should be removed from the
database separately.
