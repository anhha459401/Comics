from django.forms.widgets import RadioSelect
from django.db import models


class CustomBooleanField(models.BooleanField):
    def formfield(self, **kwargs):
        kwargs["widget"] = RadioSelect(choices=((True, "True"), (False, "False")))
        kwargs["initial"] = True
        return super().formfield(**kwargs)
