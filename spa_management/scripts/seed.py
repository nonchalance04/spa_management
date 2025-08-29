#!/usr/bin/env python3
"""
Seed script to populate the database with sample data for the new service structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import ServiceCategory, Service, ServiceClassification, Therapist, Cashier

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create service categories
        categories_data = [
            {"category_name": "Signature Massage"},
            {"category_name": "Holistic Recovery"},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = ServiceCategory(**cat_data)
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        print(f"Created {len(categories)} service categories")
        
        # Create services and their classifications
        services_data = [
            {
                "category": categories[0],  # Signature Massage
                "service_name": "Acupressure",
                "description": "Channel the ancient healing power of China with this acupressure massage. Targeted pressure points stimulate energy meridians to promote deep relaxation and support overall wellness. No oil used.",
                "classifications": [
                    {"classification_name": "(Full Back)", "price": 1300.00, "duration_minutes": 60},
                    {"classification_name": "(Full Body)", "price": 1950.00, "duration_minutes": 90},
                    {"classification_name": "(Full Body)", "price": 2500.00, "duration_minutes": 120}
                ]
            },
            {
                "category": categories[0],  # Signature Massage
                "service_name": "The Shiatsu",
                "description": "Harnessing the wisdom of Japanese rhythmic finger pressure along energy meridians, this treatment promotes deep relaxation, improves circulation, and restores balance to your mind and body.",
                "classifications": [
                    {"classification_name": "(Full Back)", "price": 1200.00, "duration_minutes": 60},
                    {"classification_name": "(Full Body)", "price": 1800.00, "duration_minutes": 90},
                    {"classification_name": "(Full Body)", "price": 2300.00, "duration_minutes": 120}
                ]
            },
            {
                "category": categories[0],  # Signature Massage
                "service_name": "The Swedish",
                "description": "Massage using heated stones for deep relaxation",
                "classifications": [
                    {"classification_name": "(Full Back)", "price": 1200.00, "duration_minutes": 60},
                    {"classification_name": "(Full Body)", "price": 1800.00, "duration_minutes": 90},
                    {"classification_name": "(Full Body)", "price": 2300.00, "duration_minutes": 120}
                ]
            },
            {
                "category": categories[0],  # Signature Massage
                "service_name": "Foot Massage",
                "description": "Unwind and revitalize with a luxurious foot massage. Targeted pressure points and tired muscles, easing tension, promoting circulation, and leaving you feeling refreshed and rejuvenated.",
                "classifications": [
                    {"classification_name": "(Foot Only)", "price": 888.00, "duration_minutes": 60},
                    {"classification_name": "(+ Shoulder)", "price": 1250.00, "duration_minutes": 90},
                    {"classification_name": "(+ Shoulder)", "price": 1600.00, "duration_minutes": 120}
                ]
            },
            {
                "category": categories[1],  # Holistic Recovery
                "service_name": "Myofascial Release",
                "description": "Focuses on the constant rehabilitation of your myofascial tissues. This physical rehabilitation is recommended if you're experiencing muscle tightness, joint stiffness, or lack of mobility.",
                "classifications": [
                    {"classification_name": "(Total Body)", "price": 2800.00, "duration_minutes": 80},
                    {"classification_name": "(Upper Body)", "price": 2000.00, "duration_minutes": 60},
                    {"classification_name": "(Lower Body)", "price": 2000.00, "duration_minutes": 60}
                ]
            },
            {
                "category": categories[1],  # Holistic Recovery
                "service_name": "Cupping Therapy",
                "description": "Special suction cups are placed on the skin to draw blood to or away from your body. Alleviates muscle soreness and tightness, for better physical movement and better blood circulation.",
                "classifications": [
                    {"classification_name": "(Total Body)", "price": 2500.00, "duration_minutes": 80},
                    {"classification_name": "(Upper Body)", "price": 2100.00, "duration_minutes": 60},
                    {"classification_name": "(Lower Body)", "price": 2100.00, "duration_minutes": 60}
                ]
            },
            {
                "category": categories[1],  # Holistic Recovery
                "service_name": "Sports Massage",
                "description": "Pre-event sports massage focuses on preparing the body for performance, while post-event sports massage aids recovery. Helping to maximize performance and minimize the risk of injury.",
                "classifications": [
                    {"classification_name": "(Pre-event)", "price": 1800.00, "duration_minutes": 60},
                    {"classification_name": "(Post-event)", "price": 1800.00, "duration_minutes": 60}
                ]
            },
            {
                "category": categories[1],  # Holistic Recovery
                "service_name": "Assessment",
                "description": "In-house professional will evaluate the effectiveness of our treatments, identify areas for improvement, and ensure we provide the highest level of care tailored to your needs.",
                "classifications": [
                    {"classification_name": "(Reoccurring)", "price": 500.00, "duration_minutes": 15},
                    {"classification_name": "(First Time)", "price": 0.00, "duration_minutes": 15}
                ]
            }
        ]
        
        for service_data in services_data:
            service = Service(
                category_id=service_data["category"].id,
                service_name=service_data["service_name"],
                description=service_data["description"]
            )
            db.session.add(service)
            db.session.flush()  # Get the ID
            
            for class_data in service_data["classifications"]:
                classification = ServiceClassification(
                    service_id=service.id,
                    classification_name=class_data["classification_name"],
                    price=class_data["price"],
                    duration_minutes=class_data["duration_minutes"]
                )
                db.session.add(classification)
        
        db.session.commit()
        print(f"Created {len(services_data)} services with their classifications")
        
        # Create sample therapists
        therapists_data = [
            {"username": "therapist1", "name": "Sarah Johnson", "room_number": "101"},
            {"username": "therapist2", "name": "Michael Chen", "room_number": "102"},
            {"username": "therapist3", "name": "Emma Davis", "room_number": "103"},
            {"username": "therapist4", "name": "David Wilson", "room_number": "104"}
        ]
        
        for therapist_data in therapists_data:
            therapist = Therapist(**therapist_data)
            therapist.set_password("password123")  # Default password
            db.session.add(therapist)
        
        db.session.commit()
        print(f"Created {len(therapists_data)} therapists")
        
        # Create sample cashiers
        cashiers_data = [
            {"username": "cashier1", "name": "Lisa Anderson", "counter_number": "C1"},
            {"username": "cashier2", "name": "Robert Taylor", "counter_number": "C2"}
        ]
        
        for cashier_data in cashiers_data:
            cashier = Cashier(**cashier_data)
            cashier.set_password("password123")  # Default password
            db.session.add(cashier)
        
        db.session.commit()
        print(f"Created {len(cashiers_data)} cashiers")
        
        print("Database seeding completed successfully!")
        print("\nSample data created:")
        print("- 4 service categories")
        print("- 8 services with multiple classifications each")
        print("- 4 therapists (username: therapist1-4, password: password123)")
        print("- 2 cashiers (username: cashier1-2, password: password123)")

if __name__ == "__main__":
    seed_database()