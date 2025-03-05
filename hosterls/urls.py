"""
URL configuration for hosterls project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from hostel.views import home,login_hosteller,generate_invoice
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your other URL patterns

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from hostel import views # Import the login view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', login_hosteller, name='login_hosteller'),  # Map the URL to the view
    path('', home, name='home'),  # Add this line for the home page
    path('hostel/', include('hostel.urls')),  # Make sure to replace 'your_app_name' with the actual app name
    #path('hostels/', include('scanexit.urls')),  # Make sure to replace 'your_app_name' with the actual app name
    path('', include('hostel.urls')),  # Replace 'your_app' with the actual app name

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)