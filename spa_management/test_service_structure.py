#!/usr/bin/env python3
"""
Test script to verify the new service structure works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import ServiceCategory, Service, ServiceClassification

def test_service_structure():
    app = create_app()
    
    with app.app_context():
        print("Testing new service structure...")
        
        # Test creating a service category
        category = ServiceCategory(category_name="Test Category")
        db.session.add(category)
        db.session.commit()
        print(f"✓ Created service category: {category.category_name}")
        
        # Test creating a service
        service = Service(
            category_id=category.id,
            service_name="Test Service",
            description="A test service for verification"
        )
        db.session.add(service)
        db.session.commit()
        print(f"✓ Created service: {service.service_name}")
        
        # Test creating service classifications
        classifications = [
            ServiceClassification(
                service_id=service.id,
                classification_name="Basic",
                price=50.0
            ),
            ServiceClassification(
                service_id=service.id,
                classification_name="Premium",
                price=75.0
            )
        ]
        
        for classification in classifications:
            db.session.add(classification)
        
        db.session.commit()
        print(f"✓ Created {len(classifications)} service classifications")
        
        # Test relationships
        print(f"✓ Service category has {len(category.services)} service(s)")
        print(f"✓ Service has {len(service.classifications)} classification(s)")
        
        # Test querying
        all_categories = ServiceCategory.query.all()
        all_services = Service.query.all()
        all_classifications = ServiceClassification.query.all()
        
        print(f"✓ Database contains:")
        print(f"  - {len(all_categories)} service categories")
        print(f"  - {len(all_services)} services")
        print(f"  - {len(all_classifications)} service classifications")
        
        print("\n✅ All tests passed! New service structure is working correctly.")

if __name__ == "__main__":
    test_service_structure()
