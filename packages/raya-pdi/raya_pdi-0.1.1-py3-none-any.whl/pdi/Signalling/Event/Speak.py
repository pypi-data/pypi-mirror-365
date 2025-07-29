from pdi.Signalling.Event.AbstractEvent import Event


class Speak(Event):
    def __init__(self, text: str):
        self.text = text

    @classmethod
    def getName(cls) -> str:
        return 'speak:speak'


class StartSpeaking(Event):
    @classmethod
    def getName(cls) -> str:
        return 'speak:start'


class StopSpeaking(Event):
    @classmethod
    def getName(cls) -> str:
        return 'speak:stop'
