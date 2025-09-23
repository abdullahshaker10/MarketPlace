"""
Product Type Handlers - Following Open-Closed Principle

This module demonstrates how to handle different product types
without violating the Open-Closed Principle using a registry pattern.

Open for extension: Easy to add new product types
Closed for modification: Existing code doesn't need changes
"""

from abc import ABC, abstractmethod


class ProductTypeHandler(ABC):
    """
    Abstract base class for product type handlers
    
    Each product type should have its own handler that knows
    how to process data for that specific type.
    """
    
    @abstractmethod
    def get_type_name(self):
        """Return the product type name this handler supports"""
        pass
    
    @abstractmethod
    def process_form_data(self, form_data):
        """
        Process form data and return type-specific data dict
        
        Args:
            form_data: Dictionary of form data from POST request
            
        Returns:
            Dictionary of type-specific data for JSON field
        """
        pass
    
    @abstractmethod
    def get_display_info(self, product):
        """
        Get formatted display information for this product type
        
        Args:
            product: Product instance
            
        Returns:
            Formatted string for display
        """
        pass
    
    @abstractmethod
    def get_search_fields(self):
        """
        Return list of fields that can be searched for this product type
        
        Returns:
            List of field names
        """
        pass


class BookHandler(ProductTypeHandler):
    """Handler for book products"""
    
    def get_type_name(self):
        return 'book'
    
    def process_form_data(self, form_data):
        return {
            'author': form_data.get('author', ''),
            'isbn': form_data.get('isbn', ''),
            'pages': int(form_data.get('pages', 0)) if form_data.get('pages') else 0,
            'publisher': form_data.get('publisher', ''),
            'genre': form_data.get('genre', ''),
            'publication_year': int(form_data.get('publication_year', 0)) if form_data.get('publication_year') else 0,
        }
    
    def get_display_info(self, product):
        author = product.get_type_data('author', 'Unknown Author')
        return f"{product.name} by {author}"
    
    def get_search_fields(self):
        return ['author', 'isbn', 'publisher', 'genre']


class ElectronicsHandler(ProductTypeHandler):
    """Handler for electronics products"""
    
    def get_type_name(self):
        return 'electronics'
    
    def process_form_data(self, form_data):
        return {
            'brand': form_data.get('brand', ''),
            'model': form_data.get('model', ''),
            'warranty_months': int(form_data.get('warranty_months', 0)) if form_data.get('warranty_months') else 0,
            'specifications': form_data.get('specifications', ''),
            'power_consumption': form_data.get('power_consumption', ''),
            'connectivity': form_data.get('connectivity', ''),
        }
    
    def get_display_info(self, product):
        brand = product.get_type_data('brand', 'Unknown Brand')
        model = product.get_type_data('model', '')
        return f"{brand} {model}".strip()
    
    def get_search_fields(self):
        return ['brand', 'model', 'specifications']


class ClothingHandler(ProductTypeHandler):
    """Handler for clothing products"""
    
    def get_type_name(self):
        return 'clothing'
    
    def process_form_data(self, form_data):
        return {
            'size': form_data.get('size', ''),
            'color': form_data.get('color', ''),
            'material': form_data.get('material', ''),
            'gender': form_data.get('gender', ''),
            'season': form_data.get('season', ''),
            'care_instructions': form_data.get('care_instructions', ''),
        }
    
    def get_display_info(self, product):
        color = product.get_type_data('color', '')
        size = product.get_type_data('size', '')
        return f"{product.name} - {color} {size}".strip()
    
    def get_search_fields(self):
        return ['color', 'material', 'size', 'gender']


class ProductTypeRegistry:
    """
    Registry for product type handlers
    
    This class follows the Open-Closed Principle:
    - Open for extension: New handlers can be registered
    - Closed for modification: No need to modify existing code
    """
    
    def __init__(self):
        self._handlers = {}
    
    def register_handler(self, handler):
        """
        Register a product type handler
        
        Args:
            handler: Instance of ProductTypeHandler
        """
        type_name = handler.get_type_name()
        self._handlers[type_name] = handler
        print(f"✅ Registered handler for product type: {type_name}")
    
    def get_handler(self, product_type_name):
        """
        Get handler for a product type
        
        Args:
            product_type_name: Name of the product type
            
        Returns:
            ProductTypeHandler instance or None if not found
        """
        return self._handlers.get(product_type_name)
    
    def get_all_handlers(self):
        """Get all registered handlers"""
        return self._handlers.copy()
    
    def get_supported_types(self):
        """Get list of all supported product type names"""
        return list(self._handlers.keys())
    
    def process_product_data(self, product_type_name, form_data):
        """
        Process form data using the appropriate handler
        
        Args:
            product_type_name: Name of the product type
            form_data: Form data from POST request
            
        Returns:
            Dictionary of processed type-specific data
        """
        handler = self.get_handler(product_type_name)
        if handler:
            return handler.process_form_data(form_data)
        else:
            # Fallback for unknown types - still open for extension!
            print(f"⚠️ No handler found for product type: {product_type_name}")
            return {}
    
    def get_display_info(self, product):
        """
        Get display info using the appropriate handler
        
        Args:
            product: Product instance
            
        Returns:
            Formatted display string
        """
        handler = self.get_handler(product.product_type.name)
        if handler:
            return handler.get_display_info(product)
        else:
            # Fallback for unknown types
            return product.name


# Create global registry instance
product_registry = ProductTypeRegistry()

# Register default handlers (this can be done in apps.py or anywhere)
product_registry.register_handler(BookHandler())
product_registry.register_handler(ElectronicsHandler())
product_registry.register_handler(ClothingHandler())


# Example of extending without modifying existing code!
class ToysHandler(ProductTypeHandler):
    """
    Example: Adding a new product type without modifying existing code
    This demonstrates the Open-Closed Principle in action!
    """
    
    def get_type_name(self):
        return 'toys'
    
    def process_form_data(self, form_data):
        return {
            'age_range': form_data.get('age_range', ''),
            'safety_rating': form_data.get('safety_rating', ''),
            'material': form_data.get('material', ''),
            'battery_required': form_data.get('battery_required', 'No'),
            'educational_value': form_data.get('educational_value', ''),
        }
    
    def get_display_info(self, product):
        age_range = product.get_type_data('age_range', '')
        return f"{product.name} (Ages {age_range})" if age_range else product.name
    
    def get_search_fields(self):
        return ['age_range', 'material', 'educational_value']

# Register the new handler (can be done anywhere without modifying existing code!)
# product_registry.register_handler(ToysHandler())