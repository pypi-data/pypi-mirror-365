from abc import ABC, abstractmethod

class SentimentAnalyzer(ABC):
    @abstractmethod
    def get_score_string(self, text: str) -> float:
        """Return sentiment score from -1 to 1."""
        pass

    @abstractmethod
    def get_label_string(self, text: str) -> str:
        """Return sentiment label: 'positive', 'neutral', or 'negative'."""
        pass

    @abstractmethod
    def get_score_list_dict(slef, content: list[dict]) -> list[dict]:
        "sentiment score"
        pass


    @abstractmethod
    def get_label_list_dict(slef, content: list[dict]) -> list[dict]:
        "sentiment score"
        pass
