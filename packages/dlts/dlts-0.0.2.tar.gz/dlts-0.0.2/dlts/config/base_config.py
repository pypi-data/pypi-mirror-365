from typing import Optional


class BaseConfig:
    def __init__(
            self,
            config_name: str
    ) -> None:

        self.config_name = config_name

    def get_config(self, scale: Optional[int, float, str]) -> dict:
        raise NotImplementedError()
