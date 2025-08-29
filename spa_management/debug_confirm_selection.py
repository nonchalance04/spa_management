#!/usr/bin/env python3
"""
Debug script to test the confirm selection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import ServiceCategory, Service, ServiceClassification, Transaction, TransactionItem

def debug_confirm_selection():
    app = create_app()
    
    with app.app_context():
        print("=== Debug Confirm Selection ===")
        
        # Check if we have services and classifications
        categories = ServiceCategory.query.all()
        services = Service.query.all()
        classifications = ServiceClassification.query.all()
        
        print(f"Categories: {len(categories)}")
        print(f"Services: {len(services)}")
        print(f"Classifications: {len(classifications)}")
        
        if not classifications:
            print("❌ No service classifications found! Run seed script first.")
            return
        
        # Test creating a transaction with classifications
        print("\n=== Testing Transaction Creation ===")
        
        # Simulate frontend data
        test_items = []
        for classification in classifications[:2]:  # Test with first 2 classifications
            test_items.append({
                "service_id": classification.service_id,
                "service_classification_id": classification.id
            })
            print(f"Test item: Service {classification.service.service_name} - {classification.classification_name} (₱{classification.price})")
        
        # Create transaction like the socket handler does
        tx = Transaction(customer_name="Test Customer", status="pending_therapist")
        db.session.add(tx)
        db.session.flush()
        
        for item in test_items:
            service_id = item.get("service_id")
            service_classification_id = item.get("service_classification_id")
            
            service = db.session.get(Service, int(service_id))
            if not service:
                print(f"❌ Service {service_id} not found")
                continue
            
            price = 0.0
            duration_minutes = 60
            
            if service_classification_id:
                classification = db.session.get(ServiceClassification, int(service_classification_id))
                if classification:
                    price = classification.price
                    print(f"✓ Found classification: {classification.classification_name} - ₱{price}")
                else:
                    print(f"❌ Classification {service_classification_id} not found")
            
            transaction_item = TransactionItem(
                transaction_id=tx.id,
                service_id=service.id,
                service_classification_id=service_classification_id,
                price=price,
                duration_minutes=duration_minutes,
            )
            db.session.add(transaction_item)
        
        tx.recompute_totals()
        tx.code = "TEST123"
        
        try:
            db.session.commit()
            print(f"✅ Transaction created successfully!")
            print(f"   Code: {tx.code}")
            print(f"   Total: ₱{tx.total_amount}")
            print(f"   Items: {len(tx.items)}")
            
            # Clean up test transaction
            db.session.delete(tx)
            db.session.commit()
            print("✅ Test transaction cleaned up")
            
        except Exception as e:
            print(f"❌ Error creating transaction: {e}")
            db.session.rollback()

if __name__ == "__main__":
    debug_confirm_selection()
