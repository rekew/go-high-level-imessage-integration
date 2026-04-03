from .base import Base
from sqlalchemy import Column, Integer, Text, ForeignKey


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True)

    location_id = Column(
        Text,
        ForeignKey("pit_config.location_id"),
        nullable=False
    )

    email = Column(Text, nullable=True)
    phone_number = Column(Text, nullable=True)