# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from core.models import Profile, Tag, Question, Answer

admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
