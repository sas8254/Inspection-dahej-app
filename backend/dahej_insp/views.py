from django.db.models import Max, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    def _filtered_queryset(self):
        qs = (
            Job.objects
            .select_related("job_type", "plant", "performer", "created_by", "updated_by")
            .all()
        )
        params = self.request.query_params
        performer = params.get("performer")
        job_type = params.get("job_type")
        plant = params.get("plant")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        if performer:
            qs = qs.filter(performer_id=performer)
        if job_type:
            qs = qs.filter(job_type_id=job_type)
        if plant:
            qs = qs.filter(plant_id=plant)
        if date_from:
            qs = qs.filter(job_date__gte=date_from)
        if date_to:
            qs = qs.filter(job_date__lte=date_to)
        return qs

    def get_queryset(self):
        return self._filtered_queryset()

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

    @action(detail=False, methods=["get"])
    def ranking(self, request):
        # Total count per performer under current filters. Highest first; ties
        # broken by most recent job (more recent ranks higher).
        qs = self._filtered_queryset()
        rows = (
            qs.values(
                "performer_id",
                "performer__username",
                "performer__first_name",
                "performer__last_name",
            )
            .annotate(total_count=Sum("count"), last_at=Max("job_date"))
            .order_by("-total_count", "-last_at")
        )
        result = []
        for idx, r in enumerate(rows, start=1):
            result.append({
                "rank": idx,
                "user_id": r["performer_id"],
                "username": r["performer__username"],
                "first_name": r["performer__first_name"],
                "last_name": r["performer__last_name"],
                "total_count": r["total_count"],
                "last_at": r["last_at"],
            })
        return Response(result)


class OverTimeViewSet(viewsets.ModelViewSet):
    serializer_class = OverTimeSerializer

    def _filtered_queryset(self):
        qs = (
            OverTime.objects
            .select_related("user", "created_by", "updated_by")
            .prefetch_related("plants")
            .all()
        )
        params = self.request.query_params
        user = params.get("user")
        plant = params.get("plant")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        if user:
            qs = qs.filter(user_id=user)
        if plant:
            qs = qs.filter(plants__id=plant).distinct()
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_queryset(self):
        return self._filtered_queryset()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=["get"])
    def ranking(self, request):
        # Total hours per user under current filters. Highest first; ties broken
        # by most recent overtime date (more recent ranks higher).
        qs = self._filtered_queryset()
        rows = (
            qs.values("user_id", "user__username", "user__first_name", "user__last_name")
            .annotate(total_hours=Sum("hours"), last_date=Max("date"))
            .order_by("-total_hours", "-last_date")
        )
        result = []
        for idx, r in enumerate(rows, start=1):
            result.append({
                "rank": idx,
                "user_id": r["user_id"],
                "username": r["user__username"],
                "first_name": r["user__first_name"],
                "last_name": r["user__last_name"],
                "total_hours": r["total_hours"],
                "last_date": r["last_date"],
            })
        return Response(result)
