from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine("sqlite:///res/videos.db", echo=True, connect_args={"check_same_thread": False})

class Video(Base):
    __tablename__ = "video"

    id = Column(String(11), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String)
    thumbnail = Column(String)
    transcoded_text = Column(String)

    def __repr__(self):
        return f"""Video(id={self.id!r}, created_at={self.created_at!r}, name={self.name!r},
        thumbnail={self.thumbnail!r}, transcoded_text={self.transcoded_text!r})"""

def generate_schema():
    Base.metadata.create_all(engine)

def get_conn():
    connection = engine.connect()
    return connection
