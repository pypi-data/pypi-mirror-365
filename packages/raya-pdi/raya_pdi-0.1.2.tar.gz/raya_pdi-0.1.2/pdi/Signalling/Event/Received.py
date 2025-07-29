from pdi.Signalling.Event.AbstractEvent import Event


class Received(Event):
    def __init__(self, command: str):
        self.command = command

    @classmethod
    def getName(cls) -> str:
        return 'command:received'
