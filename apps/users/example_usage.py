"""
Example Usage of the Abstract Factory Pattern for User Account Creation

This module demonstrates how to use the Abstract Factory pattern implementation
for creating different types of user accounts in the marketplace application.

The Abstract Factory pattern provides several benefits:
1. Consistent account creation across different user types
2. Encapsulation of complex creation logic
3. Easy extensibility for new user types
4. Clean separation of concerns
5. Type safety and validation
"""

import os
import sys
import django

# Setup Django (for running this as a standalone script)
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "marketplace.settings")
    django.setup()

from .models import UserType
from .factories import create_account, AccountFactoryRegistry


def example_buyer_creation():
    """
    Example: Creating a Buyer Account

    This demonstrates how to create a buyer account with all the
    buyer-specific configurations and preferences.
    """
    print("=== Creating Buyer Account ===")

    buyer_data = {
        # Required fields
        "username": "john_buyer",
        "email": "john@example.com",
        "password": "secure_password_123",
        # Optional personal information
        "first_name": "John",
        "last_name": "Doe",
        # Buyer-specific preferences
        "preferred_shipping_method": "express",
        "newsletter_subscription": True,
        "deal_notifications": True,
        "product_recommendations": True,
        "marketing_emails": True,
    }

    # Create the account using the factory pattern
    result = create_account(UserType.BUYER, buyer_data)

    if result.is_successful:
        user = result.user
        buyer_profile = result.profile_data["buyer_profile"]

        print(f"✅ Buyer account created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User Type: {user.get_user_type_display()}")
        print(f"   Preferred Shipping: {buyer_profile.preferred_shipping_method}")
        print(f"   Newsletter: {buyer_profile.newsletter_subscription}")
        print(f"   Account Status: {user.business_info.account_status}")

        # The factory automatically created all related profiles
        print(f"   Has Profile: {hasattr(user, 'profile')}")
        print(f"   Has Preferences: {hasattr(user, 'preferences')}")
        print(f"   Has Analytics: {hasattr(user, 'analytics')}")
        print(f"   Has Business Info: {hasattr(user, 'business_info')}")
        print(f"   Has Buyer Profile: {hasattr(user, 'buyer_profile')}")

    else:
        print(f"❌ Failed to create buyer account:")
        for error in result.errors:
            print(f"   - {error}")

    print()


def example_seller_creation():
    """
    Example: Creating a Seller Account

    This demonstrates how to create a seller account with business
    information and store configuration.
    """
    print("=== Creating Seller Account ===")

    seller_data = {
        # Required fields
        "username": "jane_seller",
        "email": "jane@businessstore.com",
        "password": "secure_business_password_123",
        # Optional personal information
        "first_name": "Jane",
        "last_name": "Smith",
        # Business information
        "business_name": "Jane's Awesome Store LLC",
        "business_type": "business",
        "tax_id": "12-3456789",
        "business_address": "123 Business Street, Commerce City, BC 12345",
        # Store configuration
        "store_name": "Jane's Awesome Store",
        "store_description": "Premium quality products with excellent customer service",
        "commission_rate": 4.5,  # Custom commission rate
        # Seller preferences (different from buyers)
        "marketing_emails": False,  # Sellers typically get fewer marketing emails
        "newsletter_subscription": False,
        "push_notifications": True,
    }

    # Create the account using the factory pattern
    result = create_account(UserType.SELLER, seller_data)

    if result.is_successful:
        user = result.user
        seller_profile = result.profile_data["seller_profile"]

        print(f"✅ Seller account created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User Type: {user.get_user_type_display()}")
        print(f"   Business Name: {seller_profile.business_name}")
        print(f"   Store Name: {seller_profile.store_name}")
        print(f"   Commission Rate: {seller_profile.commission_rate}%")
        print(f"   Account Status: {user.business_info.account_status}")
        print(
            f"   Verification Required: {result.profile_data.get('verification_required', False)}"
        )

        # Seller-specific configurations
        print(f"   Marketing Emails: {user.preferences.marketing_emails}")
        print(f"   Can Sell: {seller_profile.can_sell}")

    else:
        print(f"❌ Failed to create seller account:")
        for error in result.errors:
            print(f"   - {error}")

    print()


def example_admin_creation():
    """
    Example: Creating an Admin Account

    This demonstrates how to create an admin account with specific
    permissions and security settings.
    """
    print("=== Creating Admin Account ===")

    admin_data = {
        # Required fields
        "username": "admin_mike",
        "email": "mike@marketplace-admin.com",
        "password": "super_secure_admin_password_123",
        # Optional personal information
        "first_name": "Mike",
        "last_name": "Johnson",
        # Admin-specific configuration
        "admin_level": "senior",
        "department": "Customer Support",
        "role_description": "Senior Customer Support Administrator",
        # Permissions
        "can_manage_users": True,
        "can_manage_products": False,  # Limited permissions for this admin
        "can_manage_orders": True,
        "can_manage_payments": False,
        "can_view_analytics": True,
        "can_manage_system": False,
        # Security settings
        "require_2fa": True,
        "session_timeout_minutes": 30,
        # Admin preferences
        "theme": "dark",
        "push_notifications": True,
        # Optional: Create as superuser
        "is_superuser": False,  # Regular admin, not superuser
    }

    # Create the account using the factory pattern
    result = create_account(UserType.ADMIN, admin_data)

    if result.is_successful:
        user = result.user
        admin_profile = result.profile_data["admin_profile"]

        print(f"✅ Admin account created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   User Type: {user.get_user_type_display()}")
        print(f"   Admin Level: {admin_profile.get_admin_level_display()}")
        print(f"   Department: {admin_profile.department}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")

        # Admin permissions
        print(f"   Can Manage Users: {admin_profile.can_manage_users}")
        print(f"   Can Manage Orders: {admin_profile.can_manage_orders}")
        print(f"   Can View Analytics: {admin_profile.can_view_analytics}")

        # Security settings
        print(f"   Requires 2FA: {admin_profile.require_2fa}")
        print(f"   Session Timeout: {admin_profile.session_timeout_minutes} minutes")

        # Admin gets premium features automatically
        print(f"   Premium Account: {user.business_info.is_premium}")

    else:
        print(f"❌ Failed to create admin account:")
        for error in result.errors:
            print(f"   - {error}")

    print()


def example_factory_registry_usage():
    """
    Example: Using the Factory Registry

    This demonstrates how to use the factory registry to dynamically
    get factories and create accounts based on user type.
    """
    print("=== Factory Registry Usage ===")

    # Get all supported user types
    supported_types = AccountFactoryRegistry.get_supported_user_types()
    print(f"Supported user types: {[ut.label for ut in supported_types]}")

    # Dynamically get factories
    for user_type in supported_types:
        factory = AccountFactoryRegistry.get_factory(user_type)
        print(f"Factory for {user_type.label}: {factory.__class__.__name__}")

    # Example of dynamic account creation based on user input
    user_type_choice = UserType.BUYER  # This could come from user input

    base_data = {
        "username": f"dynamic_{user_type_choice.value}",
        "email": f"dynamic_{user_type_choice.value}@example.com",
        "password": "dynamic_password_123",
        "first_name": "Dynamic",
        "last_name": "User",
    }

    result = create_account(user_type_choice, base_data)

    if result.is_successful:
        print(
            f"✅ Dynamically created {user_type_choice.label} account: {result.user.username}"
        )
    else:
        print(f"❌ Failed to create dynamic account: {result.errors}")

    print()


def example_error_handling():
    """
    Example: Error Handling

    This demonstrates how the factory pattern handles errors gracefully
    and provides meaningful error messages.
    """
    print("=== Error Handling Examples ===")

    # Example 1: Missing required fields
    print("1. Missing required fields:")
    incomplete_data = {
        "username": "incomplete_user",
        # Missing email and password
    }

    result = create_account(UserType.BUYER, incomplete_data)
    if not result.is_successful:
        print(f"   ❌ Expected error: {result.errors[0]}")

    # Example 2: Invalid user type (this would raise ValueError)
    print("2. Invalid user type:")
    try:
        invalid_factory = AccountFactoryRegistry.get_factory("invalid_type")
    except ValueError as e:
        print(f"   ❌ Expected error: {e}")

    # Example 3: Duplicate email
    print("3. Duplicate email constraint:")

    # Create first user
    first_user_data = {
        "username": "first_user",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    result1 = create_account(UserType.BUYER, first_user_data)

    if result1.is_successful:
        print(f"   ✅ First user created: {result1.user.username}")

        # Try to create second user with same email
        second_user_data = {
            "username": "second_user",
            "email": "duplicate@example.com",  # Same email
            "password": "password123",
        }
        result2 = create_account(UserType.SELLER, second_user_data)

        if not result2.is_successful:
            print(f"   ❌ Expected duplicate email error occurred")

    print()


def example_extensibility():
    """
    Example: Extensibility

    This demonstrates how easy it is to extend the factory pattern
    with new user types (conceptual example).
    """
    print("=== Extensibility Example ===")

    print("Current supported user types:")
    for user_type in AccountFactoryRegistry.get_supported_user_types():
        print(f"  - {user_type.label}")

    print("\nTo add a new user type (e.g., 'Moderator'), you would:")
    print("1. Add MODERATOR = 'moderator', 'Moderator' to UserType choices")
    print("2. Create a ModeratorProfile model")
    print("3. Create a ModeratorAccountFactory class")
    print(
        "4. Register it: AccountFactoryRegistry.register_factory(UserType.MODERATOR, ModeratorAccountFactory)"
    )
    print("5. All existing code continues to work without changes!")

    print()


def main():
    """
    Main function that runs all examples
    """
    print("🏪 Marketplace User Account Creation Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_buyer_creation()
    example_seller_creation()
    example_admin_creation()
    example_factory_registry_usage()
    example_error_handling()
    example_extensibility()

    print("=" * 60)
    print("✅ All examples completed!")
    print()
    print("Key Benefits of the Abstract Factory Pattern:")
    print("• Consistent account creation across all user types")
    print("• Complex creation logic is encapsulated in factories")
    print("• Easy to add new user types without changing existing code")
    print("• Type-safe account creation with proper validation")
    print("• Clean separation between account types and their creation logic")
    print("• Automatic creation and configuration of all related models")


if __name__ == "__main__":
    main()
