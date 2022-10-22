from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class DownloadDb(Base):
    __tablename__ = "dwnloads"
    id = Column("id", Integer, primary_key=True)
    path = Column("path", String, default=None)
    download_status = Column(Integer, default=-1)
    key_data = Column("key_data", String)
    tl_data = Column("tl_data", String)
    title = Column("title", String, index=True)
    links = Column("files", String, default=None)
    page = Column("page", String)
    downloads = Column("downloads", String)
    # image = Column("image", String)
    author = Column("author", String)
    status = Column("status", String, default=None)


engine = create_engine(f"sqlite:///./Audiobook.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)
print("database is ready")
