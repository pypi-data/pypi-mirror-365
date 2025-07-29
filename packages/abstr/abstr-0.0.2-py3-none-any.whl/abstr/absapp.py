from masterpiece import Application

class AbsApp(Application):
    """Base class for applications.
    """

    def __init__(self, name: str) -> None:
        """Construct application with the given name.
        Args:
            name (str): name for the application
        """
        super().__init__(name)


    @classmethod
    def register(cls) -> None:
        """Register plugin group `juham`."""
        Application.register_plugin_group("abstr")
