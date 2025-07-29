"""
Magic Link authentication views for testing purposes
"""
import uuid
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from apps.custom_auth.models import MagicLink

User = get_user_model()


def magic_link_login_page(request):
    """
    Display the magic link login page
    """
    return render(request, 'custom_auth/magic_link_login.html')


@csrf_exempt
def generate_magic_link(request):
    """
    Generate a magic link for testing purposes
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Create magic link
            magic_link = MagicLink.objects.create(
                user=user,
                token=str(uuid.uuid4()),
                expires_at=timezone.now() + timedelta(minutes=30)
            )
            
            # Generate the magic link URL
            magic_url = request.build_absolute_uri(
                reverse('magic_link_verify', kwargs={'token': magic_link.token})
            )
            
            # For testing, return the link directly instead of sending email
            return JsonResponse({
                'success': True,
                'magic_link': magic_url,
                'message': f'Magic link generated for {user.email}',
                'expires_in': '30 minutes'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def verify_magic_link(request, token):
    """
    Verify and use a magic link to log in the user
    """
    try:
        magic_link = MagicLink.objects.get(token=token)
        
        if not magic_link.is_valid():
            messages.error(request, 'This magic link has expired or been used.')
            return redirect('magic_link_login')
        
        # Mark the magic link as used
        magic_link.mark_as_used()
        
        # Log in the user
        login(request, magic_link.user)
        
        # Redirect to dashboard or home page
        messages.success(request, f'Welcome back, {magic_link.user.first_name}!')
        return redirect('dashboard')  # Adjust this URL as needed
        
    except MagicLink.DoesNotExist:
        messages.error(request, 'Invalid magic link.')
        return redirect('magic_link_login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('magic_link_login')


def test_users_list(request):
    """
    Display a list of all test users for easy access during testing
    """
    researchers = User.objects.filter(email__contains='test', is_staff=False).order_by('email')
    companies = User.objects.filter(email__contains='test', is_staff=True).order_by('email')
    
    context = {
        'researchers': researchers,
        'companies': companies,
        'base_url': request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    }
    
    return render(request, 'custom_auth/test_users_list.html', context)


@csrf_exempt
def quick_login(request):
    """
    Quick login for testing - directly log in a user by email
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': f'Logged in as {user.first_name} {user.last_name}',
                'redirect_url': '/dashboard/'  # Adjust as needed
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
