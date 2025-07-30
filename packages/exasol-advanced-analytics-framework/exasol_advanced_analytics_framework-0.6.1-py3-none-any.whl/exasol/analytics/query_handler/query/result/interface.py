from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Iterator,
    List,
    Tuple,
    Union,
)

from exasol.analytics.schema.column import Column

Row = Tuple[Any, ...]


class QueryResult(ABC):

    @abstractmethod
    def __getattr__(self, name: str) -> Any:
        pass

    @abstractmethod
    def __getitem__(self, item: Any) -> Any:
        pass

    @abstractmethod
    def next(self) -> bool:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Row]:
        pass

    @abstractmethod
    def __next__(self) -> Row:
        pass

    @abstractmethod
    def rowcount(self) -> int:
        pass

    @abstractmethod
    def fetch_as_dataframe(self, num_rows: Union[str, int], start_col: int = 0):
        pass

    @abstractmethod
    def columns(self) -> List[Column]:
        pass

    @abstractmethod
    def column_names(self) -> List[str]:
        pass
