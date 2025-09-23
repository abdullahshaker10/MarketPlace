from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from .models import Product, ProductType


def product_view(request, product_id=None):
    """
    Unified view that handles:
    - GET: List all products (if no product_id)
    - GET: Show product details (if product_id provided)
    - POST: Create new product (if no product_id)
    - POST: Update existing product (if product_id provided)
    """
    
    # Handle different HTTP methods and scenarios
    if request.method == 'GET':
        if product_id:
            # Show product details
            return _handle_product_detail(request, product_id)
        else:
            # List all products
            return _handle_product_list(request)
    
    elif request.method == 'POST':
        if product_id:
            # Update existing product
            return _handle_product_update(request, product_id)
        else:
            # Create new product
            return _handle_product_create(request)


def _handle_product_list(request):
    """Handle listing products with optional filtering"""
    product_type_filter = request.GET.get('type')
    
    # Get all products with their types (JSON data is loaded automatically)
    products = Product.objects.select_related('product_type').filter(is_active=True)
    
    # Apply filter if specified
    if product_type_filter:
        products = products.filter(product_type__name=product_type_filter)
    
    # Build product data
    products_data = []
    for product in products:
        products_data.append({
            'product': product,
            'type_data': product.type_specific_data,
            'type_name': product.product_type.name,
            'display_info': product.get_display_info()
        })
    
    context = {
        'products_data': products_data,
        'product_types': ProductType.objects.filter(is_active=True),
        'current_filter': product_type_filter,
        'view_mode': 'list'
    }
    
    return render(request, 'products/product_view.html', context)


def _handle_product_detail(request, product_id):
    """Handle showing individual product details"""
    product = Product.get_by_id_with_data(product_id)
    if not product:
        messages.error(request, 'Product not found')
        return redirect('product_view')
    
    context = {
        'product': product,
        'type_data': product.type_specific_data,
        'type_name': product.product_type.name,
        'display_info': product.get_display_info(),
        'product_types': ProductType.objects.filter(is_active=True),
        'view_mode': 'detail'
    }
    
    return render(request, 'products/product_view.html', context)


def _handle_product_create(request):
    """Handle creating a new product"""
    try:
        with transaction.atomic():
            # Get basic product data
            product_type_id = request.POST.get('product_type')
            product_type = get_object_or_404(ProductType, id=product_type_id)
            
            # Create the main product
            product = Product.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                price=request.POST.get('price'),
                product_type=product_type
            )
            
            # Set type-specific data based on product type
            _set_type_specific_data(product, request.POST)
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_view', product_id=product.id)
            
    except Exception as e:
        messages.error(request, f'Error creating product: {str(e)}')
        return redirect('product_view')


def _handle_product_update(request, product_id):
    """Handle updating an existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        with transaction.atomic():
            # Update basic product fields
            product.name = request.POST.get('name')
            product.description = request.POST.get('description', '')
            product.price = request.POST.get('price')
            product.save()
            
            # Update type-specific data
            _set_type_specific_data(product, request.POST)
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_view', product_id=product.id)
            
    except Exception as e:
        messages.error(request, f'Error updating product: {str(e)}')
        return redirect('product_view', product_id=product_id)


def _set_type_specific_data(product, post_data):
    """
    Set type-specific data using registry pattern
    
    This function now follows the Open-Closed Principle:
    - Open for extension: New product types can be added by registering handlers
    - Closed for modification: This function doesn't need changes for new types
    """
    from .type_handlers import product_registry
    
    type_name = product.product_type.name
    
    # Use registry to process data - no if/elif chains needed!
    type_specific_data = product_registry.process_product_data(type_name, post_data)
    
    product.type_specific_data = type_specific_data
    product.save()