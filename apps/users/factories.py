"""
User Account Factory Implementation using Abstract Factory Pattern

This module implements the Abstract Factory design pattern for creating
different types of user accounts (Buyer, Seller, Admin) with their
associated profiles and configurations.

The Abstract Factory pattern is ideal here because:
1. We need to create families of related objects (User + Profile + Configurations)
2. We want to encapsulate the complex creation logic for each user type
3. We want to ensure consistency across all objects created for a user type
4. We want to make it easy to add new user types in the future
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import UserType, BuyerProfile, SellerProfile, AdminProfile

User = get_user_model()


class AccountCreationResult:
    """
    Result object that encapsulates the created account and its components

    This provides a clean interface for accessing the created user and
    all associated profile objects.
    """

    def __init__(self, user: User, profile_data: Dict[str, Any]):
        self.user = user
        self.profile_data = profile_data
        self.success = True
        self.errors = []

    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.success = False

    @property
    def is_successful(self) -> bool:
        """Check if account creation was successful"""
        return self.success and not self.errors


class AccountFactoryAbstract(ABC):
    """
    Abstract Factory for creating user accounts

    This abstract class defines the interface that all concrete account
    factories must implement. It ensures consistent account creation
    across different user types.

    The factory encapsulates:
    - User creation with appropriate user_type
    - Type-specific profile creation
    - Default preferences setup
    - Analytics initialization
    - Business info configuration
    - Any additional setup required for the user type
    """

    @abstractmethod
    def create_account(self, user_data: Dict[str, Any]) -> AccountCreationResult:
        """
        Create a complete user account with all associated profiles

        Args:
            user_data: Dictionary containing user information
                Required fields: username, email, password
                Optional fields: first_name, last_name, etc.

        Returns:
            AccountCreationResult: Object containing the created user and profile data
        """
        pass

    @abstractmethod
    def get_user_type(self) -> UserType:
        """Return the user type this factory creates"""
        pass

    def _create_base_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create the base User object with common fields

        This method handles the creation of the core User model with
        fields that are common to all user types.
        """
        # Extract required fields
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")

        if not all([username, email, password]):
            raise ValueError("Username, email, and password are required")

        # Create user with type-specific user_type
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=self.get_user_type(),
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
        )

        return user

    def _setup_base_profiles(self, user: User) -> Dict[str, Any]:
        """
        Set up the base profiles that all users need

        This creates the common profile objects that every user should have:
        - UserProfile (basic profile information)
        - UserPreferences (user settings)
        - UserAnalytics (tracking data)
        - UserBusinessInfo (business-related data)
        """
        profile_data = {}

        # These are automatically created by Django signals, but we ensure they exist
        profile_data["user_profile"] = user.profile
        profile_data["user_preferences"] = user.preferences
        profile_data["user_analytics"] = user.analytics
        profile_data["user_business_info"] = user.business_info

        return profile_data

    @abstractmethod
    def _create_type_specific_profile(
        self, user: User, user_data: Dict[str, Any]
    ) -> Any:
        """
        Create the type-specific profile for this user type

        Each concrete factory must implement this to create the appropriate
        profile type (BuyerProfile, SellerProfile, or AdminProfile).
        """
        pass

    @abstractmethod
    def _configure_type_specific_settings(
        self, user: User, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure type-specific settings and preferences

        Each user type may need different default settings, permissions,
        or configurations. This method handles those customizations.
        """
        pass


class BuyerAccountFactory(AccountFactoryAbstract):
    """
    Concrete Factory for creating Buyer accounts

    Handles the creation of buyer accounts with:
    - Buyer-specific profile with shopping preferences
    - Default buyer settings (notifications, recommendations)
    - Buyer-specific business info setup
    """

    def get_user_type(self) -> UserType:
        return UserType.BUYER

    @transaction.atomic
    def create_account(self, user_data: Dict[str, Any]) -> AccountCreationResult:
        """
        Create a complete buyer account

        This method orchestrates the creation of all components needed
        for a buyer account in a single database transaction.
        """
        try:
            # Create base user
            user = self._create_base_user(user_data)

            # Set up base profiles (automatically created by signals)
            profile_data = self._setup_base_profiles(user)

            # Create buyer-specific profile
            buyer_profile = self._create_type_specific_profile(user, user_data)
            profile_data["buyer_profile"] = buyer_profile

            # Configure buyer-specific settings
            settings_data = self._configure_type_specific_settings(user, user_data)
            profile_data.update(settings_data)

            return AccountCreationResult(user, profile_data)

        except Exception as e:
            result = AccountCreationResult(None, {})
            result.add_error(f"Failed to create buyer account: {str(e)}")
            return result

    def _create_type_specific_profile(
        self, user: User, user_data: Dict[str, Any]
    ) -> BuyerProfile:
        """Create and configure BuyerProfile"""
        buyer_profile = BuyerProfile.objects.create(
            user=user,
            preferred_shipping_method=user_data.get(
                "preferred_shipping_method", "standard"
            ),
            newsletter_subscription=user_data.get("newsletter_subscription", True),
            deal_notifications=user_data.get("deal_notifications", True),
            product_recommendations=user_data.get("product_recommendations", True),
        )
        return buyer_profile

    def _configure_type_specific_settings(
        self, user: User, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure buyer-specific settings"""
        # Configure preferences for buyers
        preferences = user.preferences
        preferences.marketing_emails = user_data.get("marketing_emails", True)
        preferences.newsletter_subscription = user_data.get(
            "newsletter_subscription", True
        )
        preferences.push_notifications = user_data.get("push_notifications", True)
        preferences.save()

        # Configure business info for buyers
        business_info = user.business_info
        business_info.account_status = "active"
        business_info.save()

        return {
            "buyer_preferences_configured": True,
            "buyer_business_info_configured": True,
        }


class SellerAccountFactory(AccountFactoryAbstract):
    """
    Concrete Factory for creating Seller accounts

    Handles the creation of seller accounts with:
    - Seller-specific profile with business information
    - Store setup and configuration
    - Seller-specific permissions and settings
    """

    def get_user_type(self) -> UserType:
        return UserType.SELLER

    @transaction.atomic
    def create_account(self, user_data: Dict[str, Any]) -> AccountCreationResult:
        """
        Create a complete seller account

        This method orchestrates the creation of all components needed
        for a seller account in a single database transaction.
        """
        try:
            # Create base user
            user = self._create_base_user(user_data)

            # Set up base profiles
            profile_data = self._setup_base_profiles(user)

            # Create seller-specific profile
            seller_profile = self._create_type_specific_profile(user, user_data)
            profile_data["seller_profile"] = seller_profile

            # Configure seller-specific settings
            settings_data = self._configure_type_specific_settings(user, user_data)
            profile_data.update(settings_data)

            return AccountCreationResult(user, profile_data)

        except Exception as e:
            result = AccountCreationResult(None, {})
            result.add_error(f"Failed to create seller account: {str(e)}")
            return result

    def _create_type_specific_profile(
        self, user: User, user_data: Dict[str, Any]
    ) -> SellerProfile:
        """Create and configure SellerProfile"""
        seller_profile = SellerProfile.objects.create(
            user=user,
            business_name=user_data.get("business_name", ""),
            business_type=user_data.get("business_type", "individual"),
            tax_id=user_data.get("tax_id", ""),
            business_address=user_data.get("business_address", ""),
            store_name=user_data.get("store_name", ""),
            store_description=user_data.get("store_description", ""),
            commission_rate=user_data.get("commission_rate", 5.0),
        )
        return seller_profile

    def _configure_type_specific_settings(
        self, user: User, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure seller-specific settings"""
        # Configure preferences for sellers
        preferences = user.preferences
        preferences.marketing_emails = user_data.get(
            "marketing_emails", False
        )  # Less marketing for sellers
        preferences.newsletter_subscription = user_data.get(
            "newsletter_subscription", False
        )
        preferences.push_notifications = user_data.get("push_notifications", True)
        preferences.save()

        # Configure business info for sellers
        business_info = user.business_info
        business_info.account_status = "pending"  # Sellers need verification
        business_info.save()

        return {
            "seller_preferences_configured": True,
            "seller_business_info_configured": True,
            "verification_required": True,
        }


class AdminAccountFactory(AccountFactoryAbstract):
    """
    Concrete Factory for creating Admin accounts

    Handles the creation of admin accounts with:
    - Admin-specific profile with permissions
    - Security settings and access controls
    - Admin-specific configurations
    """

    def get_user_type(self) -> UserType:
        return UserType.ADMIN

    @transaction.atomic
    def create_account(self, user_data: Dict[str, Any]) -> AccountCreationResult:
        """
        Create a complete admin account

        This method orchestrates the creation of all components needed
        for an admin account in a single database transaction.
        """
        try:
            # Create base user
            user = self._create_base_user(user_data)

            # Set admin flags
            user.is_staff = True
            user.is_superuser = user_data.get("is_superuser", False)
            user.save()

            # Set up base profiles
            profile_data = self._setup_base_profiles(user)

            # Create admin-specific profile
            admin_profile = self._create_type_specific_profile(user, user_data)
            profile_data["admin_profile"] = admin_profile

            # Configure admin-specific settings
            settings_data = self._configure_type_specific_settings(user, user_data)
            profile_data.update(settings_data)

            return AccountCreationResult(user, profile_data)

        except Exception as e:
            result = AccountCreationResult(None, {})
            result.add_error(f"Failed to create admin account: {str(e)}")
            return result

    def _create_type_specific_profile(
        self, user: User, user_data: Dict[str, Any]
    ) -> AdminProfile:
        """Create and configure AdminProfile"""
        admin_profile = AdminProfile.objects.create(
            user=user,
            admin_level=user_data.get("admin_level", "junior"),
            can_manage_users=user_data.get("can_manage_users", False),
            can_manage_products=user_data.get("can_manage_products", False),
            can_manage_orders=user_data.get("can_manage_orders", False),
            can_manage_payments=user_data.get("can_manage_payments", False),
            can_view_analytics=user_data.get("can_view_analytics", False),
            can_manage_system=user_data.get("can_manage_system", False),
            department=user_data.get("department", ""),
            role_description=user_data.get("role_description", ""),
            require_2fa=user_data.get("require_2fa", True),
            session_timeout_minutes=user_data.get("session_timeout_minutes", 30),
        )
        return admin_profile

    def _configure_type_specific_settings(
        self, user: User, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure admin-specific settings"""
        # Configure preferences for admins
        preferences = user.preferences
        preferences.marketing_emails = False  # Admins don't need marketing emails
        preferences.newsletter_subscription = False
        preferences.push_notifications = user_data.get("push_notifications", True)
        preferences.theme = user_data.get(
            "theme", "dark"
        )  # Admins might prefer dark theme
        preferences.save()

        # Configure business info for admins
        business_info = user.business_info
        business_info.account_status = "active"
        business_info.is_premium = True  # Admins get premium features
        business_info.save()

        return {
            "admin_preferences_configured": True,
            "admin_business_info_configured": True,
            "admin_permissions_set": True,
        }


class AccountFactoryRegistry:
    """
    Registry for managing account factories

    This class provides a centralized way to register and retrieve
    account factories. It implements a simple registry pattern to
    make it easy to get the right factory for a given user type.
    """

    _factories = {
        UserType.BUYER: BuyerAccountFactory,
        UserType.SELLER: SellerAccountFactory,
        UserType.ADMIN: AdminAccountFactory,
    }

    @classmethod
    def get_factory(cls, user_type: UserType) -> AccountFactoryAbstract:
        """
        Get the appropriate factory for the given user type

        Args:
            user_type: The type of user account to create

        Returns:
            AccountFactoryAbstract: The factory instance for the user type

        Raises:
            ValueError: If the user type is not supported
        """
        if user_type not in cls._factories:
            raise ValueError(f"Unsupported user type: {user_type}")

        factory_class = cls._factories[user_type]
        return factory_class()

    @classmethod
    def register_factory(cls, user_type: UserType, factory_class: type):
        """
        Register a new factory for a user type

        This allows for extending the system with new user types
        without modifying existing code.
        """
        cls._factories[user_type] = factory_class

    @classmethod
    def get_supported_user_types(cls) -> list:
        """Get list of supported user types"""
        return list(cls._factories.keys())


# Convenience function for creating accounts
def create_account(
    user_type: UserType, user_data: Dict[str, Any]
) -> AccountCreationResult:
    """
    Convenience function to create an account of the specified type

    This is the main entry point for creating user accounts using the
    factory pattern. It handles getting the right factory and creating
    the account.

    Args:
        user_type: The type of user account to create
        user_data: Dictionary containing user information

    Returns:
        AccountCreationResult: Result of the account creation

    Example:
        result = create_account(UserType.BUYER, {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_shipping_method': 'express'
        })

        if result.is_successful:
            user = result.user
            buyer_profile = result.profile_data['buyer_profile']
        else:
            print(f"Account creation failed: {result.errors}")
    """
    factory = AccountFactoryRegistry.get_factory(user_type)
    return factory.create_account(user_data)
