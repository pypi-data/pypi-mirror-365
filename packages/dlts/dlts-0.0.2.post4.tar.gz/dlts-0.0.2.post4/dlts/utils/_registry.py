import os
import importlib
from typing import Callable, Dict, Any, Union, Tuple, TypeVar, List


RegistryItem = TypeVar("RegistryItem", bound=Callable)


class Registry:

    _registry_list: Dict[str, RegistryItem] = {}

    def __init__(
            self,
            registry_name: str,
            base_type: Union[type, Tuple[Any, ...], Callable]=None,
            lazy_dirs: List[str] =None,
    ) -> None:
        """
            Args:
                registry_name (str): The name of the registry.
                base_type (Union[type, Tuple[Any, ...], Callable], optional): The base type that registered items must conform to.
                    If None, no type checking is performed. Defaults to None.
                lazy_dirs (List[str], optional): List of directories to lazily load modules from.
                    If None, no lazy loading is performed. Defaults to None.
        """
        self.registry_name: str = registry_name
        self.base_type: Union[type, Tuple[Any, ...], Callable] = base_type
        self.lazy_dirs = lazy_dirs
        self._loaded = False

    def items(self) -> List[Tuple[str, RegistryItem]]:
        self._load_modules()
        return self._registry_list.items()

    def keys(self) -> List[str]:
        self._load_modules()
        return self._registry_list.keys()

    def _load_modules(self) -> None:
        """Load all modules in lazy_dirs (trigger registration logic)"""
        if self._loaded or not self.lazy_dirs:
            return
        self._loaded = True
        for dir_path in self.lazy_dirs:
            if not os.path.isdir(dir_path):
                continue
            # Traverse all .py files in the directory (excluding __init__.py)
            for filename in os.listdir(dir_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]  # Remove the .py suffix
                    # Import the module (assuming the directory is in the Python path)
                    importlib.import_module(f"{dir_path}.{module_name}")

    def register(self, name: str):
        def decorator(component: RegistryItem) -> RegistryItem:
            # check conflict name
            if name in self._registry_list:
                raise ValueError(f"The name '{name}' already exist in registry list '{self.registry_name}'")

            # Checks whether the type meets the requirements (if base_type is specified)
            if self.base_type is not None:
                # If base_type is a class, the component is required to be a subclass of it (or itself)
                if isinstance(self.base_type, type):
                    if not issubclass(component, self.base_type):
                        raise TypeError(f"The component '{component.__name__}' must be the subclass of '{self.base_type.__name__}'")
                # If base_type is another type (such as a function), the component is required to be an instance of that type
                else:
                    if not isinstance(component, self.base_type):
                        raise TypeError(f"The component type must be'{type(self.base_type).__name__}'")

            self._registry_list[name] = component
            return component

        return decorator


    def get(self, name: str) -> RegistryItem:
        self._load_modules()
        if name not in self._registry_list:
            raise KeyError(f"The '{name} is not in '{self.registry_name}''，the registry list key is {list(self._registry_list.keys())}")
        return self._registry_list[name]


if __name__ == "__main__":
    # Example usage
    registry = Registry(registry_name="example_registry", base_type=Callable)

    @registry.register("example_function")
    def example_function(x: int) -> int:
        return x * 2

    print(registry.get("example_function")(5))  # Output: 10
    print(registry.keys())  # Output: {'example_function': <function example_function at ...>}
