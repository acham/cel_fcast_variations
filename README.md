# CEL Exercise: Forecast Variations

## Overview

This application queries hourly forecast data for coordinates provided
by the user at regular intervals, stores them in a local database, and
provides an API to query this data.

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
environment file and the database file into the container.

## Implementation

`main.py` defines the API endpoints, and it starts an optional
asynchronous task to collect forecast points from the National Weather
Service's public API at regular intervals. This asynchronous task is
defined in function `retrieve_new_forecasts`.

`config.py` defines a configuration that is mainly obtained from the
environment variables.  `model/` contains a data model that is used by
the API, and `db/` implements the database layer, including the
database schema and CRUD operations to write and retrieve forecast
points.

## Discussion 

SQLite was chosen due to its simplicity and its ability
to use local storage, which is a requirement for this project. For
larger-scale forecast data, a dedicated time series database such as
TimescaleDB would be a more adequate choice.

The API endpoint to retrieve a forecast range requires a JSON request
body with the following fields: 
  - latitude: float 
  - longitude: float 
  - fc_date: date string in format YYYY-MM-DD 
  - hour of day: int, from 0
to 23

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

The backing CRUD operation for this endpoint retrieves all of the
forecast points that correspond to this specification from the
database and then finds the minimum and maximum temperatures in the
range. With a time series database, these minimum and maximum values
can be better discovered through the database query itself. Here,
there is an assumption that each forecast specification does not
correspond to many data points, so it is acceptable to transfer all
the corresponding points and let the Python code handle the filtering.

There is also an assumption that older records are removed from the
database separately.  With a time series database, a lifetime can be
specified for each point, allowing the database to automatically clean
old data.
