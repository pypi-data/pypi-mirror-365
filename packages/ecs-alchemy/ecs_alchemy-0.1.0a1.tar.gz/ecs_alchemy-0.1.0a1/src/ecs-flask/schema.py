from sqlalchemy import create_engine, Column, String, DateTime, PrimaryKeyConstraint, text
from sqlalchemy.orm import declarative_base
import click

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entity'
    entity_id = Column(String(32), primary_key=True)
    create_ts = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

class Component(Base):
    __tablename__ = 'component'
    component_id = Column(String(32), primary_key=True)
    slug = Column(String(255))
    name = Column(String(255))
    tablename = Column(String(255))
    description = Column(String(255))

class EntityMComponent(Base):
    __tablename__ = 'entity_m_component'
    entity_id = Column(String(32))
    component_id = Column(String(32))
    component_data_id = Column(String(32))
    __table_args__ = (
        PrimaryKeyConstraint('entity_id', 'component_data_id'),
    )

@click.command()
@click.option("--db", default = 'sqlite:///mydatabase.db', help="Database URI")
def main(db):
    engine = create_engine('sqlite:///mydatabase.db')
    
    # Drop all existing tables
    Base.metadata.drop_all(engine)
    
    # Create new tables
    Base.metadata.create_all(engine)

# Usage example:
if __name__ == '__main__':
    main()