import googlemaps
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.text import slugify

def company_directory_path(instance, filename):
    return f'companies/company_{instance.id}/{filename}'

def customer_directory_path(instance, filename):
    return f'users/user_{instance.user.id}/{filename}'


class Customer(models.Model):
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    display_name = models.CharField(max_length=125, blank=True, null=True)
    primary_phone = models.CharField(max_length=14, blank=False)
    secondary_phone = models.CharField(max_length=14, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    picture = models.ImageField(
        upload_to=customer_directory_path,
        blank=True,
        null=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='customer',
        on_delete=models.CASCADE,
        blank=False
    )

    class Meta:
        verbose_name = 'customer'
        verbose_name_plural = 'customers'


    def save(self, *args, **kwargs):
        self.full_clean()
        super(Customer, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = f'{self.first_name} {self.last_name}'
        super(Customer, self).clean(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.picture.delete(save=False)
        super(Customer, self).delete(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.display_name}'


class Vendor(models.Model):
    company = models.ForeignKey(
        'services.Company',
        related_name='members',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    career = models.ForeignKey(
        'services.Career',
        null=True,
        blank=True,
        related_name='vendors',
        on_delete=models.SET_NULL
    )
    customer = models.OneToOneField(
        'services.Customer',
        blank=True,
        null=True,
        related_name='vendor_info',
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name = 'vendor information'
        verbose_name_plural = 'vendors information'


class Career(models.Model):
    industry = models.CharField(max_length=50, unique=True)
    trade_name = models.CharField(max_length=100, unique=True)
    institution = models.ForeignKey(
        'services.Institution',
        null=True,
        blank=True,
        related_name='careers',
        on_delete=models.SET_NULL,
    )


class Institution(models.Model):
    short_name = models.CharField(max_length=15, unique=True, blank=False)
    long_name = models.CharField(max_length=150, unique=True, blank=False)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    slug = models.SlugField(max_length=50, unique=True, blank=True, editable=False)
    description = models.CharField(max_length=255, unique=True, blank=False)
    career = models.OneToOneField(
        'services.Career',
        related_name='categorical_name',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


    def save(self, *args, **kwargs):
        self.full_clean()
        super(Category, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).clean(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Job(models.Model):
    job_title = models.CharField(max_length=50, blank=False)
    category = models.ForeignKey(
        'services.Category',
        related_name='jobs',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )


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
    owner = models.OneToOneField(
        'services.Customer',
        related_name='national_id',
        on_delete=models.CASCADE
    )

    def __str__(self):
        if self.id_type == 0:
            return f'{self.id_number[:3]}-{self.id_number[3:10]}-{self.id_number[-1:]}'
        elif self.id_type == 1:
            return f'{self.id_number}'
        elif self.id_type == 2:
            return f'{self.id_number[:3]}-{self.id_number[3:5]}-{self.id_number[-4:]}'


class Address(models.Model):
    full_name = models.CharField(max_length=100, blank=False)
    state_province_region = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    sector = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=200, default='Dominican Republic')
    address_line_one = models.CharField(max_length=150, blank=False)
    address_line_two = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=14, blank=False)
    is_primary = models.BooleanField(default=False, editable=False)
    latlng = JSONField(blank=True, editable=False, null=True) # psql version
    formatted_name = models.CharField(max_length=500, blank=True, editable=False)
    owner = models.ForeignKey(
        'services.Customer',
        related_name='adresses',
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Address, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.formatted_name = ', '.join((
            f'{self.address_line_one}',
            f'{self.sector}',
            f'{self.city}',
            f'{self.state_province_region}',
            f'{self.country}'
        ))
        super(Address, self).clean(*args, **kwargs)

    def __str__(self):
        return f'{self.owner.display_name}: address_{self.id}'


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
        'services.Customer',
        related_name='creator_of',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'company'
        verbose_name_plural = 'companies'
        unique_together = (
            ('rnc', 'name')
        )

    def delete(self, *args, **kwargs):
        self.logo.delete(save=False)
        super(Company, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Company, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Company, self).clean(*args, **kwargs)
