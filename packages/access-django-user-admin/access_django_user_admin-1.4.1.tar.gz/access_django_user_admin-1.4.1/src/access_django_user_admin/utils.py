# access_django_user_admin/utils.py
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def get_base_template():
    app_name = getattr(settings, 'APP_NAME', None)

    # Mapping the APP_NAME to the correct template path
    template_mapping = {
        'Service Index': 'Operations_ServiceIndex_Django/templates/services/base_nav_full.html',
        'Dashboard': 'Operations_Dashboard_Django/templates/dashboard/base_nav_full.html',
        'ACCESS Operations API': 'Operations_Warehouse_Django/templates/web/base_nav_full.html',
    }

    return template_mapping.get(app_name, 'base_nav_full.html')

def get_current_app_name():
    return getattr(settings, 'APP_NAME', 'Unknown App')
