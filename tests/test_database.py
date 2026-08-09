from pathlib import Path

from app.database import BASE_DIR, DATABASE_PATH


def test_database_path_is_created_inside_project_data_directory():
    assert DATABASE_PATH == BASE_DIR / "data" / "optimus.db"
    assert DATABASE_PATH.parent == BASE_DIR / "data"
    assert DATABASE_PATH.parent.exists()
