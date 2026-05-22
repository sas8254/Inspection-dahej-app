from rest_framework import viewsets

from .models import Job, JobType, OverTime, Plant
from .serializers import (
    JobSerializer,
    JobTypeSerializer,
    OverTimeSerializer,
    PlantSerializer,
)


class JobTypeViewSet(viewsets.ModelViewSet):
    queryset = JobType.objects.all().order_by("name")
    serializer_class = JobTypeSerializer


class PlantViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all().order_by("name")
    serializer_class = PlantSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer

    def get_queryset(self):
        # select_related avoids N+1 queries when the serializer reads
        # job_type.name / plant.name / created_by.username for each row.
        return (
            Job.objects
            .select_related("job_type", "plant", "performer", "created_by", "updated_by")
            .all()
        )

    def perform_create(self, serializer):
        # created_by / updated_by are derived from the request, not the client.
        # On create, both point to the same user (covers the NOT NULL constraint
        # cleanly without requiring the client to send updated_by).
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class OverTimeViewSet(viewsets.ModelViewSet):
    serializer_class = OverTimeSerializer

    def get_queryset(self):
        return (
            OverTime.objects
            .select_related("user", "created_by", "updated_by")
            .prefetch_related("plants")
            .all()
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
