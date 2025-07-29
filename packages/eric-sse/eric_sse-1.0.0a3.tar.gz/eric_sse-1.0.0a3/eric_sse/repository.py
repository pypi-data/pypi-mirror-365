from abc import ABC, abstractmethod
from typing import AsyncIterable, Tuple

from eric_sse.listener import MessageQueueListener
from eric_sse.queue import Queue, InMemoryQueue


class AbstractMessageQueueRepository(ABC):
    """
    Abstraction for queues creation

    see :class:`eric_sse.entities.AbstractChannel`
    """
    @abstractmethod
    def create(self) -> Queue:
        ...

    @abstractmethod
    def persist(self, listener: MessageQueueListener, queue: Queue) -> None:
        ...

    @abstractmethod
    def load(self) -> AsyncIterable[Tuple[MessageQueueListener, Queue]]:
        """
        Returns a list of persisted listeners and a dictionary of queues indexed by the ids of those listeners
        """
        ...

    @abstractmethod
    def delete(self, listener_id: str) -> None:
        ...


class InMemoryMessageQueueRepository(AbstractMessageQueueRepository):
    """
    Default implementation used by :class:`eric_sse.entities.AbstractChannel`
    """
    def create(self) -> Queue:
        return InMemoryQueue()

    def persist(self, listeners: list[MessageQueueListener], queues: dict[str, Queue]) -> None:
        pass

    def load(self) ->  AsyncIterable[Tuple[MessageQueueListener, Queue]]:
        pass

    def delete(self, listener_id: str) -> None:
        pass
