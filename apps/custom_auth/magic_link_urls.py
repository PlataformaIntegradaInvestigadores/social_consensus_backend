"""
URLs for magic link authentication system
"""
from django.urls import path
from . import magic_link_views

urlpatterns = [
    # Magic link authentication
    path('magic-link/', magic_link_views.magic_link_login_page, name='magic_link_login'),
    path('magic-link/generate/', magic_link_views.generate_magic_link, name='magic_link_generate'),
    path('magic-link/verify/<str:token>/', magic_link_views.verify_magic_link, name='magic_link_verify'),
    
    # Quick login for testing
    path('quick-login/', magic_link_views.quick_login, name='quick_login'),
    
    # Test users list
    path('test-users/', magic_link_views.test_users_list, name='test_users_list'),
]
