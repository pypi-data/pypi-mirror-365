from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Type

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.resource_db.property_manager import PathHandling_PropertyManager

@dataclass
class MainConfig_PropertyKey:
    MAIN_CONFIG_FILE_PATH:str = "main_config_file_path"

@dataclass
class Config_PropertyManager(PathHandling_PropertyManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체

    @property
    def config_file_path(self)->Path:
        return self.get_as_absolute_path(MainConfig_PropertyKey.MAIN_CONFIG_FILE_PATH)

    @config_file_path.setter
    def config_file_path(self, value:Path)->None:
        self.set_as_relative_path(MainConfig_PropertyKey.MAIN_CONFIG_FILE_PATH, value)



class ConfigRecord(ResourceRecord[Config_PropertyManager]):
    pass


class ConfigDB(ResourceDB[ConfigRecord]):
    
    def create(self, name:NAME)->ConfigRecord:
        # 실제로 
        record = super().create(name)
        record.property_manager.config_file_path = record.dir_path / "main_config.py"
        return record

class ConfigDBView(DBView):
    db:ConfigDB


@dataclass
class MainConfig_ResourceFactory(ResourceDBFactory[Config_PropertyManager, ConfigRecord, ConfigDB, ConfigDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().config_dir)
    
    CONFIG_MANAGER_CLASS:Type[PropertyManager] = Config_PropertyManager
    RECORD_CLASS:Type[ResourceRecord] = ConfigRecord
    DB_CLASS:Type[ResourceDB] = ConfigDB
    VIEW_CLASS:Type[ConfigDBView] = ConfigDBView
