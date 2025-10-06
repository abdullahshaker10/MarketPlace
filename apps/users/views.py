"""
User Views using Abstract Factory Pattern

This module demonstrates how to use the Abstract Factory pattern
for user account creation in Django views. It provides clean,
consistent interfaces for creating different types of user accounts.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
import json

from .models import UserType
from .factories import create_account, AccountFactoryRegistry


class UserRegistrationView(View):
    """
    Generic user registration view that uses the Abstract Factory pattern

    This view demonstrates how the factory pattern simplifies user creation
    by encapsulating all the complex logic within the factories.
    """

    def get(self, request):
        """Display registration form"""
        context = {
            "user_types": UserType.choices,
            "supported_types": AccountFactoryRegistry.get_supported_user_types(),
        }
        return render(request, "users/register.html", context)

    def post(self, request):
        """Handle user registration using factory pattern"""
        try:
            # Extract user type from form data
            user_type_str = request.POST.get("user_type", UserType.BUYER)
            user_type = UserType(user_type_str)

            # Prepare user data from form
            user_data = {
                "username": request.POST.get("username"),
                "email": request.POST.get("email"),
                "password": request.POST.get("password"),
                "first_name": request.POST.get("first_name", ""),
                "last_name": request.POST.get("last_name", ""),
            }

            # Add type-specific data based on user type
            if user_type == UserType.BUYER:
                user_data.update(
                    {
                        "preferred_shipping_method": request.POST.get(
                            "preferred_shipping_method", "standard"
                        ),
                        "newsletter_subscription": request.POST.get(
                            "newsletter_subscription"
                        )
                        == "on",
                        "deal_notifications": request.POST.get("deal_notifications")
                        == "on",
                        "product_recommendations": request.POST.get(
                            "product_recommendations"
                        )
                        == "on",
                    }
                )
            elif user_type == UserType.SELLER:
                user_data.update(
                    {
                        "business_name": request.POST.get("business_name", ""),
                        "business_type": request.POST.get(
                            "business_type", "individual"
                        ),
                        "tax_id": request.POST.get("tax_id", ""),
                        "business_address": request.POST.get("business_address", ""),
                        "store_name": request.POST.get("store_name", ""),
                        "store_description": request.POST.get("store_description", ""),
                    }
                )
            elif user_type == UserType.ADMIN:
                # Admin creation might be restricted to superusers
                if not request.user.is_superuser:
                    messages.error(
                        request, "You do not have permission to create admin accounts."
                    )
                    return redirect("users:register")

                user_data.update(
                    {
                        "admin_level": request.POST.get("admin_level", "junior"),
                        "department": request.POST.get("department", ""),
                        "role_description": request.POST.get("role_description", ""),
                        "can_manage_users": request.POST.get("can_manage_users")
                        == "on",
                        "can_manage_products": request.POST.get("can_manage_products")
                        == "on",
                        "can_manage_orders": request.POST.get("can_manage_orders")
                        == "on",
                        "can_manage_payments": request.POST.get("can_manage_payments")
                        == "on",
                        "can_view_analytics": request.POST.get("can_view_analytics")
                        == "on",
                        "can_manage_system": request.POST.get("can_manage_system")
                        == "on",
                    }
                )

            # Use factory pattern to create account
            result = create_account(user_type, user_data)

            if result.is_successful:
                # Log the user in
                user = authenticate(
                    request, username=user_data["email"], password=user_data["password"]
                )
                if user:
                    login(request, user)
                    messages.success(
                        request,
                        f"{user_type.label} account created successfully! Welcome, {user.username}!",
                    )

                    # Redirect based on user type
                    if user_type == UserType.BUYER:
                        return redirect("users:buyer_dashboard")
                    elif user_type == UserType.SELLER:
                        return redirect("users:seller_dashboard")
                    elif user_type == UserType.ADMIN:
                        return redirect("admin:index")
                else:
                    messages.error(
                        request,
                        "Account created but login failed. Please try logging in manually.",
                    )
                    return redirect("users:login")
            else:
                # Handle creation errors
                for error in result.errors:
                    messages.error(request, error)
                return render(
                    request,
                    "users/register.html",
                    {"user_types": UserType.choices, "form_data": request.POST},
                )

        except ValueError as e:
            messages.error(request, f"Invalid user type: {e}")
            return redirect("users:register")
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            return redirect("users:register")
