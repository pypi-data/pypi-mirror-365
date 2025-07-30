# Deep Learning Tools for Pytorch

[![Python >= 3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/release/)

A package that contains tools for deep learning model. We add the registry class which can make developer use the registry method
to manage their models or functions conveniently.

In other side, we will provide our work in classification task for developer, which can use the model directly.
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

## Papers
- Nutrients 2024, "[A Lightweight Hybrid Model with Location-Preserving ViT for
Efficient Food Recognition](https://ldu-iiplab.github.io/zh/publication/sheng-2024-lightweight/sheng-2024-lightweight.pdf)"

- ![EHFR Net Structure](doc/images/LP-ViT.jpg "本地图片示例")

### BibTex
```BibTex
@article{sheng2024lightweight,
  title={A lightweight hybrid model with location-preserving ViT for efficient food recognition},
  author={Sheng, Guorui and Min, Weiqing and Zhu, Xiangyi and Xu, Liang and Sun, Qingshuo and Yang, Yancun and Wang, Lili and Jiang, Shuqiang},
  journal={Nutrients},
  volume={16},
  number={2},
  pages={200},
  year={2024},
  publisher={MDPI}
}
```

## Update
- 0.0.2 - We add the EHFR-Net model in the tools.
- 0.0.1 - It is an official version.
- 0.0.1alpha2 - It is a test version.

## Future Plans
- Add some models which are used in the food classification.
- Add more tools for deep learning model management.

## License

mDeep Learning Tools for Pytorch is MIT licensed. See the [LICENSE](LICENSE) for details.

