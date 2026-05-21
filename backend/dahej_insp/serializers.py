from rest_framework import serializers

from .models import Job, JobType, OverTime, Plant


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ("id", "name")


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ("id", "name")


class JobSerializer(serializers.ModelSerializer):
    # Read-only display fields so clients don't have to do an extra fetch
    # to show human-readable names alongside the FK ids.
    job_type_name = serializers.CharField(source="job_type.name", read_only=True)
    plant_name = serializers.CharField(source="plant.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    updated_by_username = serializers.CharField(source="updated_by.username", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "job_type", "job_type_name",
            "plant", "plant_name",
            "count", "done", "remarks",
            "created_at", "created_by", "created_by_username",
            "updated_at", "updated_by", "updated_by_username",
            "updation_remarks",
        )
        read_only_fields = (
            "id", "created_at", "created_by", "updated_at", "updated_by",
        )


class OverTimeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    plant_names = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    updated_by_username = serializers.CharField(source="updated_by.username", read_only=True)

    class Meta:
        model = OverTime
        fields = (
            "id",
            "user", "user_username",
            "plants", "plant_names",
            "date", "hours", "remarks",
            "created_at", "created_by", "created_by_username",
            "updated_at", "updated_by", "updated_by_username",
            "updation_remarks",
        )
        read_only_fields = (
            "id", "created_at", "created_by", "updated_at", "updated_by",
        )

    def get_plant_names(self, obj):
        return list(obj.plants.values_list("name", flat=True))
