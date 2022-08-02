from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count, Avg
from fontawesome_5.fields import IconField
from django.contrib.auth.models import User


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=20, null=False)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Anecdote(models.Model):
    name = models.CharField(max_length=100, null=False, )
    content = models.TextField(null=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(
        Category,
        related_name='categories_anecdotes',
        blank=False,
    )

    def __str__(self):
        return self.name

    @property
    def reactions_details(self):
        reactions = self.reactions_set\
            .extra(select={'id': 'reaction_id'})\
            .values('id', 'reaction__icon', 'reaction__color', 'reaction__name')\
            .annotate(count=Count('reaction_id'))\
            .order_by('id')

        for reaction in reactions:
            reaction['reaction__icon'] = reaction['reaction__icon'].as_html()
        return reactions

    @property
    def reactions(self):
        return self.reactions_set\
            .extra(select={'id': 'reaction_id'})\
            .values('id',)\
            .annotate(count=Count('reaction_id'))\
            .order_by('id')

    @property
    def rate(self):
        return self.rating_set.values('rate').exclude(rate=0).aggregate(rate=Avg('rate'))

    def save(self, *args, **kwargs):
        super(Anecdote, self).save(*args, **kwargs)


class Comment(models.Model):
    content = models.TextField(max_length=200, null=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    anecdote = models.ForeignKey(
        Anecdote,
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.created_by.username


class ReactionType(models.Model):
    name = models.CharField(max_length=20, null=False)
    icon = IconField()
    color = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Reactions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    anecdote = models.ForeignKey(
        Anecdote,
        on_delete=models.CASCADE
    )
    reaction = models.ForeignKey(
        ReactionType,
        on_delete=models.CASCADE
    )
    reacted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'anecdote', 'reaction'),)


class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    anecdote = models.ForeignKey(
        Anecdote,
        on_delete=models.CASCADE
    )
    rate = models.PositiveIntegerField(null=False, validators=[MinValueValidator(0), MaxValueValidator(5)])

    unique_together = (('user', 'anecdote',),)
