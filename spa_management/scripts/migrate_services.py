#!/usr/bin/env python3
"""
Migration script to update the database schema for the new service structure.
This script will:
1. Create new service_categories, services, and service_classifications tables
2. Migrate existing data from categories and services tables
3. Update transaction_items to reference service_classifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import ServiceCategory, Service, ServiceClassification, TransactionItem
from sqlalchemy import text

def migrate_services():
    app = create_app()
    
    with app.app_context():
        print("Starting service migration...")
        
        # Create new tables
        print("Creating new service tables...")
        db.create_all()
        
        # Check if old tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'categories' in existing_tables and 'services' in existing_tables:
            print("Migrating data from old tables...")
            
            # Migrate categories to service_categories
            old_categories = db.session.execute(text("SELECT * FROM categories")).fetchall()
            for cat in old_categories:
                new_category = ServiceCategory(
                    category_name=cat.name
                )
                db.session.add(new_category)
            
            db.session.commit()
            print(f"Migrated {len(old_categories)} categories")
            
            # Migrate services
            old_services = db.session.execute(text("SELECT * FROM services")).fetchall()
            for svc in old_services:
                # Find corresponding new category
                if svc.category_id:
                    old_cat = db.session.execute(text("SELECT name FROM categories WHERE id = :id"), 
                                               {"id": svc.category_id}).fetchone()
                    new_category = ServiceCategory.query.filter_by(category_name=old_cat.name).first()
                    category_id = new_category.id if new_category else None
                else:
                    category_id = None
                
                if category_id:
                    new_service = Service(
                        category_id=category_id,
                        service_name=svc.name,
                        description=f"Migrated service: {svc.name}"
                    )
                    db.session.add(new_service)
                    db.session.flush()  # Get the ID
                    
                    # Create a default classification for this service
                    classification = ServiceClassification(
                        service_id=new_service.id,
                        classification_name=svc.classification or "Standard",
                        price=svc.price
                    )
                    db.session.add(classification)
            
            db.session.commit()
            print(f"Migrated {len(old_services)} services")
            
            # Update transaction_items to reference service_classifications
            print("Updating transaction items...")
            transaction_items = db.session.execute(text("SELECT * FROM transaction_items")).fetchall()
            
            for item in transaction_items:
                # Find the corresponding service classification
                old_service = db.session.execute(text("SELECT name FROM services WHERE id = :id"), 
                                               {"id": item.service_id}).fetchone()
                if old_service:
                    new_service = Service.query.filter_by(service_name=old_service.name).first()
                    if new_service and new_service.classifications:
                        classification = new_service.classifications[0]  # Use first classification
                        db.session.execute(
                            text("UPDATE transaction_items SET service_classification_id = :class_id WHERE id = :item_id"),
                            {"class_id": classification.id, "item_id": item.id}
                        )
            
            db.session.commit()
            print(f"Updated {len(transaction_items)} transaction items")
            
            print("Migration completed successfully!")
            
        else:
            print("No old tables found. Creating fresh schema...")
            print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_services()
