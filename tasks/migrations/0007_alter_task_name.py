# Generated by Django 4.1.6 on 2023-03-02 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0006_alter_task_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="name",
            field=models.CharField(max_length=50),
        ),
    ]
