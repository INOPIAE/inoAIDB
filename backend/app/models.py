from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    totp_secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

#     auth_tokens = relationship("AuthToken", back_populates="user")

# class AuthToken(Base):
#     __tablename__ = 'auth_tokens'

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     token = Column(Text, nullable=False, unique=True)
#     created = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
#     expires = Column(TIMESTAMP(timezone=True), nullable=False)

#     user = relationship("User", back_populates="auth_tokens")

class AuthInvite(Base):
    __tablename__ = 'auth_invites'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    use_count = Column(Integer, default=0)
    use_max = Column(Integer, nullable=False, default=1)
    created = Column(DateTime(timezone=True), server_default=func.now())


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)
    applications = relationship("Application", back_populates="manufacturer", cascade="all, delete")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    languagemodel_id = Column(Integer, ForeignKey("language_models.id"))
    modelchoice_id = Column(Integer, ForeignKey("model_choices.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    is_active = Column(Boolean, default=True)

    manufacturer = relationship("Manufacturer", back_populates="applications")
    languagemodel = relationship("LanguageModel", back_populates="applications")
    modelchoice = relationship("ModelChoice", back_populates="applications")

class LanguageModel(Base):
    __tablename__ = "language_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    is_active = Column(Boolean, default=True)

    applications = relationship("Application", back_populates="languagemodel")


class ModelChoice(Base):
    __tablename__ = "model_choices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    applications = relationship("Application", back_populates="modelchoice")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    user = relationship("User")

class ApplicationUser(Base):
    __tablename__ = "application_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    selected = Column(Boolean, default=False)

    applications = relationship("Application")
    user = relationship("User")
