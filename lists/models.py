from django.db import models
from django.urls import reverse


class List(models.Model):
    pass

    def __str__(self):
        return self.id


    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])



class Item(models.Model):
    text = models.TextField(default='', blank=False)
    list = models.ForeignKey(List, default=None, on_delete='CASCADE')

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text
