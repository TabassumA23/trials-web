from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_trialoption_question"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trialoption",
            name="description",
        ),
        migrations.RemoveField(
            model_name="trialquestion",
            name="description",
        ),
    ]
