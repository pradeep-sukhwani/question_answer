from django.db import models
from django_extensions.db.fields import AutoSlugField


class Tag(models.Model):
    name = models.CharField("Tag Name", help_text="Name of the tag", max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return u"{id}_{name}".format(id=self.id, name=self.slug)
