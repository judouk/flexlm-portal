from abc import ABC, abstractmethod

class ContentBackend(ABC):
    @abstractmethod
    def record_file(
        self,
        source_path: str,
        target_path: str,
        message: str,
    ):
        pass

    @abstractmethod
    def publish(self):
        pass
