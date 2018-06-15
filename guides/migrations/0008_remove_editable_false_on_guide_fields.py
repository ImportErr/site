# Generated by Django 2.0.6 on 2018-06-12 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0007_make_overview_charfield_make_author_uneditable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guide',
            name='_content_rendered',
            field=models.TextField(editable=False),
        ),
        migrations.AlterField(
            model_name='guide',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]