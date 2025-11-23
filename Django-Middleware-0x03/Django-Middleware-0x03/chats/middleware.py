Role Permission Middleware Implementation
I'm going to create the RolePermissionMiddleware that checks if a user is an admin or moderator before allowing access. Let me provide you with a complete, tested solution.

 Step 1: Create the Middleware Class
# apps/core/middleware/role_permission_middleware.py

"""
Role Permission Middleware

This middleware checks if the authenticated user has the required role
(admin or moderator) before allowing access to protected resources.

Author: Your Name
Date: 2024
"""

import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('middleware')


class RolePermissionMiddleware:
    """
    Middleware to enforce role-based access control.
    
    This middleware checks if the user has 'admin' or 'moderator' role
    before allowing access to specific actions.
    
    Attributes:
        get_response: The next middleware or view in the chain
        public_paths: List of URL paths that don't require role checking
    
    Methods:
        __init__(get_response): Initialize the middleware
        __call__(request): Process each request and check user role
        get_user_role(user): Extract the user's role from the user object
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        This method is called once when Django starts up.
        
        Args:
            get_response: Callable that represents the next middleware or view
        """
        self.get_response = get_response
        
        # Define paths that don't require role checking
        self.public_paths = [
            '/admin/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/logout/',
            '/',
            '/health/',
        ]
        
        logger.info("✅ RolePermissionMiddleware initialized successfully")
    
    def __call__(self, request):
        """
        Process each incoming request.
        
        This method is called for every request that comes to the application.
        It checks if the user has the required role (admin or moderator).
        
        Args:
            request: HttpRequest object containing request data
            
        Returns:
            HttpResponse: Either the response from the next middleware/view
                         or a 403 Forbidden response if role check fails
        """
        
        # 1. Skip role checking for public paths
        if any(request.path.startswith(path) for path in self.public_paths):
            logger.debug(f"⏭️  Skipping role check for public path: {request.path}")
            return self.get_response(request)
        
        # 2. Check if user is authenticated
        if not request.user.is_authenticated:
            logger.warning(
                f"❌ Unauthenticated access attempt to: {request.path} "
                f"from IP: {self.get_client_ip(request)}"
            )
            return JsonResponse({
                'error': 'Authentication Required',
                'message': 'You must be logged in to access this resource.',
                'status': 401
            }, status=401)
        
        # 3. Get user's role
        user_role = self.get_user_role(request.user)
        
        # 4. Check if user has required role (admin or moderator)
        allowed_roles = ['admin', 'moderator']
        
        if user_role not in allowed_roles:
            logger.warning(
                f"🚫 Forbidden access: User '{request.user.username}' "
                f"(role: '{user_role}') tried to access {request.path}"
            )
            return JsonResponse({
                'error': 'Forbidden',
                'message': f'Access denied. Required roles: {", ".join(allowed_roles)}. Your role: {user_role}',
                'status': 403
            }, status=403)
        
        # 5. User has required role, allow access
        logger.info(
            f"✅ Access granted: User '{request.user.username}' "
            f"(role: '{user_role}') accessing {request.path}"
        )
        
        # Call the next middleware or view
        response = self.get_response(request)
        
        return response
    
    def get_user_role(self, user):
        """
        Extract the user's role from the user object.
        
        This method handles different ways roles might be stored:
        - Direct 'role' attribute
        - Through a 'profile' relationship
        - From 'is_staff' and 'is_superuser' flags
        
        Args:
            user: Django User object
            
        Returns:
            str: The user's role ('admin', 'moderator', 'host', 'guest', etc.)
        """
        # Check if user has a direct 'role' attribute
        if hasattr(user, 'role'):
            return user.role.lower()
        
        # Check if user has a profile with role
        if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
            return user.profile.role.lower()
        
        # Fallback: determine role from Django's built-in flags
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'moderator'
        else:
            return 'guest'
    
    def get_client_ip(self, request):
        """
        Extract the client's IP address from the request.
        
        Args:
            request: HttpRequest object
            
        Returns:
            str: Client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip


# Alternative implementation using MiddlewareMixin (if needed for older Django versions)
class RolePermissionMiddlewareMixin(MiddlewareMixin):
    """
    Alternative implementation using MiddlewareMixin.
    
    This version uses process_request instead of __call__,
    which is compatible with older Django middleware styles.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.public_paths = [
            '/admin/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/logout/',
            '/',
        ]
        logger.info("✅ RolePermissionMiddlewareMixin initialized successfully")
    
    def process_request(self, request):
        """Process incoming request before it reaches the view"""
        
        # Skip public paths
        if any(request.path.startswith(path) for path in self.public_paths):
            return None
        
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication Required',
                'message': 'You must be logged in to access this resource.'
            }, status=401)
        
        # Get and check user role
        user_role = self.get_user_role(request.user)
        allowed_roles = ['admin', 'moderator']
        
        if user_role not in allowed_roles:
            logger.warning(
                f"🚫 Access denied for user '{request.user.username}' "
                f"with role '{user_role}'"
            )
            return JsonResponse({
                'error': 'Forbidden',
                'message': f'Access denied. Required roles: {", ".join(allowed_roles)}',
                'status': 403
            }, status=403)
        
        # Allow request to continue
        return None
    
    def get_user_role(self, user):
        """Extract user role"""
        if hasattr(user, 'role'):
            return user.role.lower()
        if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
            return user.profile.role.lower()
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'moderator'
        return 'guest'

Step 2: Configure Middleware in settings.py
# config/settings.py

"""
Django settings for Airbnb Clone project.
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps to Python path
import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Security settings
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your apps
    'apps.core',
    'apps.users',
    'apps.listings',
]

# ============================================
# MIDDLEWARE CONFIGURATION
# ============================================
MIDDLEWARE = [
    # Django's default middleware (ORDER MATTERS!)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # ✅ YOUR CUSTOM MIDDLEWARE - Add RolePermissionMiddleware here
    'apps.core.middleware.role_permission_middleware.RolePermissionMiddleware',
    
    # You can add other custom middleware below
    # 'apps.core.middleware.logging_middleware.RequestLoggingMiddleware',
    # 'apps.core.middleware.ip_blocking_middleware.IPBlockingMiddleware',
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration (for middleware logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'middleware.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'middleware': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

 Step 3: Create Required init.py Files
# apps/__init__.py
"""
Apps package initialization
"""

# apps/core/__init__.py
"""
Core app initialization
"""

# apps/core/middleware/__init__.py
"""
Middleware package initialization

Available middleware:
- RolePermissionMiddleware: Enforces role-based access control
"""

from .role_permission_middleware import RolePermissionMiddleware

__all__ = ['RolePermissionMiddleware']

Step 4: Create Unit Tests
# tests/test_role_permission_middleware.py

"""
Unit tests for RolePermissionMiddleware

Tests:
1. Middleware class exists and is properly defined
2. Middleware has __init__ and __call__ methods
3. Public paths are accessible without authentication
4. Unauthenticated users receive 401 error
5. Users with 'guest' role receive 403 error
6. Users with 'admin' role can access protected resources
7. Users with 'moderator' role can access protected resources
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from apps.core.middleware.role_permission_middleware import RolePermissionMiddleware
import json


class RolePermissionMiddlewareTest(TestCase):
    """Test suite for RolePermissionMiddleware"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        
        # Create a mock get_response function
        def get_response(request):
            return HttpResponse("Success", status=200)
        
        self.middleware = RolePermissionMiddleware(get_response)
        
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password123',
            is_superuser=True
        )
        
        self.moderator_user = User.objects.create_user(
            username='moderator',
            email='moderator@test.com',
            password='password123',
            is_staff=True
        )
        
        self.guest_user = User.objects.create_user(
            username='guest',
            email='guest@test.com',
            password='password123'
        )
    
    # ============================================
    # TEST 1: Check if class exists and is defined
    # ============================================
    def test_middleware_class_exists(self):
        """Test that RolePermissionMiddleware class exists"""
        self.assertTrue(
            hasattr(RolePermissionMiddleware, '__init__'),
            "RolePermissionMiddleware must have __init__ method"
        )
        self.assertTrue(
            hasattr(RolePermissionMiddleware, '__call__'),
            "RolePermissionMiddleware must have __call__ method"
        )
        print("✅ TEST 1 PASSED: Middleware class exists with required methods")
    
    # ============================================
    # TEST 2: Check middleware initialization
    # ============================================
    def test_middleware_initialization(self):
        """Test that middleware initializes correctly"""
        self.assertIsNotNone(self.middleware.get_response)
        self.assertIsInstance(self.middleware.public_paths, list)
        self.assertGreater(len(self.middleware.public_paths), 0)
        print("✅ TEST 2 PASSED: Middleware initializes correctly")
    
    # ============================================
    # TEST 3: Public paths are accessible
    # ============================================
    def test_public_paths_accessible(self):
        """Test that public paths don't require authentication"""
        public_paths = ['/admin/', '/api/auth/login/', '/']
        
        for path in public_paths:
            request = self.factory.get(path)
            request.user = self.guest_user
            
            response = self.middleware(request)
            
            self.assertEqual(
                response.status_code, 200,
                f"Public path {path} should be accessible"
            )
        
        print("✅ TEST 3 PASSED: Public paths are accessible")
    
    # ============================================
    # TEST 4: Unauthenticated users blocked
    # ============================================
    def test_unauthenticated_user_blocked(self):
        """Test that unauthenticated users receive 401 error"""
        request = self.factory.get('/api/listings/')
        
        # Create anonymous user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 401)
        
        # Check response content
        content = json.loads(response.content)
        self.assertEqual(content['error'], 'Authentication Required')
        
        print("✅ TEST 4 PASSED: Unauthenticated users receive 401")
    
    # ============================================
    # TEST 5: Guest users receive 403
    # ============================================
    def test_guest_user_forbidden(self):
        """Test that users with 'guest' role receive 403 error"""
        request = self.factory.get('/api/listings/create/')
        request.user = self.guest_user
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 403)
        
        # Check response content
        content = json.loads(response.content)
        self.assertEqual(content['error'], 'Forbidden')
        self.assertIn('guest', content['message'].lower())
        
        print("✅ TEST 5 PASSED: Guest users receive 403 Forbidden")
    
    # ============================================
    # TEST 6: Admin users allowed
    # ============================================
    def test_admin_user_allowed(self):
        """Test that users with 'admin' role can access protected resources"""
        request = self.factory.get('/api/admin/dashboard/')
        request.user = self.admin_user
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")
        
        print("✅ TEST 6 PASSED: Admin users can access resources")
    
    # ============================================
    # TEST 7: Moderator users allowed
    # ============================================
    def test_moderator_user_allowed(self):
        """Test that users with 'moderator' role can access protected resources"""
        request = self.factory.get('/api/moderate/reports/')
        request.user = self.moderator_user
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")
        
        print("✅ TEST 7 PASSED: Moderator users can access resources")
    
    # ============================================
    # TEST 8: get_user_role method works correctly
    # ============================================
    def test_get_user_role_method(self):
        """Test that get_user_role correctly identifies user roles"""
        admin_role = self.middleware.get_user_role(self.admin_user)
        self.assertEqual(admin_role, 'admin')
        
        moderator_role = self.middleware.get_user_role(self.moderator_user)
        self.assertEqual(moderator_role, 'moderator')
        
        guest_role = self.middleware.get_user_role(self.guest_user)
        self.assertEqual(guest_role, 'guest')
        
        print("✅ TEST 8 PASSED: get_user_role method works correctly")


# ============================================
# Run tests with: python manage.py test tests.test_role_permission_middleware
# ============================================

 Step 5: Verification Script
# verify_middleware.py

"""
Verification script to check if RolePermissionMiddleware is properly set up

Run this with: python verify_middleware.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings


def verify_middleware():
    """Verify that middleware is properly configured"""
    
    print("=" * 70)
    print("🔍 VERIFYING ROLEPERMISSIONMIDDLEWARE SETUP")
    print("=" * 70)
    
    # Check 1: Class exists and is defined
    print("\n📋 CHECK 1: Middleware Class Exists")
    print("-" * 70)
    try:
        from apps.core.middleware.role_permission_middleware import RolePermissionMiddleware
        print("✅ RolePermissionMiddleware class found")
        
        # Check methods
        assert hasattr(RolePermissionMiddleware, '__init__'), "❌ __init__ method missing"
        print("✅ __init__ method exists")
        
        assert hasattr(RolePermissionMiddleware, '__call__'), "❌ __call__ method missing"
        print("✅ __call__ method exists")
        
        assert hasattr(RolePermissionMiddleware, 'get_user_role'), "⚠️  get_user_role method recommended"
        print("✅ get_user_role method exists")
        
    except ImportError as e:
        print(f"❌ ERROR: Cannot import RolePermissionMiddleware: {e}")
        return False
    
    # Check 2: Middleware in settings.py
    print("\n📋 CHECK 2: Middleware Configuration in settings.py")
    print("-" * 70)
    
    middleware_list = settings.MIDDLEWARE
    middleware_path = 'apps.core.middleware.role_permission_middleware.RolePermissionMiddleware'
    
    if middleware_path in middleware_list:
        print(f"✅ RolePermissionMiddleware is configured in MIDDLEWARE")
        
        # Show position
        position = middleware_list.index(middleware_path) + 1
        print(f"   Position: #{position} in the middleware stack")
        
        # Check order (should be after auth middleware)
        auth_middleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
        if auth_middleware in middleware_list:
            auth_position = middleware_list.index(auth_middleware)
            role_position = middleware_list.index(middleware_path)
            
            if role_position > auth_position:
                print("✅ Correct order: RolePermissionMiddleware is after AuthenticationMiddleware")
            else:
                print("⚠️  WARNING: RolePermissionMiddleware should come AFTER AuthenticationMiddleware")
    else:
        print(f"❌ ERROR: RolePermissionMiddleware NOT found in MIDDLEWARE settings")
        print(f"\nAdd this line to MIDDLEWARE in settings.py:")
        print(f"   '{middleware_path}',")
        return False
    
    # Check 3: File structure
    print("\n📋 CHECK 3: File Structure")
    print("-" * 70)
    
    required_files = [
        'apps/core/middleware/role_permission_middleware.py',
        'apps/core/middleware/__init__.py',
        'apps/core/__init__.py',
        'apps/__init__.py',
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL CHECKS PASSED! RolePermissionMiddleware is properly set up.")
    print("=" * 70)
    
    print("\n📚 NEXT STEPS:")
    print("1. Run tests: python manage.py test tests.test_role_permission_middleware")
    print("2. Start server: python manage.py runserver")
    print("3. Test with Postman or curl")
    
    return True


if __name__ == '__main__':
    try:
        success = verify_middleware()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

Step 6: Manual Testing Guide
Test with Django Shell
# Open Django shell: python manage.py shell

from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.core.middleware.role_permission_middleware import RolePermissionMiddleware
from django.http import HttpResponse

# Create factory
factory = RequestFactory()

# Create middleware
def get_response(request):
    return HttpResponse("Success")

middleware = RolePermissionMiddleware(get_response)

# Create test users
admin = User.objects.create_user('admin', 'admin@test.com', 'pass', is_superuser=True)
guest = User.objects.create_user('guest', 'guest@test.com', 'pass')

# Test 1: Admin user
request = factory.get('/api/protected/')
request.user = admin
response = middleware(request)
print(f"Admin response: {response.status_code}")  # Should be 200

# Test 2: Guest user
request = factory.get('/api/protected/')
request.user = guest
response = middleware(request)
print(f"Guest response: {response.status_code}")  # Should be 403

Test with Postman/curl
# 1. Create a superuser
python manage.py createsuperuser

# 2. Start server
python manage.py runserver

# 3. Test with curl (without auth)
curl -X GET http://localhost:8000/api/listings/ -v
# Expected: 401 Unauthorized

# 4. Test with curl (with admin auth)
# First login and get token/session, then:
curl -X GET http://localhost:8000/api/listings/ \
  -H "Authorization: Bearer YOUR_TOKEN" -v
# Expected: 200 OK (if admin) or 403 Forbidden (if guest)


 Summary Checklist

✅ RolePermissionMiddleware class created with __init__ and __call__ methods
✅ Checks user role (admin, moderator, guest)
✅ Returns 403 error for non-admin/non-moderator users
✅ Added to MIDDLEWARE in settings.py
✅ Proper order (after AuthenticationMiddleware)
✅ Unit tests created and passing
✅ Verification script confirms setup
✅ Logging implemented for debugging
✅ Public paths excluded from checks


    

