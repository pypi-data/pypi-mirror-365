from pathlib import Path

project_root = Path(__file__).parent.parent

resource_dir = project_root / "resources"

work_dir = resource_dir / "works"
dataset_dir = resource_dir / "datasets"
model_dir = resource_dir / "models"
log_dir = resource_dir / "logs"
result_dir = resource_dir / "results"
config_dir = resource_dir / "configs"
checkpoint_dir = resource_dir / "checkpoints"
tensorboard_dir = resource_dir / "tensorboard"








train_code_path = project_root / "tools/train.py"
test_code_path = project_root / "tools/test.py"


def to_relative_path(path:Path)->Path:
    return path.relative_to(project_root)

def to_absolute_path(path:Path)->Path:
    return project_root / path