# Generated by Django 4.2.17 on 2025-03-18 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Charged', 'Charged'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], default='Pending', max_length=50),
        ),
    ]
