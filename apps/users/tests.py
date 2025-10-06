"""
Comprehensive tests for the Abstract Factory Pattern implementation

This test suite validates the Abstract Factory pattern implementation
for user account creation, ensuring that all user types are created
correctly with their associated profiles and configurations.
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    UserType,
    BuyerProfile,
    SellerProfile,
    AdminProfile,
    UserProfile,
    UserPreferences,
    UserAnalytics,
    UserBusinessInfo,
)
from .factories import (
    AccountFactoryAbstract,
    BuyerAccountFactory,
    SellerAccountFactory,
    AdminAccountFactory,
    AccountFactoryRegistry,
    create_account,
    AccountCreationResult,
)

User = get_user_model()


class AccountCreationResultTest(TestCase):
    """Test the AccountCreationResult class"""

    def test_successful_result(self):
        """Test successful result creation"""
        user = User(username="test", email="test@example.com")
        profile_data = {"test": "data"}
        result = AccountCreationResult(user, profile_data)

        self.assertTrue(result.is_successful)
        self.assertEqual(result.user, user)
        self.assertEqual(result.profile_data, profile_data)
        self.assertEqual(result.errors, [])

    def test_result_with_errors(self):
        """Test result with errors"""
        result = AccountCreationResult(None, {})
        result.add_error("Test error")

        self.assertFalse(result.is_successful)
        self.assertIn("Test error", result.errors)
        self.assertFalse(result.success)


class BuyerAccountFactoryTest(TransactionTestCase):
    """Test the BuyerAccountFactory"""

    def setUp(self):
        """Set up test data"""
        self.factory = BuyerAccountFactory()
        self.user_data = {
            "username": "test_buyer",
            "email": "buyer@example.com",
            "password": "test_password_123",
            "first_name": "Test",
            "last_name": "Buyer",
            "preferred_shipping_method": "express",
            "newsletter_subscription": True,
            "deal_notifications": True,
            "product_recommendations": False,
        }

    def test_get_user_type(self):
        """Test that factory returns correct user type"""
        self.assertEqual(self.factory.get_user_type(), UserType.BUYER)

    def test_create_buyer_account_success(self):
        """Test successful buyer account creation"""
        result = self.factory.create_account(self.user_data)

        self.assertTrue(result.is_successful)
        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.username, "test_buyer")
        self.assertEqual(result.user.email, "buyer@example.com")
        self.assertEqual(result.user.user_type, UserType.BUYER)

        # Check that all related models were created
        self.assertTrue(hasattr(result.user, "profile"))
        self.assertTrue(hasattr(result.user, "preferences"))
        self.assertTrue(hasattr(result.user, "analytics"))
        self.assertTrue(hasattr(result.user, "business_info"))
        self.assertTrue(hasattr(result.user, "buyer_profile"))

        # Check buyer-specific profile
        buyer_profile = result.user.buyer_profile
        self.assertEqual(buyer_profile.preferred_shipping_method, "express")
        self.assertTrue(buyer_profile.newsletter_subscription)
        self.assertTrue(buyer_profile.deal_notifications)
        self.assertFalse(buyer_profile.product_recommendations)

        # Check profile data in result
        self.assertIn("buyer_profile", result.profile_data)
        self.assertIn("user_profile", result.profile_data)
        self.assertIn("user_preferences", result.profile_data)
        self.assertIn("user_analytics", result.profile_data)
        self.assertIn("user_business_info", result.profile_data)

    def test_create_buyer_account_missing_required_fields(self):
        """Test buyer account creation with missing required fields"""
        incomplete_data = {"username": "test_buyer"}
        result = self.factory.create_account(incomplete_data)

        self.assertFalse(result.is_successful)
        self.assertIsNone(result.user)
        self.assertTrue(len(result.errors) > 0)

    def test_buyer_preferences_configuration(self):
        """Test that buyer preferences are configured correctly"""
        result = self.factory.create_account(self.user_data)

        preferences = result.user.preferences
        self.assertTrue(preferences.marketing_emails)
        self.assertTrue(preferences.newsletter_subscription)
        self.assertTrue(preferences.push_notifications)

        business_info = result.user.business_info
        self.assertEqual(business_info.account_status, "active")


class SellerAccountFactoryTest(TransactionTestCase):
    """Test the SellerAccountFactory"""

    def setUp(self):
        """Set up test data"""
        self.factory = SellerAccountFactory()
        self.user_data = {
            "username": "test_seller",
            "email": "seller@example.com",
            "password": "test_password_123",
            "first_name": "Test",
            "last_name": "Seller",
            "business_name": "Test Business LLC",
            "business_type": "business",
            "tax_id": "12-3456789",
            "business_address": "123 Business St, City, State",
            "store_name": "Test Store",
            "store_description": "A test store for testing purposes",
            "commission_rate": 3.5,
        }

    def test_get_user_type(self):
        """Test that factory returns correct user type"""
        self.assertEqual(self.factory.get_user_type(), UserType.SELLER)

    def test_create_seller_account_success(self):
        """Test successful seller account creation"""
        result = self.factory.create_account(self.user_data)

        self.assertTrue(result.is_successful)
        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.username, "test_seller")
        self.assertEqual(result.user.email, "seller@example.com")
        self.assertEqual(result.user.user_type, UserType.SELLER)

        # Check that all related models were created
        self.assertTrue(hasattr(result.user, "profile"))
        self.assertTrue(hasattr(result.user, "preferences"))
        self.assertTrue(hasattr(result.user, "analytics"))
        self.assertTrue(hasattr(result.user, "business_info"))
        self.assertTrue(hasattr(result.user, "seller_profile"))

        # Check seller-specific profile
        seller_profile = result.user.seller_profile
        self.assertEqual(seller_profile.business_name, "Test Business LLC")
        self.assertEqual(seller_profile.business_type, "business")
        self.assertEqual(seller_profile.tax_id, "12-3456789")
        self.assertEqual(seller_profile.store_name, "Test Store")
        self.assertEqual(seller_profile.commission_rate, 3.5)

        # Check profile data in result
        self.assertIn("seller_profile", result.profile_data)
        self.assertIn("verification_required", result.profile_data)
        self.assertTrue(result.profile_data["verification_required"])

    def test_seller_preferences_configuration(self):
        """Test that seller preferences are configured correctly"""
        result = self.factory.create_account(self.user_data)

        preferences = result.user.preferences
        self.assertFalse(preferences.marketing_emails)  # Less marketing for sellers
        self.assertFalse(preferences.newsletter_subscription)
        self.assertTrue(preferences.push_notifications)

        business_info = result.user.business_info
        self.assertEqual(business_info.account_status, "pending")  # Needs verification


class AdminAccountFactoryTest(TransactionTestCase):
    """Test the AdminAccountFactory"""

    def setUp(self):
        """Set up test data"""
        self.factory = AdminAccountFactory()
        self.user_data = {
            "username": "test_admin",
            "email": "admin@example.com",
            "password": "test_password_123",
            "first_name": "Test",
            "last_name": "Admin",
            "admin_level": "senior",
            "department": "IT",
            "role_description": "Senior IT Administrator",
            "can_manage_users": True,
            "can_manage_products": True,
            "can_view_analytics": True,
            "require_2fa": True,
            "session_timeout_minutes": 15,
        }

    def test_get_user_type(self):
        """Test that factory returns correct user type"""
        self.assertEqual(self.factory.get_user_type(), UserType.ADMIN)

    def test_create_admin_account_success(self):
        """Test successful admin account creation"""
        result = self.factory.create_account(self.user_data)

        self.assertTrue(result.is_successful)
        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.username, "test_admin")
        self.assertEqual(result.user.email, "admin@example.com")
        self.assertEqual(result.user.user_type, UserType.ADMIN)

        # Check Django admin flags
        self.assertTrue(result.user.is_staff)
        self.assertFalse(result.user.is_superuser)  # Default is False

        # Check that all related models were created
        self.assertTrue(hasattr(result.user, "profile"))
        self.assertTrue(hasattr(result.user, "preferences"))
        self.assertTrue(hasattr(result.user, "analytics"))
        self.assertTrue(hasattr(result.user, "business_info"))
        self.assertTrue(hasattr(result.user, "admin_profile"))

        # Check admin-specific profile
        admin_profile = result.user.admin_profile
        self.assertEqual(admin_profile.admin_level, "senior")
        self.assertEqual(admin_profile.department, "IT")
        self.assertTrue(admin_profile.can_manage_users)
        self.assertTrue(admin_profile.can_manage_products)
        self.assertTrue(admin_profile.can_view_analytics)
        self.assertTrue(admin_profile.require_2fa)
        self.assertEqual(admin_profile.session_timeout_minutes, 15)

        # Check profile data in result
        self.assertIn("admin_profile", result.profile_data)
        self.assertIn("admin_permissions_set", result.profile_data)
        self.assertTrue(result.profile_data["admin_permissions_set"])

    def test_create_superuser_admin(self):
        """Test creating an admin with superuser privileges"""
        self.user_data["is_superuser"] = True
        result = self.factory.create_account(self.user_data)

        self.assertTrue(result.is_successful)
        self.assertTrue(result.user.is_superuser)
        self.assertTrue(result.user.is_staff)

    def test_admin_preferences_configuration(self):
        """Test that admin preferences are configured correctly"""
        result = self.factory.create_account(self.user_data)

        preferences = result.user.preferences
        self.assertFalse(preferences.marketing_emails)  # Admins don't need marketing
        self.assertFalse(preferences.newsletter_subscription)
        self.assertTrue(preferences.push_notifications)
        self.assertEqual(preferences.theme, "dark")  # Admins might prefer dark theme

        business_info = result.user.business_info
        self.assertEqual(business_info.account_status, "active")
        self.assertTrue(business_info.is_premium)  # Admins get premium features


class AccountFactoryRegistryTest(TestCase):
    """Test the AccountFactoryRegistry"""

    def test_get_factory_buyer(self):
        """Test getting buyer factory"""
        factory = AccountFactoryRegistry.get_factory(UserType.BUYER)
        self.assertIsInstance(factory, BuyerAccountFactory)

    def test_get_factory_seller(self):
        """Test getting seller factory"""
        factory = AccountFactoryRegistry.get_factory(UserType.SELLER)
        self.assertIsInstance(factory, SellerAccountFactory)

    def test_get_factory_admin(self):
        """Test getting admin factory"""
        factory = AccountFactoryRegistry.get_factory(UserType.ADMIN)
        self.assertIsInstance(factory, AdminAccountFactory)

    def test_get_factory_invalid_type(self):
        """Test getting factory for invalid user type"""
        with self.assertRaises(ValueError):
            AccountFactoryRegistry.get_factory("invalid_type")

    def test_get_supported_user_types(self):
        """Test getting supported user types"""
        supported_types = AccountFactoryRegistry.get_supported_user_types()
        self.assertIn(UserType.BUYER, supported_types)
        self.assertIn(UserType.SELLER, supported_types)
        self.assertIn(UserType.ADMIN, supported_types)
        self.assertEqual(len(supported_types), 3)

    def test_register_new_factory(self):
        """Test registering a new factory type"""

        class TestFactory(AccountFactoryAbstract):
            def get_user_type(self):
                return "test"

            def create_account(self, user_data):
                pass

            def _create_type_specific_profile(self, user, user_data):
                pass

            def _configure_type_specific_settings(self, user, user_data):
                pass

        # Register new factory
        AccountFactoryRegistry.register_factory("test", TestFactory)

        # Test that it can be retrieved
        factory = AccountFactoryRegistry.get_factory("test")
        self.assertIsInstance(factory, TestFactory)

        # Clean up
        del AccountFactoryRegistry._factories["test"]


class ConvenienceFunctionTest(TransactionTestCase):
    """Test the convenience create_account function"""

    def test_create_buyer_account(self):
        """Test creating buyer account using convenience function"""
        user_data = {
            "username": "convenience_buyer",
            "email": "convenience_buyer@example.com",
            "password": "test_password_123",
            "first_name": "Convenience",
            "last_name": "Buyer",
        }

        result = create_account(UserType.BUYER, user_data)

        self.assertTrue(result.is_successful)
        self.assertEqual(result.user.user_type, UserType.BUYER)
        self.assertTrue(hasattr(result.user, "buyer_profile"))

    def test_create_seller_account(self):
        """Test creating seller account using convenience function"""
        user_data = {
            "username": "convenience_seller",
            "email": "convenience_seller@example.com",
            "password": "test_password_123",
            "first_name": "Convenience",
            "last_name": "Seller",
        }

        result = create_account(UserType.SELLER, user_data)

        self.assertTrue(result.is_successful)
        self.assertEqual(result.user.user_type, UserType.SELLER)
        self.assertTrue(hasattr(result.user, "seller_profile"))

    def test_create_admin_account(self):
        """Test creating admin account using convenience function"""
        user_data = {
            "username": "convenience_admin",
            "email": "convenience_admin@example.com",
            "password": "test_password_123",
            "first_name": "Convenience",
            "last_name": "Admin",
        }

        result = create_account(UserType.ADMIN, user_data)

        self.assertTrue(result.is_successful)
        self.assertEqual(result.user.user_type, UserType.ADMIN)
        self.assertTrue(hasattr(result.user, "admin_profile"))
        self.assertTrue(result.user.is_staff)


class DatabaseIntegrityTest(TransactionTestCase):
    """Test database integrity and constraints"""

    def test_user_type_choices(self):
        """Test that user_type field accepts valid choices"""
        for user_type in [UserType.BUYER, UserType.SELLER, UserType.ADMIN]:
            user_data = {
                "username": f"test_{user_type.value}",
                "email": f"{user_type.value}@example.com",
                "password": "test_password_123",
            }

            result = create_account(user_type, user_data)
            self.assertTrue(result.is_successful)
            self.assertEqual(result.user.user_type, user_type)

    def test_unique_email_constraint(self):
        """Test that email uniqueness is enforced"""
        user_data = {
            "username": "test_user1",
            "email": "duplicate@example.com",
            "password": "test_password_123",
        }

        # Create first user
        result1 = create_account(UserType.BUYER, user_data)
        self.assertTrue(result1.is_successful)

        # Try to create second user with same email
        user_data["username"] = "test_user2"
        result2 = create_account(UserType.SELLER, user_data)
        self.assertFalse(result2.is_successful)

    def test_profile_relationships(self):
        """Test that profile relationships are correctly established"""
        user_data = {
            "username": "relationship_test",
            "email": "relationship@example.com",
            "password": "test_password_123",
        }

        result = create_account(UserType.BUYER, user_data)
        user = result.user

        # Test OneToOne relationships
        self.assertEqual(user.profile.user, user)
        self.assertEqual(user.preferences.user, user)
        self.assertEqual(user.analytics.user, user)
        self.assertEqual(user.business_info.user, user)
        self.assertEqual(user.buyer_profile.user, user)

        # Test reverse relationships
        self.assertEqual(user.profile.user.buyer_profile, user.buyer_profile)


class FactoryPatternBenefitsTest(TransactionTestCase):
    """Test that demonstrates the benefits of the Factory Pattern"""

    def test_consistent_account_creation(self):
        """Test that all account types are created consistently"""
        base_data = {
            "password": "test_password_123",
            "first_name": "Test",
            "last_name": "User",
        }

        test_cases = [
            (UserType.BUYER, "buyer_test", "buyer@test.com"),
            (UserType.SELLER, "seller_test", "seller@test.com"),
            (UserType.ADMIN, "admin_test", "admin@test.com"),
        ]

        for user_type, username, email in test_cases:
            user_data = {
                **base_data,
                "username": username,
                "email": email,
            }

            result = create_account(user_type, user_data)

            # All account types should be created successfully
            self.assertTrue(
                result.is_successful, f"Failed to create {user_type} account"
            )

            # All should have base profiles
            self.assertTrue(hasattr(result.user, "profile"))
            self.assertTrue(hasattr(result.user, "preferences"))
            self.assertTrue(hasattr(result.user, "analytics"))
            self.assertTrue(hasattr(result.user, "business_info"))

            # Each should have their specific profile
            if user_type == UserType.BUYER:
                self.assertTrue(hasattr(result.user, "buyer_profile"))
            elif user_type == UserType.SELLER:
                self.assertTrue(hasattr(result.user, "seller_profile"))
            elif user_type == UserType.ADMIN:
                self.assertTrue(hasattr(result.user, "admin_profile"))

    def test_extensibility(self):
        """Test that the pattern is easily extensible"""
        # This test demonstrates how easy it would be to add a new user type

        # Get current supported types
        original_types = AccountFactoryRegistry.get_supported_user_types()

        # The registry pattern makes it easy to add new types
        self.assertEqual(len(original_types), 3)

        # If we wanted to add a new type, we would:
        # 1. Create a new model (e.g., ModeratorProfile)
        # 2. Create a new factory (e.g., ModeratorAccountFactory)
        # 3. Register it with AccountFactoryRegistry.register_factory()

        # The existing code wouldn't need to change at all!

    def test_encapsulation_of_complexity(self):
        """Test that complex creation logic is properly encapsulated"""
        # The factory pattern hides the complexity of creating multiple
        # related objects and configuring them properly

        user_data = {
            "username": "complex_test",
            "email": "complex@example.com",
            "password": "test_password_123",
        }

        # Simple interface hides complex creation process
        result = create_account(UserType.SELLER, user_data)

        # But results in a fully configured account with:
        # - User object with correct type
        # - All base profiles (UserProfile, UserPreferences, etc.)
        # - Type-specific profile (SellerProfile)
        # - Proper configuration and defaults
        # - All relationships established

        self.assertTrue(result.is_successful)
        self.assertEqual(result.user.user_type, UserType.SELLER)
        self.assertEqual(result.user.business_info.account_status, "pending")
        self.assertFalse(result.user.preferences.marketing_emails)
        self.assertTrue(hasattr(result.user, "seller_profile"))

        # All this complexity is handled by the factory, not the client code!
