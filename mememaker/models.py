from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Meme(models.Model):
    image = models.ImageField(upload_to='memes/')
    caption = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=255, default='1')
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Meme #{self.pk}"
