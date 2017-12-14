from django.apps import AppConfig

#必须写的内容，是Django启动的时候会自动加载
class StarkConfig(AppConfig):
    name = 'stark'
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('stark')
