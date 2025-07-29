from pdi.Signalling.Event.AbstractEvent import Event


class InputActive(Event):
    @classmethod
    def getName(cls) -> str:
        return 'input:active'


class InputNotActive(Event):
    @classmethod
    def getName(cls) -> str:
        return 'input:not-active'


class InputVolume(Event):
    def __init__(self, volume: float):
        self.volume = volume

    @classmethod
    def getName(cls) -> str:
        return 'input:volume'
