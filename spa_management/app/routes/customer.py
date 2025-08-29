from flask import Blueprint, render_template, jsonify
from ..extensions import db
from ..models import Service, ServiceCategory, ServiceClassification, Therapist, Cashier

customer_bp = Blueprint("customer", __name__)


# @customer_bp.get("/")
# @customer_bp.get("/customer/")
# def customer_page():
#     services = Service.query.filter_by(active=True).order_by(Service.name.asc()).all()
#     categories: dict[str, list[Service]] = {}
#     for s in services:
#         cat_name = s.category.name if s.category else "Uncategorized"
#         categories.setdefault(cat_name, []).append(s)
#     return render_template("customer2.html", services=services, categories=categories)

@customer_bp.get("/")
def home_page():
    services = Service.query.order_by(Service.service_name.asc()).all()
    categories: dict[str, list[Service]] = {}
    for s in services:
        cat_name = s.category.category_name if s.category else "Uncategorized"
        categories.setdefault(cat_name, []).append(s)
    return render_template("home.html", services=services, categories=categories)

@customer_bp.get("/about")
def about_age():
    return render_template("about.html")

# Experimental link for service 2 page
@customer_bp.get("/services1")
def customer_page1():
    services = Service.query.order_by(Service.service_name.asc()).all()
    categories: dict[str, list[Service]] = {}
    for s in services:
        cat_name = s.category.category_name if s.category else "Uncategorized"
        categories.setdefault(cat_name, []).append(s)
    return render_template("services1.html", services=services, categories=categories)

@customer_bp.get("/services2")
def customer_page2():
    services = Service.query.order_by(Service.service_name.asc()).all()
    categories: dict[str, list[Service]] = {}
    for s in services:
        cat_name = s.category.category_name if s.category else "Uncategorized"
        categories.setdefault(cat_name, []).append(s)
    return render_template("services2.html", services=services, categories=categories)


# API ginagamit ni therapist page para kuhain yung data sa services table ng database
@customer_bp.get("/api/services")
def api_services():
    services = Service.query.order_by(Service.service_name.asc()).all()
    result = []
    for s in services:
        for classification in s.classifications:
            result.append({
                "id": s.id,
                "classification_id": classification.id,
                "name": s.service_name,
                "classification_name": classification.classification_name,
                "price": classification.price,
                "duration_minutes": classification.duration_minutes,
                "category": s.category.category_name if s.category else "Uncategorized",
                "description": s.description or "No description available"
            })
    return jsonify(result)

# API to get service classifications for a specific service
@customer_bp.get("/api/services/<int:service_id>/classifications")
def api_service_classifications(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify([
        {
            "id": classification.id,
            "classification_name": classification.classification_name,
            "price": classification.price,
            "duration_minutes": classification.duration_minutes,
            "service_name": service.service_name,
            "category": service.category.category_name if service.category else "Uncategorized"
        }
        for classification in service.classifications
    ])

# API to get all service categories
@customer_bp.get("/api/categories")
def api_categories():
    categories = ServiceCategory.query.order_by(ServiceCategory.category_name.asc()).all()
    return jsonify([
        {
            "id": category.id,
            "category_name": category.category_name,
            "services_count": len(category.services)
        }
        for category in categories
    ])

# Panlagay ng dummy datas sa tables ng database: services, therapist, cashier tables
# @customer_bp.get("/initdb/")
# def initdb():
#     db.drop_all()
#     db.create_all()

#     # Seed service categories first
#     categories_data = [
#         "Signature Massage",
#         "Supplementary", 
#         "Holistic Recovery",
#     ]
    
#     categories = {}
#     for name in categories_data:
#         cat = ServiceCategory(category_name=name)
#         db.session.add(cat)
#         db.session.flush()  # Get the ID
#         categories[name] = cat.id

#     # Seed services with classifications
#     services_data = [
#         {
#             "service_name": "Accupressure",
#             "description": "Traditional pressure point massage",
#             "category": "Signature Massage",
#             "classifications": [
#                 {"classification_name": "Full Back", "price": 40.0, "duration_minutes": 45},
#                 {"classification_name": "Full Body", "price": 65.0, "duration_minutes": 60}
#             ]
#         },
#         {
#             "service_name": "Foot Reflexology",
#             "description": "Therapeutic foot massage",
#             "category": "Supplementary",
#             "classifications": [
#                 {"classification_name": "30 minutes", "price": 20.0, "duration_minutes": 30}
#             ]
#         },
#         {
#             "service_name": "Hot Stone Massage",
#             "description": "Relaxing massage with heated stones",
#             "category": "Holistic Recovery",
#             "classifications": [
#                 {"classification_name": "60 minutes", "price": 55.0, "duration_minutes": 60}
#             ]
#         },
#         {
#             "service_name": "Facial Treatment",
#             "description": "Rejuvenating facial therapy",
#             "category": "Holistic Recovery",
#             "classifications": [
#                 {"classification_name": "45 minutes", "price": 35.0, "duration_minutes": 45}
#             ]
#         }
#     ]
    
#     for service_data in services_data:
#         category_id = categories.get(service_data["category"])
#         service = Service(
#             category_id=category_id,
#             service_name=service_data["service_name"],
#             description=service_data["description"]
#         )
#         db.session.add(service)
#         db.session.flush()  # Get the ID
        
#         for class_data in service_data["classifications"]:
#             classification = ServiceClassification(
#                 service_id=service.id,
#                 classification_name=class_data["classification_name"],
#                 price=class_data["price"],
#                 duration_minutes=class_data.get("duration_minutes", 60)
#             )
#             db.session.add(classification)

#     # Seed therapists with credentials
#     t1 = Therapist(username="thera1", name="Therapist 1", room_number="101")
#     t1.set_password("pass123")
#     t2 = Therapist(username="thera2", name="Therapist 2", room_number="102")
#     t2.set_password("pass123")
#     db.session.add_all([t1, t2])

#     # Seed cashiers with credentials
#     c1 = Cashier(username="cash1", name="Cashier 1", counter_number="1")
#     c1.set_password("pass123")
#     c2 = Cashier(username="cash2", name="Cashier 2", counter_number="2")
#     c2.set_password("pass123")
#     db.session.add_all([c1, c2])

#     db.session.commit()
#     return "Database initialized and seeded with new service structure. Visit /login/therapist and /login/cashier", 200
