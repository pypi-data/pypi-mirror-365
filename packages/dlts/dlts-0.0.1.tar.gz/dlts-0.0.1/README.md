# Deep Learning Tools for Pytorch

[![Python >= 3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/release/)

A package that contains tools for deep learning model.

Now, it just contains registry class for managing your models or functions conveniently.

## Installation

```bash
pip install dlts
```

## Example for using

```python
from typing import Callable

from dlts import Registry

# Example usage
registry = Registry(registry_name="example_registry", base_type=Callable)

@registry.register("example_function")
def example_function(x: int) -> int:
    return x * 2

print(registry.get("example_function")(5))  # Output: 10
print(registry.keys())  # Output: dict_keys(['example_function'])
```

## Update
- 0.0.1 - It is an official version.
- 0.0.1alpha2 - It is a test version.

## Future Plans
- Add some models which are used in the food classification.
- Add more tools for deep learning model management.

## License

mDeep Learning Tools for Pytorch is MIT licensed. See the [LICENSE](LICENSE) for details.

