from django.contrib.admin.widgets import FilteredSelectMultiple

from django.contrib import admin
from django import forms
from django.db import models
from django.forms import Textarea, TextInput
from django.urls import reverse
from django.utils.safestring import mark_safe

from Anecdotes.models import ReactionType, Anecdote, Comment, Category
from Anecdotes.utils import generate_icon_html, generate_reactions_table


class AnecdoteForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=FilteredSelectMultiple('categories', False),
    )

    class Meta:
        model = Anecdote
        fields = (
            'name',
            'content',
            'categories',
        )


class CommentInLines(admin.TabularInline):
    extra = 0
    model = Comment
    template = 'tabular_custom.html'
    readonly_fields = ('created_at', 'updated_at', 'created_by',)
    fields = ('content', 'created_at', 'updated_at', 'created_by')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 60})},
    }


class ReactionTypeForm(forms.ModelForm):
    class Meta:
        model = ReactionType
        fields = ('name', 'color', 'icon')
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


@admin.register(ReactionType)
class ReactionTypeAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('name', 'image_preview',)

    form = ReactionTypeForm

    def image_preview(self, obj):
        return generate_icon_html(obj.icon.as_html(), color=obj.color)


@admin.register(Anecdote)
class AnecdoteAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    readonly_fields = ('rate', 'reactions_details')
    form = AnecdoteForm
    inlines = [CommentInLines]

    def reactions_details(self, obj):
        if not obj.reactions_details:
            return 'No reactions'
        return generate_reactions_table(obj)

    def rate(self, obj):
        if obj.rate['rate'] is None:
            return "No rating"
        return obj.rate['rate']

    def comments(self, obj):
        comments = Comment.objects.filter(commentanecdote__anecdote_id=obj.pk)
        return comments if comments.count() is not 0 else ''

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'created_by') is False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if hasattr(instance, 'created_by') is False:
                instance.created_by = request.user
            instance.save()
        formset.save()


class AnecdoteInLines(admin.TabularInline):
    extra = 0
    model = Anecdote.categories.through
    template = 'tabular_custom_categories.html'
    fields = ('name', 'created_at', 'created_by', 'edit')
    show_change_link = True
    readonly_fields = ('name', 'created_at', 'created_by', 'edit')

    def edit(self, instance):
        return mark_safe('<a href="%s">edit</a>' % \
                         reverse('admin:Anecdotes_anecdote_change',
                                 args=(instance.anecdote.id,)))

    def has_add_permission(self, request, obj=None):
        return False

    def name(self, instance):
        return instance.anecdote.name

    def created_by(self, instance):
        return instance.anecdote.created_by

    def created_at(self, instance):
        return instance.anecdote.created_at

    name.short_description = 'name'
    created_by.short_name = 'created_by'
    created_at.short_name = 'created_at'
    edit.short_name = 'edit'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('name', 'description')
    inlines = [AnecdoteInLines]
