from django.contrib.auth.models import User
from django.db import models


class Institute(models.Model):
    name = models.CharField(max_length=60, unique=True, null=False)
    abbreviation = models.CharField(max_length=12, unique=True, null=False, blank=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.abbreviation:
            self.abbreviation = "".join(
                [word[0].upper() for word in self.name.split(" ")]
            )

        super(Institute, self).save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=60, unique=True, null=False)
    institute = models.ForeignKey("users.Institute", on_delete=models.CASCADE)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=False)
    is_advisor = models.BooleanField(default=False)
    institute = models.ForeignKey(
        "users.Institute", on_delete=models.CASCADE, null=True, blank=True
    )
    department = models.ForeignKey(
        "users.Department", on_delete=models.CASCADE, null=True, blank=True
    )
    requisitions = models.ForeignKey(
        "requisitions.Requisition", on_delete=models.CASCADE, null=True, blank=True
    )
    phone = models.CharField(max_length=25, null=True, blank=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.institute}/{self.department}"
