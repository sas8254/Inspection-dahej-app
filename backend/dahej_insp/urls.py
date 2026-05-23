from rest_framework.routers import DefaultRouter

from .views import (
    JobFileViewSet,
    JobTypeViewSet,
    JobViewSet,
    OverTimeViewSet,
    PlantViewSet,
)

app_name = "dahej_insp"

router = DefaultRouter()
router.register("job-types", JobTypeViewSet, basename="jobtype")
router.register("plants", PlantViewSet, basename="plant")
router.register("jobs", JobViewSet, basename="job")
router.register("job-files", JobFileViewSet, basename="jobfile")
router.register("overtimes", OverTimeViewSet, basename="overtime")

urlpatterns = router.urls
