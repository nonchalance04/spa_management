# Service Structure Changes Documentation

## Overview
The spa management system has been updated with a new three-tier service structure that provides better flexibility and organization for service offerings.

## New Database Schema

### ServiceCategory
- **Table**: `service_categories`
- **Purpose**: Top-level categorization of services
- **Fields**:
  - `id`: Primary key (auto-increment)
  - `category_name`: Unique category name (e.g., "Massage Therapy", "Facial Treatments")

### Service
- **Table**: `services`
- **Purpose**: Individual service offerings within categories
- **Fields**:
  - `id`: Primary key (auto-increment)
  - `category_id`: Foreign key to `service_categories`
  - `service_name`: Name of the service
  - `description`: Detailed description of the service

### ServiceClassification
- **Table**: `service_classifications`
- **Purpose**: Specific variations/pricing tiers for each service
- **Fields**:
  - `id`: Primary key (auto-increment)
  - `service_id`: Foreign key to `services`
  - `classification_name`: Variation name (e.g., "30 minutes", "Full Body", "Premium")
  - `price`: Price for this specific classification

## Updated Models

### TransactionItem Updates
- Added `service_classification_id` field to reference specific pricing
- Maintains backward compatibility with existing `service_id` field
- Price is now sourced from `ServiceClassification` table

## API Endpoints

### New Endpoints
1. **GET `/api/services`** - Returns all services with their classifications
2. **GET `/api/services/<id>/classifications`** - Get classifications for a specific service
3. **GET `/api/categories`** - Get all service categories

### Updated Endpoints
- All existing service endpoints now work with the new structure
- Service data includes classification information

## Migration and Seeding

### Migration Script
- **File**: `scripts/migrate_services.py`
- **Purpose**: Migrate existing data to new structure
- **Usage**: Run to convert old category/service data

### Seed Script
- **File**: `scripts/seed.py`
- **Purpose**: Populate database with comprehensive sample data
- **Includes**: 4 categories, 8 services, multiple classifications each

### Quick Setup
- **File**: `/initdb/` endpoint in customer routes
- **Purpose**: Quick database reset and seeding for development

## Helper Functions

### Service Helpers
- **File**: `app/utils/service_helpers.py`
- **Functions**:
  - `get_services_by_category()`: Group services by category
  - `get_service_with_classifications()`: Get service with all pricing options
  - `create_transaction_item()`: Create transaction items with classifications
  - `get_popular_services()`: Analytics for popular services
  - `search_services()`: Search functionality

## Usage Examples

### Creating a New Service Structure
```python
# Create category
category = ServiceCategory(category_name="Wellness Services")
db.session.add(category)
db.session.commit()

# Create service
service = Service(
    category_id=category.id,
    service_name="Aromatherapy",
    description="Relaxing essential oil therapy"
)
db.session.add(service)
db.session.commit()

# Create classifications
classifications = [
    ServiceClassification(
        service_id=service.id,
        classification_name="30 minutes",
        price=60.0
    ),
    ServiceClassification(
        service_id=service.id,
        classification_name="60 minutes",
        price=100.0
    )
]
for classification in classifications:
    db.session.add(classification)
db.session.commit()
```

### Creating Transaction Items
```python
from app.utils.service_helpers import create_transaction_item

# Create transaction item with specific classification
transaction_item = create_transaction_item(
    transaction_id=transaction.id,
    service_classification_id=classification.id,
    duration_minutes=60
)
db.session.commit()
```

### Querying Services
```python
# Get all services grouped by category
categories = get_services_by_category()

# Get service with all pricing options
service_details = get_service_with_classifications(service_id)

# Search for services
results = search_services("massage")
```

## Benefits of New Structure

1. **Flexible Pricing**: Multiple price points per service
2. **Better Organization**: Clear hierarchy (Category → Service → Classification)
3. **Scalability**: Easy to add new variations without schema changes
4. **Analytics**: Better tracking of popular service variations
5. **User Experience**: Customers can choose from multiple options per service

## Files Modified

1. **`app/models.py`** - Updated with new service models
2. **`app/routes/customer.py`** - Updated API endpoints and views
3. **`scripts/migrate_services.py`** - New migration script
4. **`scripts/seed.py`** - Updated seed script
5. **`app/utils/service_helpers.py`** - New helper functions
6. **`test_service_structure.py`** - Test script for verification

## Next Steps

1. Run migration script if upgrading existing database
2. Update frontend templates to display classifications
3. Test transaction flow with new service structure
4. Update any custom queries to use new field names

## Testing

Run the test script to verify everything works:
```bash
python test_service_structure.py
```

Or use the quick setup endpoint:
```
GET /initdb/
```
