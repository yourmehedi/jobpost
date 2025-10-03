from .models import FeatureToggle

def is_feature_enabled(key):
    try:
        feature = FeatureToggle.objects.get(key=key)
        return feature.enabled
    except FeatureToggle.DoesNotExist:
        return False   
