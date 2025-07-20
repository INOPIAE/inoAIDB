from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Index, Table
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
    expire = Column(DateTime(timezone=True), nullable=True)
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
    duration_month = Column(Integer, default=0)
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

    __table_args__ = (
        Index('ix_manufacturer_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
    )


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

    areas = relationship("ApplicationArea", secondary="application_area_entry", back_populates="applications")

    __table_args__ = (
        Index('ix_application_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
    )

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
    risk_id = Column(Integer, ForeignKey("risk.id"), nullable=True)

    applications = relationship("Application")
    user = relationship("User")

class Risk(Base):
    __tablename__ = "risk"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sort = Column(Integer, nullable=True)

    application_users = relationship("ApplicationUser")

class PaymentToken(Base):
    __tablename__ = "payment_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    token = Column(String, unique=True, nullable=False)
    duration = Column(Integer, default=0)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User")

class ApplicationArea(Base):
    __tablename__ = "application_area"
    id = Column(Integer, primary_key=True)
    area = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    applications = relationship("Application", secondary="application_area_entry", back_populates="areas")

application_area_entry_table = Table(
    'application_area_entry',
    Base.metadata,
    Column('application_id', ForeignKey('applications.id'), primary_key=True),
    Column('area_id', ForeignKey('application_area.id'), primary_key=True)
)
