from pathlib import Path
from .memo import FileMemo
from .file_io import JsonFileIO, YamlFileIO


class MemoFactory:
    def make_file_json_file_memo(self, file_path:Path)->FileMemo:
        return FileMemo(file_path.with_suffix(".json"), JsonFileIO(), None)

    def make_file_yaml_file_memo(self, file_path:Path)->FileMemo:
        return FileMemo(file_path.with_suffix(".yaml"), YamlFileIO(), None)


