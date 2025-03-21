# Generated by Django 4.2.17 on 2025-03-18 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_product_category_product_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('plates', 'Plates'), ('bowls', 'Bowls'), ('cups', 'Cups'), ('cutlery', 'Cutlery'), ('trays', 'Trays')], default='plates', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
    ]
