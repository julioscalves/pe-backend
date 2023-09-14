from django_filters import rest_framework as django_filters
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser


from .models import (
    Requisition,
    Event,
    Status,
    Tag,
    Project,
    Delivery,
)

from .serializers import (
    RequisitionSerializer,
    EventSerializer,
    StatusSerializer,
    TagSerializer,
    ProjectSerializer,
    DeliverySerializer,
    StatisticsSerializer,
)

from users.models import Profile


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filter_backends = [SearchFilter]
    parser_classes = [MultiPartParser]
    search_fields = ["title"]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Project.objects.all()
        queryset = queryset.order_by("title")

        return queryset
    
    def update(self, request, *args, **kwargs):
        request_author = request.data.get('author')
        request_advisor = request.data.get('advisor')
        author_instance = Profile.objects.get(name=request_author)
        advisor_instance = Profile.objects.get(name=request_advisor)

        data_copy = request.data.copy()
        del data_copy['author']
        del data_copy['advisor']

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        instance.author = author_instance
        instance.advisor = advisor_instance

        serializer = self.get_serializer(instance, data=data_copy, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        advisor_name = request.data.get("advisor")
        author_name = request.data.get("author")
        advisor_instance = Profile.objects.get(name=advisor_name)
        author_instance = Profile.objects.get(name=author_name)

        project_serializer = ProjectSerializer(data=request.data)
        if project_serializer.is_valid(raise_exception=True):
            project_serializer.save(advisor=advisor_instance, author=author_instance)

            headers = self.get_success_headers(project_serializer.data)
            return Response(
                project_serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        queryset = Delivery.objects.filter(is_active=True)
        queryset = queryset.order_by("-timestamp")

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        instance.update_tags()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        author_instance = Profile.objects.get(user__username=request.user)
        requisition_protocol = request.data.get("requisition")
        requisition_instance = Requisition.objects.get(protocol=requisition_protocol)
        deliver_serializer = DeliverySerializer(data=request.data)

        if deliver_serializer.is_valid(raise_exception=True):
            deliver_serializer.save(
                author=author_instance, requisition=requisition_instance
            )
            headers = self.get_success_headers(deliver_serializer.data)
            return Response(
                deliver_serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        return Response(deliver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequisitionViewSet(viewsets.ModelViewSet):
    serializer_class = RequisitionSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp"]
    lookup_field = "protocol"
    lookup_value_regex = r"[0-9]+\.[0-9]+"
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        queryset = Requisition.objects.all()
        queryset = queryset.order_by("-timestamp")

        return queryset

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project").split("-")[-1]
        project_instance = Project.objects.get(id=project_id)
        author_instance = Profile.objects.get(id=project_instance.author.id)
        requisition_serializer = RequisitionSerializer(data=request.data)

        received_tag, _ = Tag.objects.get_or_create(name="Recebida")
        tags = [received_tag] + [
            Tag.objects.get_or_create(name=tag)[0] for tag in request.data.get("tags")
        ]

        if requisition_serializer.is_valid(raise_exception=True):
            requisition_instance = requisition_serializer.save(
                author=author_instance, project=project_instance
            )
            requisition_instance.tags.set(tags)
            headers = self.get_success_headers(requisition_serializer.data)
            return Response(
                requisition_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        return Response(
            requisition_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class RequisitionEventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Event.objects.all()

        else:
            raise PermissionDenied(
                "Você não possui as permissões necessárias para acessar este recurso."
            )


class RequisitionStatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        return Status.objects.all()


class RequisitionTagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Tag.objects.all()
        queryset = queryset.order_by("name")
        return queryset


class StatisticsFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="requisition__date", lookup_expr="gte"
    )
    end_date = django_filters.DateFilter(
        field_name="requisition__date", lookup_expr="lte"
    )

    class Meta:
        model = Delivery
        fields = ["start_date", "end_date"]


class StatisticsViewSet(viewsets.ModelViewSet):
    serializer_class = StatisticsSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StatisticsFilter
    ordering_fields = ["date", "males", "females"]
    pagination_class = None

    def get_queryset(self):
        queryset = Delivery.objects.select_related("requisition")

        return queryset

    def generate_statistics(self, queryset): 
        data = {
            "by_total": {
                "required_males": 0,
                "required_females": 0,
                "delivered_males": 0,
                "delivered_females": 0,
            },
            "by_protocol": {},
            "by_institute": {},
            "by_department": {},
            "by_advisor": {},
            "by_author": {},
            "by_project": {},
            "by_tags": {},
        }

        for query in queryset:
            protocol = query.requisition.protocol
            institute = query.requisition.project.advisor.institute
            department = query.requisition.project.advisor.department
            advisor = query.requisition.project.advisor
            author = query.requisition.project.author
            project = query.requisition.project

            mapping = {
                "by_protocol": protocol,
                "by_institute": institute.abbreviation,
                "by_department": f"{department.name} ({institute.abbreviation})",
                "by_advisor": advisor.name,
                "by_author": author.name,
                "by_project": project.title,
            }
            for key, value in zip(mapping.keys(), mapping.values()):
                if not value in data[key]:
                    data[key][value] = {
                        "required_males": 0,
                        "required_females": 0,
                        "delivered_males": 0,
                        "delivered_females": 0,
                    }

            for tag in query.requisition.tags.all():
                data["by_tags"][tag.name] = {
                    "required_males": 0,
                    "required_females": 0,
                    "delivered_males": 0,
                    "delivered_females": 0,
                }

        processed = []

        for query in queryset:
            protocol = query.requisition.protocol
            institute = query.requisition.project.advisor.institute
            department = query.requisition.project.advisor.department
            advisor = query.requisition.project.advisor
            author = query.requisition.project.author
            project = query.requisition.project

            if protocol not in processed:
                data["by_protocol"][protocol][
                    "required_males"
                ] += query.requisition.males
                data["by_protocol"][protocol][
                    "required_females"
                ] += query.requisition.females

                data["by_institute"][institute.abbreviation][
                    "required_males"
                ] += query.requisition.males
                data["by_institute"][institute.abbreviation][
                    "required_females"
                ] += query.requisition.females

                data["by_department"][

                    department.name
                ]["required_males"] += query.requisition.males
                data["by_department"][
                    department.name
                ]["required_females"] += query.requisition.females

                data["by_advisor"][advisor.name][
                    "required_males"
                ] += query.requisition.males
                data["by_advisor"][advisor.name][
                    "required_females"
                ] += query.requisition.females

                data["by_author"][author.name][
                    "required_males"
                ] += query.requisition.males
                data["by_author"][author.name][
                    "required_females"
                ] += query.requisition.females

                data["by_project"][project.title][
                    "required_males"
                ] += query.requisition.males
                data["by_project"][project.title][
                    "required_females"
                ] += query.requisition.females

                for tag in query.requisition.tags.all():
                    data["by_tags"][tag.name][
                        "required_males"
                    ] += query.requisition.males
                    data["by_tags"][tag.name][
                        "required_females"
                    ] += query.requisition.females

                data["by_total"]["required_males"] += query.requisition.males
                data["by_total"]["required_females"] += query.requisition.females

            data["by_protocol"][protocol][
                "delivered_males"
            ] += query.males
            data["by_protocol"][protocol][
                "delivered_females"
            ] += query.females


            data["by_institute"][institute.abbreviation][
                "delivered_males"
            ] += query.males
            data["by_institute"][institute.abbreviation][
                "delivered_females"
            ] += query.females

            data["by_department"][department.name][
                "delivered_males"
            ] += query.males
            data["by_department"][department.name][
                "delivered_females"
            ] += query.females

            data["by_advisor"][advisor.name][
                "delivered_males"
            ] += query.males
            data["by_advisor"][advisor.name][
                "delivered_females"
            ] += query.females

            data["by_author"][author.name][
                "delivered_males"
            ] += query.males
            data["by_author"][author.name][
                "delivered_females"
            ] += query.females

            data["by_project"][project.title][
                "delivered_males"
            ] += query.males
            data["by_project"][project.title][
                "delivered_females"
            ] += query.females

            data["by_total"]["delivered_males"] += query.males
            data["by_total"]["delivered_females"] += query.females

            for tag in query.requisition.tags.all():
                data["by_tags"][tag.name]["delivered_males"] += query.males
                data["by_tags"][tag.name]["delivered_females"] += query.females

            processed.append(protocol)

        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.generate_statistics(queryset)

        return Response(data)
