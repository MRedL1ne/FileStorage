from . import db
from datetime import datetime

class File(db.Model):
    # Создаем таблицу файлов
    __tablename__ = 'files'
    id = db.Column("id", db.INTEGER, primary_key=True)
    name = db.Column("name", db.CHAR(255), nullable=False)
    extension = db.Column("extension", db.String(20), nullable=False)
    size = db.Column("size", db.BIGINT, nullable=False)
    path = db.Column("path", db.TEXT, nullable=False)
    created_at = db.Column("created_at", db.TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = db.Column("updated_at", db.TIMESTAMP, nullable=True)
    comment = db.Column("comment", db.TEXT, nullable=True)

    def __init__(self,name,ext,size,path,cr_at=datetime.now(),up_at=None,comment=None):
        self.name = name
        self.extension = ext
        self.size = size
        self.path = path
        self.created_at = cr_at
        self.updated_at = up_at
        self.comment = comment

    def __repr__(self):
        return {
            "name": self.name.strip(),
            "extension": self.extension.strip(),
            "size": self.size,
            "path": self.path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comment": self.comment
        }.__str__()

    def getData(self):
        return {
            "id": self.id,
            "name": self.name.strip(),
            "extension": self.extension.strip(),
            "size": self.size,
            "path": self.path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comment": self.comment
        }