# Generated by Django 3.1.1 on 2020-09-16 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Anecdotes', '0006_auto_20200910_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reactions',
            name='anecdote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Anecdotes.anecdote'),
        ),
        migrations.AlterField(
            model_name='reactions',
            name='reaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Anecdotes.reactiontype'),
        ),
    ]
