<p align=center>
    <img src="https://upload.wikimedia.org/wikipedia/fi/thumb/2/2a/Veolia-logo.svg/250px-Veolia-logo.svg.png"/>
</p>

<p>
    <a href="https://pypi.org/project/veolia-api/"><img src="https://img.shields.io/pypi/v/veolia-api.svg"/></a>
    <a href="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" /></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>
    <a href="https://github.com/Jezza34000/veolia-api/actions"><img src="https://github.com/Jezza34000/veolia-api/workflows/CI/badge.svg"/></a>
</p>

Python wrapper for using Veolia API : https://www.eau.veolia.fr/

## Installation

```bash
pip install veolia-api
```

## Usage

```python
"""Example of usage of the Veolia API"""

import asyncio
import logging

from veolia_api.veolia_api import VeoliaAPI

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    """Main function."""
    # Create an instance of the VeoliaAPI class
    api = VeoliaAPI("username", "password")

    try:
        # Fetch data for November 2024
        await api.fetch_all_data(2024, 11)

        # Display fetched data
        print(api.account_data.daily_consumption)
        print(api.account_data.monthly_consumption)
        print(api.account_data.alert_settings.daily_enabled)

    except Exception as e:
        logging.error("An error occurred: %s", e)
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(main())

```

## Credits

This repository is inspired by the work done by @CorentinGrard. Thanks to him for his work.
