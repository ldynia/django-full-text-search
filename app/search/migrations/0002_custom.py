from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
      migrations.RunSQL("CREATE INDEX description_gin_idx ON search_animal USING GIN(to_tsvector('english', description));"),
    ]
