from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ServicesConfig(AppConfig):
    name = 'services'
    verbose_name = _('services')
    
    def ready(self):
        import services.signals
        super(ServicesConfig, self).ready()
