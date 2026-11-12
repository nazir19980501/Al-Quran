from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quran", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ayah",
            name="juz_number",
            field=models.PositiveSmallIntegerField(
                blank=True,
                db_index=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ayah",
            name="hizb_number",
            field=models.PositiveSmallIntegerField(
                blank=True,
                db_index=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ayah",
            name="page_number",
            field=models.PositiveSmallIntegerField(
                blank=True,
                db_index=True,
                null=True,
            ),
        ),
    ]
