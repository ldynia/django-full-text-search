from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]
    operations = [
        migrations.RunSQL("CREATE INDEX description_idx_gin ON search_animal USING GIN(to_tsvector('english', description));"),
        migrations.RunSQL("CREATE INDEX description_tsv_idx_gin ON search_animal USING GIN(description_tsv);"),
        migrations.RunSQL("CREATE INDEX meta_json_idx_gin ON search_animal USING GIN(to_tsvector('english', meta_json));"),
        migrations.RunSQL("""
            CREATE TRIGGER description_update
            BEFORE INSERT OR UPDATE
            ON search_animal
            FOR EACH ROW EXECUTE procedure tsvector_update_trigger(description_tsv, 'pg_catalog.english', description);
        """),
    ]
