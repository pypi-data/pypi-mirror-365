"""Django urlpatterns declaration for frame_surfer app."""

from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from frame_surfer import views

app_name = "frame_surfer"
router = NautobotUIViewSetRouter()

# The standard is for the route to be the hyphenated version of the model class name plural.
# for example, ExampleModel would be example-models.
# router.register("frame-surfer-example-models", views.FrameSurferExampleModelUIViewSet)
router = NautobotUIViewSetRouter()
router.register(r"frame-tv", views.FrameSurferFrameTVModelUIViewSet, basename="frametv")
router.register(r"unsplashmodel", views.FrameSurferUnsplashModelUIViewSet, basename="unsplashmodel")
router.register(r"photomodel", views.FrameSurferPhotoModelUIViewSet, basename="photomodel")


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("frame_surfer/docs/index.html")), name="docs"),
    path("", include(router.urls)),
]
urlpatterns += router.urls
