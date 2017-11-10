from django.conf import settings
from django.db import models
from django.utils.text import slugify

def company_directory_path(instance, filename):
    return f'companies/company_{instance.id}/{filename}'

def vendor_directory_path(instance, filename):
    return f'vendors/vendor_{instance.id}/{filename}'


class Company(models.Model):
    rnc = models.CharField(max_length=9, blank=False, unique=True)
    name = models.CharField(max_length=150, blank=False)
    slug = models.SlugField(editable=False, blank=True, default='')
    logo = models.ImageField(
        upload_to=company_directory_path,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.OneToOneField(
        'users.Vendor',
        related_name='company',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'company'
        verbose_name_plural = 'companies'
        unique_together = (
            ('rnc', 'name')
        )


class Person(models.Model):
    name = models.CharField(max_length=125, blank=False)
    display_name = models.CharField(max_length=125, blank=True, null=True)
    primary_phone = models.CharField(max_length=14, blank=False)
    secondary_phone = models.CharField(max_length=14, blank=True)
    national_id = models.OneToOneField(
        'users.NationalId',
        related_name='owner',
        on_delete=models.CASCADE
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='person_info',
        on_delete=models.CASCADE
    )
    address = models.ForeignKey(
        'users.Address',
        related_name='owner',
        on_delete=models.CASCADE
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Person, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = self.name
        super(Person, self).clean(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: {self.display_name}'


class Vendor(Person):
    company = models.ForeignKey(
        'users.Company',
        related_name='vendors',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    picture = models.ImageField(
        upload_to=vendor_directory_path,
        blank=True,
        null=True
    )
    
    class Meta(Person.Meta):
        verbose_name = 'vendor'
        verbose_name_plural = 'vendors'


class Client(Person):
    pass


class NationalId(models.Model):
    CEDULA = 0
    PASSPORT = 1
    SSN = 2
    ID_TYPE_CHOICES = (
        (CEDULA, 'Cedula'),
        (PASSPORT, 'Passport'),
        (SSN, 'Social Security Number')
    )
    id_type = models.IntegerField(
        choices=ID_TYPE_CHOICES,
        default=CEDULA,
        verbose_name='ID Type: Cedula, SSN, Passport'
    )
    id_number = models.CharField(max_length=15, blank=False)

    def __str__(self):
        if self.id_type == 0:
            return f'{self.id_number[:3]}-{self.id_number[3:10]}-{self.id_number[-1:]}'
        elif self.id_type == 1:
            return f'{self.id_number}'
        elif self.id_type == 2:
            return f'{self.id_number[:3]}-{self.id_number[3:5]}-{self.id_number[-4:]}'


class Address(models.Model):
    full_name = models.CharField(max_length=100, blank=False)
    state_province_region = models.CharField(max_length=50, blank=False)
    city = models.CharField(max_length=50, blank=False)
    sector = models.CharField(max_length=50, blank=False)
    address_line_one = models.CharField(max_length=150, blank=False)
    address_line_two = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=14, blank=False)
    is_primary = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Address, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = self.name
        super(Address, self).clean(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: {self.display_name}'
