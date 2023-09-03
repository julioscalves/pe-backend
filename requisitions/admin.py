from django.contrib import admin

from .models import Requisition, Event, Status, Tag, Delivery, Project

admin.site.register(Requisition)
admin.site.register(Event)
admin.site.register(Status)
admin.site.register(Tag)
admin.site.register(Delivery)
admin.site.register(Project)
