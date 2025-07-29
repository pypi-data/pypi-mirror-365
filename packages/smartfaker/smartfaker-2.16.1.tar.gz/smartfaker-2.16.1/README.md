## Installation
pip install git+https://github.com/abirxdhack/Fake-Address-Gen.git

## Usage
```python
from smartfaker import Faker

fake = Faker()

# Get a single address for Bangladesh
address = fake.address("BD")
print(address)

# Get multiple addresses with specific fields
addresses = fake.address("BD", count=2, fields=["street_address", "city"])
print(addresses)

# Get available countries
countries = fake.countries()
print(countries)

# Synchronous version (if preferred)
address_sync = fake.address_sync("US")
print(address_sync)