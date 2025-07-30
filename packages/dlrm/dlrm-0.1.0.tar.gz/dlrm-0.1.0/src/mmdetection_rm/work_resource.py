from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
import shutil
from typing import Optional, Type

from resource_manager import NAME, ConfigManager, ResourceDB, ResourceDBFactory, ResourceRecord, ID, DBView
# from resource_manager.dirdb.dirdb import DirDB
# from resource_manager.dirdb.factory import DirDBFactory
# from resource_manager.memo import MemoFactory
from .task import TaskConfigKey, TaskDB, TaskResourceFactory, TaskRecord
# from .command_builder import MMDetectionCommandBuilder

from . import env_config



@dataclass
class WorkConfigKey:
    # TRAIN_DATASET_ID:str = "train_dataset_id"
    # VAL_DATASET_ID:str = "val_dataset_id"
    # TEST_DATASET_ID:str = "test_dataset_id"
    # PRETRAINED_CHECKPOINT_FILE_PATH:str = "pretrained_checkpoint_file_path"
    pass
    # CONFIG_FILE_PATH:str = "config_file_path"
    MMDETECTION_CONFIG_FILE_PATH:str = "mmdetection_config_file_path"



@dataclass
class WorkConfigManager(ConfigManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체체
    # @cached_property
    # def train_dataset_id(self)->ID:
    #     return self.config[WorkConfigKey.TRAIN_DATASET_ID]

    # @cached_property
    # def pretrained_checkpoint_file_path(self)->Path:
    #     return self.config[WorkConfigKey.PRETRAINED_CHECKPOINT_FILE_PATH]


    # @cached_property
    # def config_file_path(self)->Path:
    #     return self.config[WorkConfigKey.CONFIG_FILE_PATH]

    @cached_property
    def mmdetection_config_file_path(self)->Path:
        return self.dir_path/self.config[WorkConfigKey.MMDETECTION_CONFIG_FILE_PATH]


# @dataclass
# class PathManager:
#     root:'WorkRecord'


#     @cached_property
#     def dir_path(self)->Path:
#         return self.root.dir_path

#     @cached_property
#     def mmdetection_config_file_path(self)->Path:
#         return self.dir_path / "mmdetection_config.py"

#     @cached_property
#     def train_work_dir_path(self)->Path:
#         return self.dir_path / "train"

#     @cached_property
#     def test_work_dir_path(self)->Path:
#         return self.dir_path / "test"


# @dataclass
# class CheckpointPathManager:
#     root:'WorkRecord'

#     @cached_property
#     def pm(self)->PathManager:
#         return self.root.pm

#     @cached_property
#     def checkpoint_dir_path(self)->Path:
#         return self.root.pm.train_work_dir_path

#     def checkpoint_file_name(self, epoch:int)->str:
#         return f"iter_{epoch}.pth"

#     def checkpoint_file_path(self, epoch:int)->Path:
#         return self.checkpoint_dir_path / self.checkpoint_file_name(epoch)

#     def find_all_checkpoint_file_paths(self)->list[Path]:
#         return list(self.checkpoint_dir_path.rglob('iter_*.pth'))

    
#     def pretrained_checkpoint_file_path(self)->Path:
#         return self.root.config_manager.pretrained_checkpoint_file_path


# @dataclass
# class CheckpointManager:
#     # 하나의 work에 대하 checkpoint 파일은 모두 한 폴더에 저장된다고 가정
#     # 저장 폴더 경로는 path manager가 관리한다.

#     root:'WorkRecord'

#     @cached_property
#     def pm(self)->'PathManager':
#         return self.root.pm

#     @cached_property
#     def cppm(self)->'CheckpointPathManager':
#         return self.root.cppm


#     @cached_property
#     def checkpoint_epochs(self)->list[int]:
#         epochs = [int(path.stem.split("_")[1]) for path in self.cppm.find_all_checkpoint_file_paths()]
#         return sorted(epochs)

#     @cached_property
#     def checkpoint_file_num(self)->int:
#         return len(self.checkpoint_epochs)

#     @cached_property
#     def latest_checkpoint_epoch(self)->int:
#         return self.checkpoint_epochs[-1]

#     @cached_property
#     def latest_checkpoint_file_path(self)->Path:
#         return self.cppm.checkpoint_file_path(epoch=self.latest_checkpoint_epoch)

# @dataclass
# class WorkCommandBuilder:
#     root:'WorkRecord'


#     @cached_property
#     def train_code_path(self)->Path:
#         return env_config.train_code_path
    
#     @cached_property
#     def test_code_path(self)->Path:
#         return env_config.test_code_path

#     def make_command(self, command_file:Path, config_path:Path, options:dict):
#         return f"python {command_file} {config_path} {options}"

#     def make_train_command(self, )->str:
#         options_dict={
#             "--cfg-options": {
#                 "custom_config":{
#                     "work_id":1,
#                 }
#             }
#         }
#         MMDetectionCommandBuilder.build_mmdet_command(self.train_code_path, self. .as_posix(), options_dict)
#         return self.make_command(self.train_code_path, self.root.config_manager.config_file_path, options_dict)

#     def make_train_command(self):

#         return MMDetectionCommandBuilder.make_train_command(config_path.as_posix(), options_dict)





@dataclass
class WorkRecord(ResourceRecord):
    config_manager:WorkConfigManager
    
    def __post_init__(self):
        self.task_resource_factory:TaskResourceFactory = TaskResourceFactory(self.dir_path)

    @cached_property
    def task_db(self)->TaskDB:
        return self.task_resource_factory.resource_db
    

    def to_relative_path(self, path:Path)->Path:
        return path.relative_to(self.dir_path)

    def exist_train_task(self)->bool:
        return self.task_db.exist(self.train_task_name)

    def make_train_task(self, train_dataset_id:ID, model_id:ID, epoch:int)->TaskRecord:
        if self.exist_train_task():
            raise ValueError(f"Train task already exists: {self.train_task_name}")
        
        task = self.task_db.create(self.train_task_name)
        task.config_manager.set_config({
            TaskConfigKey.WORK_ID:self.id,
            TaskConfigKey.TASK_TYPE:"train",
            TaskConfigKey.DATASET_ID:train_dataset_id,
            TaskConfigKey.MODEL_ID:model_id,
            TaskConfigKey.EPOCH:epoch,

        })

        return task

    # CONFIG_NAME = "work_config.json"
    # dir_db:DirDB = DirDBFactory().make_dirdb

    # def __post_init__(self):
    #     self.pm:'PathManager' = PathManager(root=self)
    #     self.cppm:'CheckpointPathManager' = CheckpointPathManager(root=self)
    #     self.checkpoint_manager:'CheckpointManager' = CheckpointManager(root=self)



    # def _make_train_task(self, dir_path:Path, mmdet_config_file_path:Path, model_id:ID, dataset_id:ID, epoch:int)->TrainTask:
    #     task = TaskFactory().make_train_task(dir_path)
    #     task.config_manager.set_config({
    #         TaskConfigKey.MMDETECTION_CONFIG_FILE_PATH:mmdet_config_file_path.as_posix(),
    #         TaskConfigKey.DATASET_ID:dataset_id,
    #         TaskConfigKey.MODEL_ID:model_id,
    #         TaskConfigKey.EPOCH:epoch
    #     })

    #     return task

    # def make_train_task(self, model_id:ID, dataset_id:ID, epoch:int)->TrainTask:
    #     return self._make_train_task(self.train_task_dir(), self.pm.mmdetection_config_file_path, model_id, dataset_id, epoch)

    @cached_property
    def train_task_dir(self)->Path:
        return self.dir_path / "train"

    @cached_property
    def train_task_name(self)->NAME:
        return self.to_relative_path(self.train_task_dir).as_posix()

    def test_task_dir(self, dataset_id:ID, epoch:int)->Path:
        return self.dir_path / "test" / f"epoch_{epoch}" / f"{dataset_id}"

    # def val_task_dir(self, dataset_id:ID)->Path:
    #     return self.dir_path / "val" / f"{dataset_id}"


# @dataclass
# class WorkConfig:
#     train_dataset_id:ID
#     test_dataset_id:ID
    
    
class WorkDB(ResourceDB[WorkRecord]):
    
    def create(self, name: NAME, main_config_file_path:Optional[Path] = None) -> WorkRecord:
        if main_config_file_path is not None:
            if not main_config_file_path.exists():
                raise FileNotFoundError(f"Main config file not found: {main_config_file_path}")

        record = super().create(name)

        new_config_path = record.dir_path / "main_config.py"
        if main_config_file_path is not None:
            shutil.copy(main_config_file_path, new_config_path)
        
        record.config_manager.set_config({
            WorkConfigKey.MMDETECTION_CONFIG_FILE_PATH:new_config_path.as_posix()
        })

        return record

class WorkDBView(DBView):
    db:WorkDB




@dataclass
class WorkResourceFactory(ResourceDBFactory[WorkConfigManager, WorkRecord, WorkDB, WorkDBView]):
    dir_path:Path = env_config.work_dir
    
    CONFIG_MANAGER_CLASS:Type[ConfigManager] = WorkConfigManager
    RECORD_CLASS:Type[ResourceRecord] = WorkRecord
    DB_CLASS:Type[ResourceDB] = WorkDB
    VIEW_CLASS:Type[WorkDBView] = WorkDBView

    CONFIG_NAME:str = field(default="work_config")

    def make_task_resource_factory(self)->TaskResourceFactory:
        return TaskResourceFactory(self.dir_path)


if __name__ == "__main__":
    factory = WorkResourceFactory()
    db = factory.resource_db
    work = db.create("test")
    # work = db.get("test")
    # print(work)
    task = work.make_train_task(1, 1, 1)

    command = task.make_run_command()
    print(command)

    
    # print(task.config_manager.config)

