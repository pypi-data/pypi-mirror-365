from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

from resource_manager.dirdb.dirdb import ID, NAME
from resource_manager.resource_db.config_manager import ConfigManager

RESOURCE_CONFIG_MANAGER = TypeVar('CONFIG_MANAGER_CLASS', bound=ConfigManager)

@dataclass
class ResourceRecord(Generic[RESOURCE_CONFIG_MANAGER]):
    # 단일 데이터 셋, 모델 또는 작업을 관리한다.
    # 리소스에 맞게 확장된 클래스를 사용한 것으로 기대대 
    id:ID
    name:NAME
    dir_path:Path
    config_manager:RESOURCE_CONFIG_MANAGER



