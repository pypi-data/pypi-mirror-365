from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Type

from mmdet_rm.settings import get_settings
from rm import ID, NAME, PropertyManager, DBView, ResourceDB, ResourceDBFactory, ResourceRecord

if TYPE_CHECKING:
    from .work_resource import WorkRecord, WorkResourceFactory


from .command_builder import MMDetectionCommandBuilder

@dataclass
class TaskConfigKey:
    WORK_ID:str = "work_id"
    TASK_ID:str = "task_id"
    TASK_TYPE:str = "task_type"
    DATASET_ID:str = "dataset_id"
    EPOCH:str = "epoch"
    MODEL_ID:str = "model_id"

@dataclass
class TaskConfigManager(PropertyManager):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체체

    @cached_property
    def work_id(self)->ID:
        return self.config[TaskConfigKey.WORK_ID]

    @cached_property
    def task_type(self)->Literal["train", "eval", "test"]:
        return self.config[TaskConfigKey.TASK_TYPE]

    @cached_property
    def dataset_id(self)->ID:
        return self.config[TaskConfigKey.DATASET_ID]

    @cached_property
    def model_id(self)->ID:
        return self.config[TaskConfigKey.MODEL_ID]

    @cached_property
    def epoch(self)->int:
        return self.config[TaskConfigKey.EPOCH]


@dataclass
class MMDetectionCommand:  
    train_code_file_path:Path = field(default_factory=lambda : get_settings().train_code_path)
    test_code_file_path:Path = field(default_factory=lambda : get_settings().test_code_path)

    def get_command(self, task_type:Literal["train", "eval", "test"], relative:bool = True)->Path:
        if task_type == "train":
            path = self.train_code_file_path
        elif task_type == "eval":
            path = self.test_code_file_path
        elif task_type == "test":
            path = self.test_code_file_path
        if relative:
            return path.relative_to(get_settings().project_root)
        else:
            return path

@dataclass
class TaskRecord(ResourceRecord):
    config_manager:TaskConfigManager
    
    cammand_file_manager = MMDetectionCommand()

    @cached_property
    def main_config_file_path(self)->Path:
        from .work_resource import WorkResourceFactory
        work_resource_factory:WorkResourceFactory = WorkResourceFactory()

        work_record:WorkRecord = work_resource_factory.resource_db.get(self.config_manager.work_id)
        return work_record.config_manager.mmdetection_config_file_path

    def make_run_command(self, relative:bool = True)->str:
        
        command_file_path = self.cammand_file_manager.get_command(self.config_manager.task_type, relative=relative)
        main_config_file_path = self.main_config_file_path
        if relative:
            main_config_file_path = main_config_file_path.relative_to(get_settings().project_root)

        options_dict={
            "--cfg-options": {
                "custom_config":{
                    TaskConfigKey.WORK_ID:self.config_manager.work_id,
                    TaskConfigKey.TASK_ID:self.id,
                }
            }
        }

        return MMDetectionCommandBuilder.build_mmdet_command(command_file_path, [main_config_file_path], options_dict)

    def get_dataset_config(self, dataset_id:ID)->tuple[Path, Path]:
        from ..dataset.dataset_resource import DatasetResourceFactory
        dataset_resource_factory:DatasetResourceFactory = DatasetResourceFactory()
        dataset_record = dataset_resource_factory.resource_db.get(dataset_id)
        dataset_dir_path = dataset_record.config_manager.dataset_dir_path
        annotation_file_path = dataset_record.config_manager.annotation_file_path

        return dataset_dir_path, annotation_file_path

    def update_config(self, config):
        dataset_id = self.config_manager.dataset_id
        # model_id = self.config_manager.model_id
        epoch = self.config_manager.epoch


        dataset_dir_path, annotation_file_path = self.get_dataset_config(dataset_id)


        # Train 모드는 val을 포함하지 않음, 어짜피 수행 안할 것임.
        # 그러니 일단 혼돈이 없도록, 전부 학습 데이터로 세팅
        config.train_dataloader.dataset.data_root = dataset_dir_path.as_posix()
        config.train_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.val_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.val_dataloader.dataset.data_root = dataset_dir_path.as_posix()
        config.test_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.test_dataloader.dataset.data_root = dataset_dir_path.as_posix()


        config.work_dir = self.dir_path.as_posix()

        return config

        # print(config)
        # print(type(config))
        # print("업데이트트")
        # exit()



class TaskDB(ResourceDB[TaskRecord]):
    pass




@dataclass
class TaskDBView(DBView):
    db:TaskDB



@dataclass
class TaskResourceFactory(ResourceDBFactory[TaskConfigManager, TaskRecord, TaskDB, TaskDBView]):
    dir_path:Path

    CONFIG_MANAGER_CLASS:Type[PropertyManager] = TaskConfigManager
    RECORD_CLASS:Type[ResourceRecord] = TaskRecord
    DB_CLASS:Type[ResourceDB] = TaskDB
    VIEW_CLASS:Type[DBView] = TaskDBView
    CONFIG_NAME:str = field(default="task_config")


    def make_record(self, id:ID, name:NAME, dir_path:Path)->TaskRecord:
        return self.RECORD_CLASS(id, name, dir_path, self.config_manager(dir_path))



if __name__ == "__main__":
    factory = TaskResourceFactory(Path("/home/submodules/mmdetection/resources/works/beverage_train/L10___id_5"))
    db = factory.resource_db
    
    print(factory.view.table)
    

