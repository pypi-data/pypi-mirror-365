
from pathlib import Path
from .file_io import CONTENT_TYPE, FileIO
import yaml
import pandas as pd
import json
from dataclasses import dataclass
from typing import ClassVar, Any, List
from typing import Callable
from abc import ABC

class Memo(ABC):
    # File과 Memory에 관계 없이 데이터를 다루는 객체
    # 확장에 따라 file, memory 또는 둘 다 동시에 저장할 수도 있음
    
    def get(self)->Any: # 데이터를 전부 반환
        raise NotImplementedError("Not Implemented")
    
    def set(self, data)->None: # 데이터를 전부 저장
        raise NotImplementedError("Not Implemented")

    def clear(self):
        raise NotImplementedError("Not Implemented")
    
    def create(self):
        raise NotImplementedError("Not Implemented")



@dataclass
class FileMemo(Memo):
    file_path:Path
    file_io:FileIO
    content: CONTENT_TYPE

    def __post_init__(self):
        if not self.file_path.exists():       
            self.file_io.create(self.file_path)
        self.content = self.file_io.read(self.file_path)

    def get(self)->Any: # 데이터를 전부 반환
        return self.content
    
    def set(self, data)->None: # 데이터를 전부 저장
        self.content = data
        self.file_io.write(self.file_path, self.content)

    def remove(self):
        self.content = None
        if self.file_path.exists():
            self.file_io.remove(self.file_path)
    
