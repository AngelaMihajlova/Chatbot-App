import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    indexed = "indexed"
    error = "error"


class GroupRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    documents = relationship("Document", back_populates="uploader")
    group_memberships = relationship("UserGroup", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    members = relationship("UserGroup", back_populates="group")
    document_groups = relationship("DocumentGroup", back_populates="group")


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    role = Column(Enum(GroupRole), default=GroupRole.member, nullable=False)

    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False, unique=True)
    mimetype = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.pending, nullable=False)
    error_message = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    uploader = relationship("User", back_populates="documents")
    document_groups = relationship("DocumentGroup", back_populates="document")


class DocumentGroup(Base):
    __tablename__ = "document_groups"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)

    document = relationship("Document", back_populates="document_groups")
    group = relationship("Group", back_populates="document_groups")


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
