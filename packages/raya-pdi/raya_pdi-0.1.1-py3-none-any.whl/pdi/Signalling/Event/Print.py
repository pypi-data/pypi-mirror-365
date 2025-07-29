from pdi.Signalling.Event.AbstractEvent import Event


class Print(Event):
    def __init__(self, text: str):
        self.text = text

    @classmethod
    def getName(cls) -> str:
        return 'print'
