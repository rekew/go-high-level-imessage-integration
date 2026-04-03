from sqlalchemy import Column, Integer, String
from .base import Base


class PitConfig(Base):
    __tablename__ = "pit_config"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, nullable=False, unique=True)  # просто поле
    pit_token = Column(String(1024), nullable=False)