from rest_framework import serializers

from users.serializers import ProfileSerializer

from .models import (
    Requisition,
    Event,
    Status,
    Tag,
    Project,
    Delivery,
)


class RequisitionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisition
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    advisor = ProfileSerializer(read_only=True)
    lookup_field = "slug"

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            "project_file": {"required": False},
            "ceua_file": {"required": False},
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class DeliverySerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    requisition = RequisitionBaseSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class StatusSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Status
        fields = "__all__"


class RequisitionSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    deliveries = serializers.SerializerMethodField()
    events = EventSerializer(many=True, source="requisition_event", read_only=True)
    status = StatusSerializer(many=True, source="requisition_status", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Requisition
        fields = "__all__"

    def to_representation(self, instance):
        instance = (
            Requisition.objects.select_related("author", "project")
            .prefetch_related("tags")
            .get(pk=instance.pk)
        )

        return super().to_representation(instance)

    def get_deliveries(self, instance):
        active_deliveries = instance.requisition_delivery.filter(is_active=True)
        serializer = DeliverySerializer(active_deliveries, many=True)
        return serializer.data


class StatisticsSerializer(serializers.ModelSerializer):
    requisition = RequisitionSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = ["date", "males", "females", "requisition"]
