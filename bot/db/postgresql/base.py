import os

from sqlalchemy.orm import DeclarativeBase
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file.storage import StorageManager


class Base(DeclarativeBase):
    # repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            # if col in self.repr_cols or idx < self.repr_cols_num:
            cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


# Configure Storage
os.makedirs("./upload_dir/media", 0o777, exist_ok=True)
container = LocalStorageDriver("./upload_dir").get_container("media")
StorageManager.add_storage("default", container)
