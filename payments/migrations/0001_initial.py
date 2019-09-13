# Generated by Django 2.2 on 2019-09-11 17:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import payments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_order_id', models.CharField(default=payments.models.payment_order_id_generator, max_length=64)),
                ('txnid', models.CharField(blank=True, max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('gateway', models.CharField(choices=[('PT', 'Paytm')], default='PT', max_length=2)),
                ('status', models.CharField(choices=[('SC', 'Success'), ('FL', 'Failed')], default='IN', max_length=2)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]