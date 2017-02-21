from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class FormDefinition(models.Model):
    edi_code = models.CharField(max_length=64, verbose_name=_("edi code"))
    edi_operator = models.CharField(max_length=64, verbose_name=_("edi operator"))
