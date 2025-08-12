#!/usr/bin/env python3
"""
Database migration script for adding Pipeline tables to existing DataVein database.
Run this to add the new Pipeline and PipelineEvent tables.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.database import engine
from backend.app.models import Pipeline, PipelineEvent
from sqlalchemy import text

def run_migration():
    """Add Pipeline and PipelineEvent tables to existing database"""
    
    print("Starting database migration...")
    
    try:
        # Check if tables already exist
        with engine.connect() as conn:
            # Check for Pipeline table
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'pipelines'
            """))
            pipeline_exists = result.fetchone() is not None
            
            # Check for PipelineEvent table
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'pipeline_events'
            """))
            events_exists = result.fetchone() is not None
        
        if pipeline_exists and events_exists:
            print("Pipeline tables already exist. No migration needed.")
            return
        
        # Create the new tables
        print("Creating Pipeline and PipelineEvent tables...")
        Pipeline.__table__.create(engine, checkfirst=True)
        PipelineEvent.__table__.create(engine, checkfirst=True)
        
        print("Migration completed successfully!")
        print("New tables created:")
        print("- pipelines")
        print("- pipeline_events")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()
