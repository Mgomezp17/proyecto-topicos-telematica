from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(String, unique=True, index=True, nullable=False)  # ID único del bloque
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    block_index = Column(Integer, nullable=False)  # Índice del bloque en el archivo
    size = Column(BigInteger, nullable=False)  # Tamaño del bloque en bytes
    datanode_url = Column(String, nullable=False)  # URL del DataNode donde está almacenado
    checksum = Column(String, nullable=False)  # Checksum del bloque para verificación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    file = relationship("File", back_populates="blocks")
