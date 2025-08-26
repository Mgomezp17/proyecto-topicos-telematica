from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)  # Ruta completa del archivo
    size = Column(BigInteger, nullable=False)  # Tamaño en bytes
    block_size = Column(Integer, nullable=False)  # Tamaño de bloque configurado
    num_blocks = Column(Integer, nullable=False)  # Número de bloques
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    owner = relationship("User", back_populates="files")
    blocks = relationship("Block", back_populates="file", cascade="all, delete-orphan")
