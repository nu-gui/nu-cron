from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # developer, tech_lead, project_manager
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    requirements = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User")

class AILog(Base):
    __tablename__ = "ai_logs"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)  # GPT-4, Claude, Mistral
    prompt = Column(String)
    response = Column(String)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project")

class VectorStore(Base):
    __tablename__ = "vector_store"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(JSON)  # Store vector embeddings
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project")

class Environment(Base):
    """Environment model for tracking development environments."""
    __tablename__ = "environments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    env_type = Column(String)  # docker or kubernetes
    status = Column(String)  # active, inactive, failed
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database initialization function
def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
