from django.apps import AppConfig

class GrievanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'grievance'

    def ready(self):
        import grievance.signals  # This ensures signals are loaded