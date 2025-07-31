from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict

from ..memo import MemoFactory, FileMemo


@dataclass
class PropertyManager:
    # 데이터를 통째로 로드/저장하는 객체를 확장하여
    # 
    # 필요한 값들에 대해 세부적으로 불러오는 것은 Record에 따라 확장해서 사용

    dir_path:Path
    memo_factory:MemoFactory
    CONFIG_NAME:str = field(default="config")

    def __post_init__(self):
        self.file_memo:FileMemo = self.memo_factory.make_file_json_file_memo(self.config_file_path)

    @cached_property
    def config_file_path(self)->Path:
        return self.dir_path / self.CONFIG_NAME

    # @cached_property
    # def config_memo(self)->FileMemo:
    #     return self.memo_factory.make_file_json_file_memo(self.config_file_path)

    def get(self, key:str)->Any:
        return self.config[key]


    def set(self, key:str, value:Any)->None:
        config = self.config
        config[key] = value
        self.config = config


    @property
    def config(self)->Dict[str, Any]:
        return self.file_memo.get()

    @config.setter
    def config(self, config:Dict[str, Any])->None:
        self.file_memo.set(config)
