"""
A library of CRUD (Create/Read/Update/Delete) operations.
Facilitates communication between Web App an DB for odnd.tools.
"""

### IMPORTS ###
from uuid import uuid4
import sqlite3
from datetime import datetime

import click
from flask import current_app, g

from ecs.db import get_db


### Entity ###
def create_entity():
    entity_id = str(uuid4())
    db = get_db()
    insert_stmt = """
        INSERT INTO entity (entity_id)
        VALUES (?)
    """

    db.execute(insert_stmt, (entity_id,))
    db.commit()

    return entity_id

### Component ###
def create_component(slug, name, tablename, description):
    component_id = str(uuid4())
    db = get_db()
    insert_stmt = """
        INSERT INTO component (component_id, slug, name, tablename, description)
        VALUES (?, ?, ?, ?, ?)
    """

    db.execute(insert_stmt, (component_id, slug, name, tablename, description))
    db.commit()

    return component_id

def read_component(slug):
    db = get_db()
    fetch_stmt = """
        SELECT slug, component_id, name, description
        FROM component
        WHERE slug = ?
    """
    return dict(db.execute(fetch_stmt, (slug,)).fetchone())

### Component Data ###   
def create_component_data(slug, component_data_dict):
    """
    Params:
    slug - The slug of the component whose data is being added.
    component_data_dict - A dictionary consisting of:
        an entry for each required data column in the component_data table
        an entry for any additional columns to be populated

    Output:
    [component]_data_id in the appropriate table
    """
    id = str(uuid4())
    db = get_db()

    fetch_tablename_stmt = "SELECT tablename FROM component WHERE slug = ?"
    tablename = db.execute(fetch_tablename_stmt, (slug,)).fetchone()[0]     
    id_column = tablename + "_id"

    # Add ID to the component data dict
    data_with_id = {id_column: id}
    data_with_id.update(component_data_dict)
    
    # Correctly format column names and placeholders
    columns_str = ",".join(data_with_id.keys())
    placeholders_str = ",".join(["?" for _ in range(len(data_with_id))])
    
    insert_stmt = f"""
        INSERT INTO {tablename} ({columns_str})
        VALUES ({placeholders_str})
    """

    insert_params = tuple(data_with_id.values())

    db.execute(insert_stmt, insert_params)
    db.commit()
    
    return id

def map_entity_component(entity_id, component_id, component_data_id):
    """
    Associate the given entity with the given data component in the DB
    """
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO entity_m_component (entity_id, component_id, component_data_id)
            VALUES( ?, ?, ? )
            """, (str(entity_id), str(component_id), str(component_data_id))
        )
        db.commit()

    except Exception as e:
        print(f"Error during mapping: {str(e)}")
        db.rollback()
        raise e