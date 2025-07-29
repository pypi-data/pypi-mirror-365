from pdi.Signalling.Event.AbstractEvent import Event


class ServerConnected(Event):
    @classmethod
    def getName(cls) -> str:
        return 'server:connected'


class ServerDisconnected(Event):
    @classmethod
    def getName(cls) -> str:
        return 'server:disconnected'
