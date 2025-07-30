from abc import ABC, abstractmethod

class ArticleFetcher(ABC):
    @abstractmethod
    def company_and_article_list(self, sample_size: int = 50) -> list[dict]:
        """returns list of dictionaries"""
        pass