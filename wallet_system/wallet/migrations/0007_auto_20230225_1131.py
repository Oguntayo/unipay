# Generated by Django 3.2.16 on 2023-02-25 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0006_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account_balance_after',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account_balance_before',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_account_balance_after',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_account_balance_before',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_account_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('processed', 'Processed'), ('refunded', 'Refunded')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('transfer', 'Transfer'), ('payment', 'Payment'), ('deposit', 'Deposit')], max_length=20, null=True),
        ),
    ]
