from django.conf import settings
from django.db import models

def company_directory_path(instance, filename):
    return f'companies/company_{instance.id}/{filename}'

def vendor_directory_path(instance, filename):
    return f'vendors/vendor_{instance.id}/{filename}'


class Company(models.Model):
    rnc = models.IntegerField(max_length=9, blank=False, unique=True)
    name = models.CharField(max_lenght=150, blank=False)
    slug = models.SlugField(editable=False, blank=True, default='')
    logo = models.ImageField(
        upload_to=company_directory_path,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        'users.Vendor',
        related_name='company'
    )

    class Meta:
        verbose_name = 'company'
        verbose_name_plural = 'companies'
        unique_together = (
            ('rnc', 'name')
        )


class Vendor(models.Model):
    name = models.CharField(max_length=100, is_blank=False)
    registered_at = models.DateTimeField(auto_=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='vendor_info',
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'users.Company',
        related_name='vendors',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )


class Address(models.Model):
    state_or_province = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    address_line_one = models.CharField(max_lenght=150)

