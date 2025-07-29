from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from topobank_publication import views

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(
    r"publication", views.PublicationViewSet, basename="publication-api"
)

urlpatterns = router.urls

app_name = "topobank_publication"
urlprefix = "go/"
urlpatterns += [
    path("publish/", view=views.publish, name="publish"),
    # FIXME: This url has to be absolute
    path("<str:short_url>/", view=views.go, name="go"),
]
