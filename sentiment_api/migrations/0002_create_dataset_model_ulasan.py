from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sentiment_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_file', models.CharField(max_length=255)),
                ('tanggal_upload', models.DateTimeField(auto_now_add=True)),
                ('jumlah_data', models.IntegerField(default=0)),
                ('jumlah_positif', models.IntegerField(default=0)),
                ('jumlah_netral', models.IntegerField(default=0)),
                ('jumlah_negatif', models.IntegerField(default=0)),
                ('processing_time_seconds', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Dataset',
                'verbose_name_plural': 'Daftar Dataset',
                'db_table': 'dataset',
                'ordering': ['-tanggal_upload'],
            },
        ),
        migrations.CreateModel(
            name='ModelML',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_model', models.CharField(default='Support Vector Machine', max_length=100)),
                ('accuracy', models.FloatField(default=0.0)),
                ('precision', models.FloatField(default=0.0)),
                ('recall', models.FloatField(default=0.0)),
                ('f1_score', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Model ML',
                'verbose_name_plural': 'Daftar Model ML',
                'db_table': 'model',
            },
        ),
        migrations.CreateModel(
            name='Ulasan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal', models.DateField(blank=True, null=True)),
                ('review_text', models.TextField()),
                ('label_sentimen', models.CharField(blank=True, max_length=20, null=True)),
                ('hasil_prediksi', models.CharField(max_length=20)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ulasan_list', to='sentiment_api.dataset')),
            ],
            options={
                'verbose_name': 'Ulasan',
                'verbose_name_plural': 'Daftar Ulasan',
                'db_table': 'ulasan',
            },
        ),
    ]
