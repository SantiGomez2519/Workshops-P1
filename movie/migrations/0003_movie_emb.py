# Generated by Django 4.2 on 2025-04-07 03:30

from django.db import migrations, models
import movie.models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_movie_genre_movie_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='emb',
            field=models.BinaryField(default=movie.models.get_default_array),
        ),
    ]
