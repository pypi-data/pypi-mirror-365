from pdi.Signalling.Event.AbstractEvent import Event


class ExecuteCommand(Event):
    def __init__(self, code: str):
        self.code = code

    @classmethod
    def getName(cls) -> str:
        return 'execute:command'
