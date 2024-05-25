# Exchange Prices Aggregator

This is a service which collects, parses and aggregates coin price data from a selection of crypto exchanges, a test assignment done for Evvve.
Currently supported:

    - Binance
    - ByBit

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Exchange Prices Aggregator](#exchange-prices-aggregator)
    - [Development](#development)
    - [Running locally](#running-locally)
    - [Running with Docker Compose](#running-with-docker-compose)

<!-- markdown-toc end -->

## Development

This project uses PDM for dependency/project management, keeping general configuration settings in `pyproject.toml`.
Install it with:

``` sh
$ pip install --user pdm
$ pdm self update
```

Fetching dependencies:

``` sh
# Production + development
$ pdm install --dev

# Production only
$ pdm install --prod
```

Run the app:

``` sh
# Switch to the project virtualenv
$ eval $(pdm venv activate)

# Make sure that your .env configuration exists and is valid
$ . ./.env

$ fastapi dev src/rabdulatipoff_evvve_test/main.py
```

Updating requirements.txt for container deployment:

``` sh
$ pdm export -f requirements --prod > requirements.txt
```

## Running locally

1. Install dependencies (skip if you have followed the [Development](#development) section):

``` sh
# It is advised to create a virtualenv first
$ virtualenv ./.venv
$ source .venv/bin/activate

$ pip install -r requirements.txt
```

2. Provide a .env configuration & modify values if needed:

``` sh
# Use .env.local if memcached is running on the host system (e.g. installed from a DEB/RPM repository)
$ cp .env.compose .env
$ . ./.env
```

3. Provide the cache service (skip if it is already running on the host):

``` sh
$ docker compose up cache -d
```

4. Run the application:

``` sh
$ fastapi prod src/rabdulatipoff_evvve_test/main.py --port $APP_PORT
```


## Running with Docker Compose

1. Provide a .env configuration & modify values if needed:

``` sh
$ cp .env.compose .env
$ . ./.env
```

2. Build the Docker image and start Compose services in detached mode:

``` sh
$ docker compose up --build -d
```

3. Observe logs with:

``` sh
$ docker compose logs app -f
```


Explore the API in a browser (APP_PORT is set to 8000 by default):

`https://localhost:8000/docs`

