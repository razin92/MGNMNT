from django.db import models

# Create your models here.
class AuthorizedUser(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    user_name = models.CharField(max_length=30, blank=True, null=True)
    user_id = models.IntegerField(unique=True)
    telephone = models.CharField(max_length=30, unique=True, blank=True, null=True)
    authorized = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.user_id, self.user_name)
    