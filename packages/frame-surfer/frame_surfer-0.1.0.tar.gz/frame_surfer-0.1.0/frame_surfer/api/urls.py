"""Django API urlpatterns declaration for frame_surfer app."""

from nautobot.apps.api import OrderedDefaultRouter

from frame_surfer.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("frame-surfer", views.FrameSurferFrameTVModelViewSet)
router.register("unsplash", views.FrameSurferUnsplashModelViewSet)
router.register("photo", views.FrameSurferPhotoModelViewSet)

app_name = "frame_surfer-api"
urlpatterns = router.urls
