from typing import Optional, Union


class BaseConfig:
    def __init__(
            self,
            config_name: str
    ) -> None:

        self.config_name = config_name

    def get_config(self, scale: Optional[Union[int, float, str, None]]) -> dict:
        raise NotImplementedError()
