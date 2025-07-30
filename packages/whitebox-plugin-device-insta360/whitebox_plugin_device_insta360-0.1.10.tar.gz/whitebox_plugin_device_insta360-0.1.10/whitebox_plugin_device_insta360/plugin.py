from plugin.utils import Plugin


class WhiteboxPluginDeviceInsta360(Plugin):
    """
    A plugin that enables support for Insta360 cameras.

    Attributes:
        name: The name of the plugin.
    """

    name = "Insta360 Camera Support"

    def get_device_classes(self) -> list:
        # Defer loading of device classes to allow for `device-manager` to first
        # register its base classes into the class registry, as base classes
        # cannot proxied
        from whitebox_plugin_device_insta360.devices import (
            Insta360X3,
            Insta360X4,
        )

        return [Insta360X3, Insta360X4]


plugin_class = WhiteboxPluginDeviceInsta360
