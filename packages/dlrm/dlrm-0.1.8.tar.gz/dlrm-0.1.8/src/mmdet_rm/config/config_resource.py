from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Type

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME

@dataclass
class MainConfig_PropertyKey:
    MAIN_CONFIG_FILE_PATH:str = "main_config_file_path"

@dataclass
class MainConfig_PropertyManager(PropertyManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체

    @property
    def main_config_file_path(self)->Path:
        return self.dir_path / self.config[MainConfig_PropertyKey.MAIN_CONFIG_FILE_PATH]

    @main_config_file_path.setter
    def main_config_file_path(self, value:Path)->None:
        self.config[MainConfig_PropertyKey.MAIN_CONFIG_FILE_PATH] = value.as_posix()



class MainConfigRecord(ResourceRecord[MainConfig_PropertyManager]):
    pass


class MainConfigDB(ResourceDB[MainConfigRecord]):
    
    def create(self, name:NAME)->MainConfigRecord:
        # 실제로 
        record = super().create(name)
        record.config_manager.set(MainConfig_PropertyKey.MAIN_CONFIG_FILE_PATH, (record.dir_path / "main_config.py").as_posix())
        return record

class MainConfigDBView(DBView):
    db:MainConfigDB


@dataclass
class MainConfig_ResourceFactory(ResourceDBFactory[MainConfig_PropertyManager, MainConfigRecord, MainConfigDB, MainConfigDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().config_dir)
    
    CONFIG_MANAGER_CLASS:Type[PropertyManager] = MainConfig_PropertyManager
    RECORD_CLASS:Type[ResourceRecord] = MainConfigRecord
    DB_CLASS:Type[ResourceDB] = MainConfigDB
    VIEW_CLASS:Type[MainConfigDBView] = MainConfigDBView

    CONFIG_NAME:str = field(default="main_config_properties")