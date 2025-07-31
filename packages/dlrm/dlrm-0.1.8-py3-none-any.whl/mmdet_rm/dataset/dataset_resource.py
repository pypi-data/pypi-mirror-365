from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Type

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME

@dataclass
class DatasetConfigKey:
    DATA_DIR:str = "data_dir_path"
    ANNOTATION_DIR:str = "annotation_file_path"

@dataclass
class DatasetConfigManager(PropertyManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체

    @cached_property
    def dataset_dir_path(self)->Path:
        return self.dir_path / self.config[DatasetConfigKey.DATA_DIR]


    @cached_property
    def annotation_file_path(self)->Path:
        return self.dir_path / self.config[DatasetConfigKey.ANNOTATION_DIR]


class DatasetRecord(ResourceRecord[DatasetConfigManager]):
    pass


class DatasetDB(ResourceDB[DatasetRecord]):
    
    def create(self, name:NAME)->DatasetRecord:
        record = super().create(name)
        record.config_manager.set(DatasetConfigKey.DATA_DIR, (record.dir_path / "data").as_posix())
        record.config_manager.set(DatasetConfigKey.ANNOTATION_DIR, (record.dir_path / "annotation.json").as_posix())

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

    CONFIG_NAME:str = field(default="dataset_config")


if __name__ == "__main__":
    factory = DatasetResourceFactory()
    db = factory.resource_db
    record = db.create("bear_v3")

    print(record.config_manager.config)
    # print(record.config_manager.dir_path)
    # print(record.config_manager.annotation_file_path)