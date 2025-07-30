from functools import cached_property

from mmdetection_rm.dataset.dataset_resource import DatasetResourceFactory
from mmdetection_rm.work.work_resource import WorkResourceFactory

class MMDetection_RM_Factory:
    @cached_property
    def dataset_factory(self)->DatasetResourceFactory:
        return DatasetResourceFactory()
    
    @cached_property
    def work_factory(self)->WorkResourceFactory:
        return WorkResourceFactory()
        