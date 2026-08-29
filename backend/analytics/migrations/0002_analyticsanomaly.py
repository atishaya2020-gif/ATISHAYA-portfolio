from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('analytics', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='AnalyticsAnomaly',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('traffic_spike', 'Traffic spike'), ('traffic_drop', 'Traffic drop'), ('page_spike', 'Page spike'), ('page_drop', 'Page drop')], max_length=32)),
                ('severity', models.PositiveSmallIntegerField(default=0)),
                ('metric', models.CharField(default='views', max_length=64)),
                ('dimension', models.CharField(blank=True, max_length=500)),
                ('current_value', models.FloatField(default=0)),
                ('baseline_value', models.FloatField(default=0)),
                ('deviation_percent', models.FloatField(default=0)),
                ('z_score', models.FloatField(default=0)),
                ('window_start', models.DateTimeField(db_index=True)),
                ('window_end', models.DateTimeField(db_index=True)),
                ('fingerprint', models.CharField(max_length=255, unique=True)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('acknowledged', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-window_end', '-severity', '-created_at'],
                'indexes': [
                    models.Index(fields=['window_end', '-severity'], name='analytics_a_window__idx'),
                    models.Index(fields=['kind', 'window_end'], name='analytics_a_kind_6e7d5c_idx'),
                ],
            },
        ),
    ]
