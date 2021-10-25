from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    designation = models.CharField(max_length=20, null=False, blank=False)
    salary = models.IntegerField(null=True, blank=True)
    picture = models.ImageField(upload_to='pictures/%Y/%m/%d/', max_length=255, null=True, blank=True)

    class Meta:
        ordering = ('-salary',)

    def __str__(self):
        return "{0} - {1}".format(self.user.username, self.designation)