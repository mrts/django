from django.db import models
from django.utils.translation import ugettext_lazy as _

class PickleMe(models.Model):
    name = models.CharField(_("Name"), max_length=10)
