from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
import random




class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.email})"



class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(unique=True,max_length=20,null=True)
    account_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now=True)
    
def generate_account_number():
    while True:
        account_number = random.randint(1000000000, 9999999999)
        check = Account.objects.filter(account_number=account_number)
        if not check.exists():
            return str(account_number)

            
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, account_number=generate_account_number())


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('transfer', 'Transfer'),
        ('fundwallet', 'Fundwallet'),
    )

    TRANSACTION_STATUSES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    TRANSACTION_CHANNELS = (
        ('card', 'Card'),
        ('wallet', 'Wallet'),
        ('bank', 'Bank'),
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, null=True, blank=True)
    transaction_channel = models.CharField(max_length=20, choices=TRANSACTION_CHANNELS, null=True, blank=True)
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, null=True, blank=True)

    sender_account_name = models.CharField(max_length=255, null=True, blank=True)
    sender_account_number = models.CharField(max_length=50, null=True, blank=True)
    sender_bank = models.CharField(max_length=255, null=True, blank=True)
    sender_email = models.EmailField(null=True, blank=True)
    sender_account_balance_before = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sender_account_balance_after = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    receiver_account_name = models.CharField(max_length=255, null=True, blank=True)
    receiver_account_number = models.CharField(max_length=50, null=True, blank=True)
    receiver_bank = models.CharField(max_length=255, null=True, blank=True)
    receiver_email = models.EmailField(null=True, blank=True)
    receiver_account_balance_before = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    receiver_account_balance_after = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    transaction_reference = models.CharField(max_length=50, null=True, blank=True)
    transaction_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    transaction_description = models.TextField(null=True, blank=True)
    transaction_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.transaction_type} of {self.transaction_amount}'
