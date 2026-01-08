from uuid import UUID

import strawberry
from aioinject import Injected
from commons.auth import AuthInfo
from commons.db.v6.enums import WorkflowStatus

from app.graphql.documents.repositories.pending_document_repository import (
    PendingDocumentRepository,
)
from app.graphql.documents.services.pending_document_processing_service import (
    PendingDocumentProcessingService,
)
from app.graphql.documents.strawberry.pending_document_processing_input import (
    PendingDocumentProcessingInput,
)
from app.graphql.documents.strawberry.pending_document_processing_type import (
    PendingDocumentProcessingType,
)
from app.graphql.inject import inject
from app.workers.broker import (
    execute_pending_document_task,
    pending_document_status_email_task,
)
from app.workers.document_execution.executor_service import DocumentExecutorService
from app.workers.tasks.pending_document_status_task import PendingDocumentStatusItem


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
        pending_document_repository: Injected[PendingDocumentRepository],
    ) -> ExecuteWorkflowResponse:
        """
        Execute the workflow to create domain entities from an approved PendingDocument.

        This kicks off a background TaskIQ task that:
        1. Fetches the PendingDocument and its confirmed PendingEntities
        2. Parses the extracted DTOs from extracted_data_json
        3. Converts DTOs to Strawberry inputs using confirmed entity mappings
        4. Creates the domain entities (Order, Quote, etc.) via services
        """
        pending_document = await pending_document_repository.get_by_id(
            pending_document_id
        )
        pending_document.workflow_status = WorkflowStatus.IN_PROGRESS
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
    ) -> list[PendingDocumentProcessingType]:
        results = await document_service.execute(pending_document_id)
        return [PendingDocumentProcessingType.from_model(r) for r in results]

    @strawberry.mutation
    @inject
    async def update_pending_document_processing(
        self,
        id: UUID,
        input: PendingDocumentProcessingInput,
        service: Injected[PendingDocumentProcessingService],
    ) -> PendingDocumentProcessingType:
        processing = await service.update(id, input)
        return PendingDocumentProcessingType.from_model(processing)

    @strawberry.mutation
    @inject
    async def delete_pending_document_processing(
        self,
        id: UUID,
        service: Injected[PendingDocumentProcessingService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def send_pending_document_status_email(
        self,
        pending_document_id: UUID,
        auth_info: Injected[AuthInfo],
        pending_document_repository: Injected[PendingDocumentRepository],
    ) -> ExecuteWorkflowResponse:
        pending_document = await pending_document_repository.get_by_id(
            pending_document_id
        )
        if not pending_document:
            return ExecuteWorkflowResponse(
                success=False,
                task_id="",
                message=f"Pending document {pending_document_id} not found",
            )

        item = PendingDocumentStatusItem(
            pending_document_id=str(pending_document_id),
            tenant=auth_info.tenant_name,
            user_id=str(auth_info.flow_user_id),
        )
        task = await pending_document_status_email_task.kiq(item)

        return ExecuteWorkflowResponse(
            success=True,
            task_id=str(task.task_id),
            message="Status email task queued. You will receive an email when processing completes.",
        )
