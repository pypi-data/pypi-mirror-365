from typing import Iterable
from pickle import dumps, loads

from redis import Redis
from eric_sse.exception import NoMessagesException, RepositoryError
from eric_sse.message import MessageContract
from eric_sse.queue import Queue
from eric_sse.connection import Connection, ConnectionRepositoryInterface

_PREFIX = 'eric-redis-queues'
_PREFIX_QUEUES = f'eric-redis-queues:q'
_PREFIX_LISTENERS = f'eric-redis-queues:l'
_PREFIX_CHANNELS = f'eric-redis-queues:c'
"""
import importlib
module = importlib.import_module('my_package.my_module')
my_class = getattr(module, 'MyClass')
my_instance = my_class()
"""
class RedisQueue(Queue):

    def __init__(self, listener_id: str, host='127.0.0.1', port=6379, db=0):
        self.id = listener_id
        self.__client = Redis(host=host, port=port, db=db)


    def pop(self) -> MessageContract:

        if not self.__client.exists(f'{_PREFIX_QUEUES}:{self.id}'):
            raise NoMessagesException

        try:
            raw_value = self.__client.lpop(f'{_PREFIX_QUEUES}:{self.id}')
            return loads(raw_value)

        except Exception as e:
            raise RepositoryError(e)


    def push(self, msg: MessageContract) -> None:
        try:
            self.__client.rpush(f'{_PREFIX_QUEUES}:{self.id}', dumps(msg))
        except Exception as e:
            raise RepositoryError(e)

class RedisConnectionsRepository(ConnectionRepositoryInterface):
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.__host: str = host
        self.__port: int = port
        self.__db: int = db
        self.__client = Redis(host=host, port=port, db=db)

    def create_queue(self, listener_id: str) -> Queue:
        return RedisQueue(listener_id= listener_id, host=self.__host, port=self.__port, db=self.__db)


    def load(self) -> Iterable[Connection]:
        for redis_key in self.__client.scan_iter(f"{_PREFIX_LISTENERS}:*"):
            key = redis_key.decode()
            try:
                listener = loads(self.__client.get(key))
                queue = self.create_queue(listener_id=listener.id)
                yield Connection(listener=listener, queue=queue)
            except Exception as e:
                raise RepositoryError(e)


    def persist(self, connection: Connection) -> None:
        try:
            self.__client.set(f'{_PREFIX_LISTENERS}:{connection.listener.id}', dumps(connection.listener))
        except Exception as e:
            raise RepositoryError(e)

    def delete(self, listener_id: str):
        try:
            self.__client.delete(f'{_PREFIX_LISTENERS}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)
        try:
            self.__client.delete(f'{_PREFIX_QUEUES}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)

