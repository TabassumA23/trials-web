from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_remove_descriptions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=128),
        ),
    ]
