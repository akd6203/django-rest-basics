from django.contrib import admin
from poll.models import Question,Choice, Tag
# Register your models here.

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Tag)