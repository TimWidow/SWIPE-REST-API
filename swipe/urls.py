import debug_toolbar
from django.urls import include, path
from django.conf.urls.static import static

from api.views import APILoginView, APILogoutView
from rest_framework_swagger.views import get_swagger_view

from swipe.settings import MEDIA_ROOT, MEDIA_URL
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# from django.contrib.sites.models import Site
# Site.objects.create(pk=2, domain='http://127.0.0.1:8000/', name='example.com')

schema_view = get_schema_view(
    openapi.Info(
        title="SWIPE API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="eat.twix@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_view = get_swagger_view(title='SWIPE API')

urlpatterns = [path('', swagger_view),
               path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
               path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
               path('api/', include('api.urls')),
               path('api-auth/', include('rest_framework.urls')),  # For logins
               path('accounts/login/', APILoginView.as_view()),
               path('accounts/logout/', APILogoutView.as_view()),
               # path('?next=/', APILogoutView.as_view()),
               path('dj-rest-auth/', include('dj_rest_auth.urls')),
               path('admin/', admin.site.urls),
               path('__debug__/', include(debug_toolbar.urls)),
               ] + static(MEDIA_URL, document_root=MEDIA_ROOT)  # + default_router.urls
