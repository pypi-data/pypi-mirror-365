import json
from typing import Any, Dict, Optional, cast, Union
from typing_extensions import override
from masterpiece import MasterPiece


class Abstr(MasterPiece):
    """Base class for the Abstract Universe Project

    """

    def __init__(self, name: str = "") -> None:
        """Constructs new abstr object with the given bistring

        Args:
            name (str): bistring
        """
        super().__init__(name)

    @override
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        attributes = ["a"]
        for attr in attributes:
            if getattr(self, attr) != getattr(type(self), attr):
                data["_base"][attr] = getattr(self, attr)
        return data

    @override
    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        for key, value in data["_base"].items():
            setattr(self, key, value)

    @override
    def run(self) -> None:
        """Start a new thread to run in the background.
        """
        super().run()

