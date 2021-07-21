from django.contrib import admin
from .models import Photo, Tag, Message, Order, Topic, Response

admin.site.register(Photo)
admin.site.register(Tag)
admin.site.register(Message)
admin.site.register(Order)
admin.site.register(Topic)
admin.site.register(Response)