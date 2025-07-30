from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class DBExecutorEnum(Enum):
    sqlite = "sqlite"


class Metrics(Enum):
    """Enum for different metrics used in evaluation."""
    EXECUTION_ACCURACY = "execution_accuracy"
    F1_SCORE = "f1_score"
    CELL_PRECISION = "cell_precision"
    CELL_RECALL = "cell_recall"
    TUPLE_CARDINALITY = "tuple_cardinality"
    TUPLE_CONSTRAINT = "tuple_constraint"
    TUPLE_ORDER = "tuple_order"


class SQLTask(BaseModel):
    query: str | None = None
    executed: list[tuple] | None = None


class SingleTask(BaseModel):
    relative_base_path: str
    target_sql: SQLTask
    predicted_sql: SQLTask | None = None
    metrics_to_calculate: list[Metrics]
    executed_metrics: dict[Metrics, float] | None = None
    engine: Any | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class MultipleTasks(BaseModel):
    tasks: list[SingleTask]
    batch_size: int = 50


if __name__ == "__main__":
    print(DBExecutorEnum.sqlite)
