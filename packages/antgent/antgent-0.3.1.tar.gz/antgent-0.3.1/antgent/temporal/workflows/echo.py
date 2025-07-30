from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from antgent.temporal.activities import AnyData, aecho, echo


@workflow.defn
class EchoWorkflow:
    def __init__(self) -> None:
        self.model: None | AnyData = None

    @workflow.run
    async def run(self, model: AnyData) -> AnyData:
        workflow.logger.info("Workflow start Echo")
        self.model = await workflow.start_activity(
            echo, model, start_to_close_timeout=timedelta(seconds=10), schedule_to_close_timeout=timedelta(seconds=10)
        )
        return self.model

    @workflow.query
    def echo(self) -> AnyData | None:
        return self.model


@workflow.defn
class EchoAsyncWorkflow:
    def __init__(self) -> None:
        self.model: None | dict[str, Any] = None

    @workflow.run
    async def run(self, model: dict[str, Any]) -> dict[str, Any]:
        workflow.logger.info("Workflow start Echo")
        self.model = await workflow.start_activity(
            aecho, model, start_to_close_timeout=timedelta(seconds=10), schedule_to_close_timeout=timedelta(seconds=10)
        )
        return self.model

    @workflow.query
    def echo(self) -> dict[str, Any] | None:
        return self.model
