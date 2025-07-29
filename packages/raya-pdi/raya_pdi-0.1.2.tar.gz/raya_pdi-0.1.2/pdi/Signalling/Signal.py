from event_dispatcher import SyncEventDispatcher, BaseEventDispatcher

from pdi.Signalling.Event.AbstractEvent import Event


class Signal:
    _dispatcher: BaseEventDispatcher

    @classmethod
    def bind(cls, eventName: str, handler: callable):
        if not hasattr(cls, '_dispatcher'):
            cls._dispatcher = SyncEventDispatcher()

        cls._dispatcher.subscribe(eventName, handler)

    @classmethod
    def publish(cls, event: Event):
        cls._dispatcher.dispatch(event.getName(), event)
