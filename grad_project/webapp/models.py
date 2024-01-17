import os

from django.db import models
from django.utils.translation import gettext_lazy as _


class ImageModel(models.Model):
    id = models.TextField("id", primary_key= True)
    dob = models.DateField("date")
    gender = models.TextField("gender")
    image = models.ImageField(_("image"), upload_to='images')

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return str(os.path.split(self.image.path)[-1])