"""
Example usage demonstrating Open-Closed Principle with Product model

This shows:
1. Working with 3 existing product types (Book, Electronics, Clothing)
2. Adding a new product type (Toys) without modifying existing code
3. How the registry pattern follows Open-Closed Principle

Run this with: python manage.py shell < apps/products/example_usage.py
"""

from apps.products.models import Product, ProductType
from apps.products.type_handlers import product_registry, ToysHandler

print("🔧 Testing Open-Closed Principle Implementation")
print("=" * 50)

# Create product types if they don't exist
book_type, _ = ProductType.objects.get_or_create(
    name='book',
    defaults={'display_name': 'Books'}
)

electronics_type, _ = ProductType.objects.get_or_create(
    name='electronics', 
    defaults={'display_name': 'Electronics'}
)

clothing_type, _ = ProductType.objects.get_or_create(
    name='clothing',
    defaults={'display_name': 'Clothing'}
)

print("✅ Product types created")

# Show current registered handlers
print(f"\n📋 Currently supported types: {product_registry.get_supported_types()}")

# Create example products using the registry pattern
print("\n🏭 Creating products using registry pattern...")

# Simulate form data for each product type
book_form_data = {
    'author': 'J.K. Rowling',
    'isbn': '978-0439708180',
    'pages': '309',
    'publisher': 'Scholastic',
    'genre': 'Fantasy'
}

electronics_form_data = {
    'brand': 'Apple',
    'model': 'iPhone 15 Pro',
    'warranty_months': '12',
    'specifications': 'A17 Pro chip, 128GB storage',
    'connectivity': 'USB-C, 5G'
}

clothing_form_data = {
    'size': 'L',
    'color': 'Red',
    'material': '100% Cotton',
    'gender': 'Male',
    'season': 'Summer'
}

# Create products using the registry (this simulates the view logic)
book = Product.objects.create(
    name="Harry Potter",
    description="Fantasy novel",
    price=15.99,
    product_type=book_type
)
# Registry processes the form data
book.type_specific_data = product_registry.process_product_data('book', book_form_data)
book.save()

electronics = Product.objects.create(
    name="iPhone 15 Pro",
    description="Latest smartphone",
    price=999.99,
    product_type=electronics_type
)
electronics.type_specific_data = product_registry.process_product_data('electronics', electronics_form_data)
electronics.save()

clothing = Product.objects.create(
    name="Summer T-Shirt",
    description="Lightweight shirt",
    price=25.99,
    product_type=clothing_type
)
clothing.type_specific_data = product_registry.process_product_data('clothing', clothing_form_data)
clothing.save()

print("✅ Products created using registry pattern")

# Test display info using registry
print("\n📋 Product List (using registry for display):")
for product in Product.objects.all():
    print(f"- {product.get_display_info()} (${product.price})")
    print(f"  Type: {product.product_type.display_name}")
    print(f"  Data: {product.type_specific_data}")
    print()

# NOW DEMONSTRATE OPEN-CLOSED PRINCIPLE!
print("\n🎯 OPEN-CLOSED PRINCIPLE DEMONSTRATION")
print("=" * 50)
print("Adding NEW product type WITHOUT modifying existing code...")

# Create toys product type
toys_type, _ = ProductType.objects.get_or_create(
    name='toys',
    defaults={'display_name': 'Toys'}
)

# Register the new handler (EXTENSION without MODIFICATION!)
product_registry.register_handler(ToysHandler())

print(f"✅ New type added! Supported types: {product_registry.get_supported_types()}")

# Create a toy product using the SAME existing code
toys_form_data = {
    'age_range': '3-6 years',
    'safety_rating': 'CE certified',
    'material': 'Non-toxic plastic',
    'battery_required': 'Yes',
    'educational_value': 'STEM learning'
}

toy = Product.objects.create(
    name="Building Blocks Set",
    description="Educational building toy",
    price=39.99,
    product_type=toys_type
)

# The SAME registry code works for the new type!
toy.type_specific_data = product_registry.process_product_data('toys', toys_form_data)
toy.save()

print("🧸 Toy product created using EXISTING registry code!")

# Test that everything still works
print("\n📋 Updated Product List (including new type):")
for product in Product.objects.all():
    print(f"- {product.get_display_info()} (${product.price})")
    print(f"  Type: {product.product_type.display_name}")
    print(f"  Data: {product.type_specific_data}")
    print()

print("\n🎉 OPEN-CLOSED PRINCIPLE SUCCESS!")
print("✅ Added new product type WITHOUT modifying existing code")
print("✅ Existing functionality continues to work")
print("✅ New functionality works seamlessly")
print("\nThe system is:")
print("📖 OPEN for extension (new product types)")
print("🔒 CLOSED for modification (existing code unchanged)")