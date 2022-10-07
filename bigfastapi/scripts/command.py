from abc import abstractmethod


class Command:
    @abstractmethod
    def run(self, args: list = None):
        pass
