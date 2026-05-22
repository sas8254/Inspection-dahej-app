from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class JobType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    performer = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="performed_jobs"
    )
    job_type = models.ForeignKey(
        JobType, on_delete=models.RESTRICT, related_name="jobs"
    )
    plant = models.ForeignKey(Plant, on_delete=models.RESTRICT, related_name="jobs")
    job_date = models.DateField()
    count = models.IntegerField(default=1)
    done = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_jobs"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="updated_jobs",
        blank=True,
        null=True,
    )
    updation_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.job_type.name} - {self.plant.name}"


class OverTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="overtimes")
    plants = models.ManyToManyField(Plant, related_name="overtimes", blank=True)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_overtimes"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="updated_overtimes",
        blank=True,
        null=True,
    )
    updation_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date} - {self.hours} hours"
