# `wattmaven-solarnetwork-tools`

[![codecov](https://codecov.io/gh/wattmaven/wattmaven-solarnetwork-tools/graph/badge.svg?token=NWTI6GOZ0P)](https://codecov.io/gh/wattmaven/wattmaven-solarnetwork-tools)

The WattMaven Python package for SolarNetwork tools.

Note that _this package is still under active development and the API is not yet stable_. Breaking changes will be
introduced in the **minor** version until the API is stable.

## Installation

```bash
pip install wattmaven-solarnetwork-tools
```

## Usage

See [examples](./examples) for usage examples.

```python
from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkCredentials,
)

# Create a client
with SolarNetworkClient(
    host="data.solarnetwork.net",
    credentials=SolarNetworkCredentials(
        token="your_token",
        secret="your_secret",
    )
) as client:
    # Make requests
    response = client.request("GET", "/solarquery/api/v1/sec/nodes")
    json = response.json()
    print(json)
    # ...
```

## Testing

```bash
# This will run tests and generate a coverage report
make test
```

![Coverage](https://codecov.io/gh/wattmaven/wattmaven-solarnetwork-tools/graphs/tree.svg?token=NWTI6GOZ0P)

## Creating a Release

This project uses [Hatch](https://hatch.pypa.io/) for building and releasing.

```bash
# Bump the version
cz bump --major-version-zero

# Build the package
uv build

# Release the package
uv publish

# Push the changes
git push
git push -u origin v<new-version>
```

## Acknowledgements

This project takes inspiration from the [solarnetwork-api-core](https://github.com/SolarNetwork/sn-api-core-js)
JavaScript package. This package is not a direct port.

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.
