from pdi.Signalling.Event.AbstractEvent import Event


class DispatcherSpeak(Event):
    @classmethod
    def getName(cls) -> str:
        return 'dispatcher.speak'


class DispatcherUnSpeak(Event):
    @classmethod
    def getName(cls) -> str:
        return 'dispatcher.un-speak'
