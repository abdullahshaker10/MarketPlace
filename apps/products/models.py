from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductType(models.Model):
    """
    Simple lookup table for product types
    
    Open-Closed Principle: New types can be added as data without code changes
    """
    name = models.CharField(max_length=50, unique=True)  # 'book', 'electronics', 'clothing'
    display_name = models.CharField(max_length=100)      # 'Books', 'Electronics', 'Clothing'
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_types'
    
    def __str__(self):
        return self.display_name


class Product(models.Model):
    """
    Clean product model using JSON field for type-specific data
    
    Supports 3 product types: Book, Electronics, Clothing
    Type-specific details are stored in JSON field.
    """
    
    # Core product attributes
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Type-specific data stored as JSON
    type_specific_data = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['product_type', 'is_active']),
            models.Index(fields=['is_active']),
        ]
    
    def get_type_data(self, field_name, default=None):
        """
        Safely get a field from type-specific data
        """
        return self.type_specific_data.get(field_name, default)
    
    def set_type_data(self, field_name, value):
        """
        Set a field in type-specific data
        """
        self.type_specific_data[field_name] = value
    
    def get_display_info(self):
        """
        Get formatted display information using registry pattern
        """
        from .type_handlers import product_registry
        return product_registry.get_display_info(self)
    
    @classmethod
    def get_by_id_with_data(cls, product_id):
        """
        Get product by ID (JSON data is always loaded with the product)
        """
        try:
            return cls.objects.select_related('product_type').get(id=product_id)
        except cls.DoesNotExist:
            return None
    
    def __str__(self):
        return f"{self.name} ({self.product_type.display_name})"