from abc import ABC, abstractmethod


class Service(ABC):

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError
