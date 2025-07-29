"""Models."""

from django.db import models
from app_utils.django import users_with_permission

class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = True
        default_permissions = ()
        permissions = (
            ("basic_access", "Can view the taxes"),
            ("admin_access", "Admin access")
        )
    
    dummy = models.BooleanField(default=True)
