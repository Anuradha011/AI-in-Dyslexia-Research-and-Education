from django.contrib import admin
from .models import (AIModelConfig, RiskScoringConfig, NLPSystemConfig,
                     CompliancePolicy, BiasMonitoringReport, SupportedLanguage)

admin.site.register(AIModelConfig)
admin.site.register(RiskScoringConfig)
admin.site.register(NLPSystemConfig)
admin.site.register(CompliancePolicy)
admin.site.register(BiasMonitoringReport)
admin.site.register(SupportedLanguage)