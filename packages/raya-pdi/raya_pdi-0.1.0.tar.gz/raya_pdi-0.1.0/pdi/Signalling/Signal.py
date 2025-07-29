from event_dispatcher import SyncEventDispatcher, BaseEventDispatcher

from pdi.Signalling.Event.AbstractEvent import Event


class Signal:
    dispatcher: BaseEventDispatcher

    @classmethod
    def bind(cls, eventName: str, handler: callable):
        if not hasattr(cls, 'dispatcher'):
            cls.dispatcher = SyncEventDispatcher()

        cls.dispatcher.subscribe(eventName, handler)

    @classmethod
    def publish(cls, event: Event):
        cls.dispatcher.dispatch(event.getName(), event)
