"""Internal event bus for decoupled cross-layer communication."""

from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

EventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class EventBus:
    """Simple synchronous in-process event bus.

    Layers publish events (e.g., "exam_completed") and other layers
    subscribe to react (e.g., update level progress). No Kafka needed
    for a modular monolith.
    """

    _handlers: dict[str, list[EventHandler]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: str, handler: EventHandler) -> None:
        cls._handlers[event_type].append(handler)

    @classmethod
    async def publish(cls, event_type: str, payload: dict[str, Any]) -> None:
        for handler in cls._handlers[event_type]:
            await handler(payload)

    @classmethod
    def clear(cls) -> None:
        """Clear all handlers (useful for testing)."""
        cls._handlers.clear()
