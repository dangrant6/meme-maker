from django.db import models

# Create your models here.
class Meme(models.Model):
    image = models.ImageField(upload_to='memes/')
    caption = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meme #{self.pk}"
