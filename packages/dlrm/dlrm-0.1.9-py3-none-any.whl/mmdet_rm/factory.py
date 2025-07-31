from functools import cached_property

from mmdet_rm.config.config_resource import MainConfig_ResourceFactory
from mmdet_rm.dataset.dataset_resource import DatasetResourceFactory
from mmdet_rm.work.work_resource import WorkResourceFactory

class MMDetection_RM_Factory:
    @cached_property
    def dataset_factory(self)->DatasetResourceFactory:
        return DatasetResourceFactory()
    
    @cached_property
    def work_factory(self)->WorkResourceFactory:
        return WorkResourceFactory()
        
    
    @cached_property
    def main_config_factory(self)->MainConfig_ResourceFactory:
        return MainConfig_ResourceFactory()