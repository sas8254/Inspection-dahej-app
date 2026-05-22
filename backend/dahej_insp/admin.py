from django.contrib import admin

from .models import Job, JobType, OverTime, Plant


@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "job_type", "plant", "performer", "count", "done", "created_by", "created_at")
    list_filter = ("done", "job_type", "plant", "performer", "created_at")
    search_fields = ("remarks", "updation_remarks")
    autocomplete_fields = ("job_type", "plant", "performer", "created_by", "updated_by")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(OverTime)
class OverTimeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "hours", "created_by", "created_at")
    list_filter = ("date", "user")
    search_fields = ("remarks", "updation_remarks")
    autocomplete_fields = ("user", "created_by", "updated_by")
    filter_horizontal = ("plants",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"
