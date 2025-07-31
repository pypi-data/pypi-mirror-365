from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Type

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.resource_db.property_manager import PathHandling_PropertyManager

@dataclass
class DatasetConfigKey:
    DATA_DIR:str = "data_dir_path"
    ANNOTATION_DIR:str = "annotation_file_path"

@dataclass
class DatasetConfigManager(PathHandling_PropertyManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체

    @property
    def dataset_dir_path(self)->Path:
        return self.get_as_absolute_path(DatasetConfigKey.DATA_DIR)

    @dataset_dir_path.setter
    def dataset_dir_path(self, value:Path)->None:
        self.set_as_relative_path(DatasetConfigKey.DATA_DIR, value)

    @property
    def annotation_file_path(self)->Path:
        return self.get_as_absolute_path(DatasetConfigKey.ANNOTATION_DIR)

    @annotation_file_path.setter
    def annotation_file_path(self, value:Path)->None:
        self.set_as_relative_path(DatasetConfigKey.ANNOTATION_DIR, value)


class DatasetRecord(ResourceRecord[DatasetConfigManager]):
    pass


class DatasetDB(ResourceDB[DatasetRecord]):
    
    def create(self, name:NAME)->DatasetRecord:
        record = super().create(name)
        pm = record.property_manager
        pm.dataset_dir_path = pm.as_absolute_path("data")
        pm.annotation_file_path = pm.as_absolute_path("annotation.json")

        return record

class DatasetDBView(DBView):
    db:DatasetDB


@dataclass
class DatasetResourceFactory(ResourceDBFactory[DatasetConfigManager, DatasetRecord, DatasetDB, DatasetDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().dataset_dir)
    
    CONFIG_MANAGER_CLASS:Type[PropertyManager] = DatasetConfigManager
    RECORD_CLASS:Type[ResourceRecord] = DatasetRecord
    DB_CLASS:Type[ResourceDB] = DatasetDB
    VIEW_CLASS:Type[DatasetDBView] = DatasetDBView

if __name__ == "__main__":
    factory = DatasetResourceFactory()
    db = factory.db
    record = db.create("bear_v3")

    print(record.property_manager.content)
    # print(record.config_manager.dir_path)
    # print(record.config_manager.annotation_file_path)