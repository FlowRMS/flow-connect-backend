from uuid import UUID

import strawberry
from aioinject import Injected
from commons.auth import AuthInfo

from app.graphql.inject import inject
from app.workers.broker import execute_pending_document_task
from app.workers.document_execution.executor_service import (
    DocumentExecutorService,
    EntityProcessResponse,
)


@strawberry.type
class ExecuteWorkflowResponse:
    success: bool
    task_id: str
    message: str


@strawberry.type
class DocumentsMutations:
    @strawberry.mutation
    @inject
    async def execute_document_workflow(
        self,
        pending_document_id: UUID,
        auth_info: Injected[AuthInfo],
    ) -> ExecuteWorkflowResponse:
        """
        Execute the workflow to create domain entities from an approved PendingDocument.

        This kicks off a background TaskIQ task that:
        1. Fetches the PendingDocument and its confirmed PendingEntities
        2. Parses the extracted DTOs from extracted_data_json
        3. Converts DTOs to Strawberry inputs using confirmed entity mappings
        4. Creates the domain entities (Order, Quote, etc.) via services
        """
        task = await execute_pending_document_task.kiq(
            pending_document_id=pending_document_id,
            auth_info=auth_info.model_dump(),
        )

        return ExecuteWorkflowResponse(
            success=True,
            task_id=str(task.task_id),
            message=f"Workflow execution started for document {pending_document_id}",
        )

    @strawberry.mutation
    @inject
    async def execute_workflow_no_worker(
        self,
        pending_document_id: UUID,
        document_service: Injected[DocumentExecutorService],
    ) -> list[EntityProcessResponse]:
        return await document_service.execute(pending_document_id)
