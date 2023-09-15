import random
from datetime import datetime
from django.db import models

from users.models import Profile
from .utils.utils import generate_slug, generate_unique_slug

REQUISITION_OPTIONS = [
    ("RE", "Recebida"),
    ("PR", "Em Produção"),
    ("CO", "Concluída"),
    ("PA", "Parcialmente concluída"),
    ("SU", "Suspensa"),
    ("CA", "Cancelada"),
]


class Project(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="")
    project_file = models.FileField(upload_to="uploads/projects", null=True, blank=True)
    ceua_protocol = models.CharField(max_length=16, blank=False, null=False)
    ceua_file = models.FileField(upload_to="uploads/ceua", null=True, blank=True)
    slug = models.SlugField(max_length=50, blank=True, null=False)
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="project_author"
    )
    advisor = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="profile_advisor"
    )

    def __str__(self):
        return f"{self.title} - {self.author}, {self.advisor}"

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = generate_unique_slug(self.title)
            while Project.objects.filter(slug=slug).exists():
                slug = generate_unique_slug(self.title)
            self.slug = slug

        super().save(*args, **kwargs)


class Delivery(models.Model):
    date = models.DateField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE, null=True)
    males = models.PositiveSmallIntegerField(default=0)
    females = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    requisition = models.ForeignKey(
        "requisitions.Requisition",
        on_delete=models.CASCADE,
        related_name="requisition_delivery",
    )

    def __str__(self):
        return f"{self.requisition.protocol}: {self.date} - {self.males}M | {self.females}F"

    def update_tags(self):
        requisition = Requisition.objects.get(id=self.requisition_id)
        all_deliveries = Delivery.objects.filter(
            requisition__id=self.requisition_id
        ).aggregate(males=models.Sum("males"), females=models.Sum("females"))
        received_tag, _ = Tag.objects.get_or_create(name="Recebida")
        partial_tag, _ = Tag.objects.get_or_create(name="Parcialmente Concluída")
        concluded_tag, _ = Tag.objects.get_or_create(name="Concluída")

        males_satisfied = (
            all_deliveries["males"] is None
            or all_deliveries["males"] >= requisition.males
        )
        females_satisfied = (
            all_deliveries["females"] is None
            or all_deliveries["females"] >= requisition.females
        )

        males_partially_satisfied = (
            all_deliveries["males"] is None
            or all_deliveries["males"] < requisition.males
        )
        females_partially_satisfied = (
            all_deliveries["females"] is None
            or all_deliveries["females"] < requisition.females
        )

        if males_satisfied and females_satisfied:
            requisition.tags.add(concluded_tag)
            requisition.tags.remove(partial_tag)
            if not Status.objects.filter(status="CO", requisition=requisition):
                Status.objects.create(
                    status="CO",
                    message="Estado alterado para requisição concluída.",
                    requisition=requisition,
                )
            requisition.tags.remove(received_tag)

        elif males_partially_satisfied and females_partially_satisfied:
            requisition.tags.add(partial_tag)
            requisition.tags.remove(concluded_tag)
            if not Status.objects.filter(status="PA", requisition=requisition):
                Status.objects.create(
                    status="PA",
                    message="Estado alterado para requisição em andamento.",
                    requisition=requisition,
                )

            requisition.tags.remove(received_tag)

        else:
            requisition.tags.add(received_tag)
            requisition.tags.remove(concluded_tag)
            requisition.tags.remove(partial_tag)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_tags()


class Event(models.Model):
    title = models.CharField(max_length=60)
    message = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE, null=True)
    requisition = models.ForeignKey(
        "requisitions.Requisition",
        on_delete=models.CASCADE,
        related_name="requisition_event",
    )

    def __str__(self):
        return self.title


class Status(models.Model):
    status = models.CharField(max_length=2, choices=REQUISITION_OPTIONS, default="EN")
    message = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE, null=True)
    requisition = models.ForeignKey(
        "requisitions.Requisition",
        on_delete=models.CASCADE,
        related_name="requisition_status",
    )

    def __str__(self):
        return f"{self.requisition.protocol} - {self.get_status_display()} - {self.timestamp}"


class Tag(models.Model):
    TAG_COLOR_CHOICES = [
        ("slate", "slate"),
        ("gray", "gray"),
        ("zinc", "zinc"),
        ("neutral", "neutral"),
        ("stone", "stone"),
        ("red", "red"),
        ("orange", "orange"),
        ("amber", "amber"),
        ("yellow", "yellow"),
        ("lime", "lime"),
        ("green", "green"),
        ("emerald", "emerald"),
        ("teal", "teal"),
        ("cyan", "cyan"),
        ("sky", "sky"),
        ("blue", "blue"),
        ("indigo", "indigo"),
        ("violet", "violet"),
        ("purple", "purple"),
        ("fuchsia", "fuchsia"),
        ("pink", "pink"),
        ("rose", "rose"),
    ]

    name = models.CharField(max_length=48, unique=True)
    description = models.TextField(blank=True, default="")
    slug = models.SlugField(max_length=16, blank=True, null=False, unique=True)
    color = models.CharField(
        max_length=7, default="blue", blank=True, choices=TAG_COLOR_CHOICES
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name.lower(), 16)

        super().save(*args, **kwargs)


class Requisition(models.Model):
    protocol = models.CharField(max_length=12, unique=True, editable=False)
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    males = models.PositiveSmallIntegerField(default=0)
    females = models.PositiveSmallIntegerField(default=0)
    tags = models.ManyToManyField(
        "requisitions.Tag", blank=True, related_name="requisition_tags"
    )
    project = models.ForeignKey("requisitions.Project", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="requisition_author",
        null=True,
    )
    author_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return self.protocol

    def generate_protocol(self):
        current_year = datetime.now().year

        while True:
            random_id = "".join([str(random.randint(0, 9)) for _ in range(5)])
            protocol = f"{random_id}.{current_year}"

            if not Requisition.objects.filter(protocol=protocol).exists():
                return protocol

    def save(self, *args, **kwargs):
        if not self.protocol:
            self.protocol = self.generate_protocol()

        super().save(*args, **kwargs)

        if not Delivery.objects.filter(requisition=self).exists():
            Delivery.objects.create(
                requisition=self,
                is_active=False,
                date=datetime.now(),
                notes="Inicialização de entrega.",
            )

        if not Status.objects.filter(requisition=self).exists():
            Status.objects.create(
                status="RE",
                message="Requisição recebida.",
                requisition=self,
            )
