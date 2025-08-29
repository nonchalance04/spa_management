"""
Helper functions for working with the new service structure.
"""

from typing import List, Dict, Any
from ..models import ServiceCategory, Service, ServiceClassification, TransactionItem
from ..extensions import db


def get_services_by_category() -> Dict[str, List[Service]]:
    """
    Get all services grouped by category.
    
    Returns:
        Dictionary with category names as keys and lists of services as values.
    """
    services = Service.query.order_by(Service.service_name.asc()).all()
    categories = {}
    
    for service in services:
        category_name = service.category.category_name if service.category else "Uncategorized"
        if category_name not in categories:
            categories[category_name] = []
        categories[category_name].append(service)
    
    return categories


def get_service_with_classifications(service_id: int) -> Dict[str, Any]:
    """
    Get a service with all its classifications.
    
    Args:
        service_id: The ID of the service to retrieve.
        
    Returns:
        Dictionary containing service details and classifications.
    """
    service = Service.query.get_or_404(service_id)
    
    return {
        "id": service.id,
        "service_name": service.service_name,
        "description": service.description,
        "category": {
            "id": service.category.id,
            "category_name": service.category.category_name
        } if service.category else None,
        "classifications": [
            {
                "id": classification.id,
                "classification_name": classification.classification_name,
                "price": classification.price
            }
            for classification in service.classifications
        ]
    }


def create_transaction_item(transaction_id: int, service_classification_id: int, 
                          duration_minutes: int = 60) -> TransactionItem:
    """
    Create a transaction item for a service classification.
    
    Args:
        transaction_id: The ID of the transaction.
        service_classification_id: The ID of the service classification.
        duration_minutes: Duration of the service in minutes.
        
    Returns:
        The created TransactionItem instance.
    """
    classification = ServiceClassification.query.get_or_404(service_classification_id)
    
    transaction_item = TransactionItem(
        transaction_id=transaction_id,
        service_id=classification.service_id,
        service_classification_id=service_classification_id,
        price=classification.price,
        duration_minutes=duration_minutes
    )
    
    db.session.add(transaction_item)
    return transaction_item


def get_popular_services(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most popular services based on transaction items.
    
    Args:
        limit: Maximum number of services to return.
        
    Returns:
        List of popular services with their details.
    """
    # Query to get services ordered by usage count
    from sqlalchemy import func
    
    popular_services = db.session.query(
        Service,
        func.count(TransactionItem.id).label('usage_count')
    ).join(
        TransactionItem, Service.id == TransactionItem.service_id
    ).group_by(
        Service.id
    ).order_by(
        func.count(TransactionItem.id).desc()
    ).limit(limit).all()
    
    result = []
    for service, usage_count in popular_services:
        result.append({
            "id": service.id,
            "service_name": service.service_name,
            "description": service.description,
            "category": service.category.category_name if service.category else "Uncategorized",
            "usage_count": usage_count,
            "classifications": [
                {
                    "id": classification.id,
                    "classification_name": classification.classification_name,
                    "price": classification.price
                }
                for classification in service.classifications
            ]
        })
    
    return result


def search_services(query: str) -> List[Dict[str, Any]]:
    """
    Search for services by name or description.
    
    Args:
        query: Search query string.
        
    Returns:
        List of matching services with their details.
    """
    services = Service.query.filter(
        db.or_(
            Service.service_name.ilike(f'%{query}%'),
            Service.description.ilike(f'%{query}%')
        )
    ).order_by(Service.service_name.asc()).all()
    
    result = []
    for service in services:
        result.append({
            "id": service.id,
            "service_name": service.service_name,
            "description": service.description,
            "category": service.category.category_name if service.category else "Uncategorized",
            "classifications": [
                {
                    "id": classification.id,
                    "classification_name": classification.classification_name,
                    "price": classification.price
                }
                for classification in service.classifications
            ]
        })
    
    return result
