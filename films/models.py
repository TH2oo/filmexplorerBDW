from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Film(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    title = models.CharField(max_length=200)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ['user', 'title']  # Pas de doublons par utilisateur

    def __str__(self):
        return f"{self.title} ({self.user.username})"