import pytest

from NL2SQLEvaluator.orchestrator import orchestrator_entrypoint
from NL2SQLEvaluator.task_definition import MultipleTasks, SingleTask, SQLTask, Metrics


class TestPipeline:
    @pytest.fixture
    def multiple_tasks(self) -> MultipleTasks:
        task = SingleTask(
            relative_base_path='data/bird/bird_train/train_databases/address/address.sqlite',
            target_sql = SQLTask(query="SELECT COUNT(*) FROM Airlines", executed=None),
            predicted_sql = SQLTask(query="SELECT COUNT(*) FROM Airlines", executed=None),
            metrics_to_calculate=[Metrics("execution_accuracy")],
        )
        return MultipleTasks(
            tasks=[task] * 5,
            batch_size = 2
        )

    def test_orchestrator(self, multiple_tasks: MultipleTasks):
        result = orchestrator_entrypoint.invoke(multiple_tasks)
        print("done")
        assert result