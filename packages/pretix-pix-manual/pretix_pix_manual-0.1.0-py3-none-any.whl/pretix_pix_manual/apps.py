from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_pix_manual"
    verbose_name = "Brazilian Pix - Manual processing"

    class PretixPluginMeta:
        name = gettext_lazy("Brazilian Pix - Manual processing")
        author = "Renne Rocha"
        description = gettext_lazy("Brazilian Pix - Manual processing")
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA
