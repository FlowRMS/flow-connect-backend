from commons.db.v6.rbac.rbac_privilege_type_enum import RbacPrivilegeTypeEnum
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy

from app.core.context_wrapper import ContextWrapper
from app.graphql.campaigns.repositories.campaigns_repository import CampaignsRepository
from app.graphql.common.landing_repository_protocol import LandingRepositoryProtocol
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.paginated_landing_page import PaginatedLandingPageInterface
from app.graphql.companies.repositories.companies_repository import CompaniesRepository
from app.graphql.contacts.repositories.contacts_repository import ContactsRepository
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.notes.repositories.notes_repository import NotesRepository
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository
from app.graphql.tasks.repositories.tasks_repository import TasksRepository
from app.graphql.v2.core.customers.repositories.customers_repository import (
    CustomersRepository,
)
from app.graphql.v2.core.factories.repositories.factories_repository import (
    FactoriesRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.files.repositories.file_repository import FileRepository
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService


class LandingPageService:
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        jobs_repository: JobsRepository,
        companies_repository: CompaniesRepository,
        contacts_repository: ContactsRepository,
        pre_opportunities_repository: PreOpportunitiesRepository,
        tasks_repository: TasksRepository,
        notes_repository: NotesRepository,
        campaigns_repository: CampaignsRepository,
        customers_repository: CustomersRepository,
        factories_repository: FactoriesRepository,
        products_repository: ProductsRepository,
        quotes_repository: QuotesRepository,
        file_repository: FileRepository,
        rbac_filter_service: RbacFilterService,
    ) -> None:
        super().__init__()
        self._context_wrapper = context_wrapper
        self._rbac_filter_service = rbac_filter_service
        self._repository_map: dict[LandingSourceType, LandingRepositoryProtocol] = {
            LandingSourceType.JOBS: jobs_repository,
            LandingSourceType.COMPANIES: companies_repository,
            LandingSourceType.CONTACTS: contacts_repository,
            LandingSourceType.PRE_OPPORTUNITIES: pre_opportunities_repository,
            LandingSourceType.TASKS: tasks_repository,
            LandingSourceType.NOTES: notes_repository,
            LandingSourceType.CAMPAIGNS: campaigns_repository,
            LandingSourceType.CUSTOMERS: customers_repository,
            LandingSourceType.FACTORIES: factories_repository,
            LandingSourceType.PRODUCTS: products_repository,
            LandingSourceType.QUOTES: quotes_repository,
            LandingSourceType.FILES: file_repository,
        }

    async def find_landing_pages(
        self,
        source_type: LandingSourceType,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> PaginatedLandingPageInterface:
        repository = self._repository_map.get(source_type)

        if repository is None:
            raise NotImplementedError(
                f"{source_type.value.title()} landing page not yet implemented"
            )

        user_id = None
        rbac_option = None

        if repository.rbac_resource is not None:
            auth_info = self._context_wrapper.get().auth_info
            user_id = auth_info.flow_user_id
            rbac_option = await self._rbac_filter_service.get_privilege_option(
                roles=auth_info.roles,
                resource=repository.rbac_resource,
                privilege=RbacPrivilegeTypeEnum.VIEW,
            )

        return await PaginatedLandingPageInterface.get_pagination_window(
            session=repository.session,
            stmt=repository.paginated_stmt(),
            record_type=repository.model_class,
            record_type_gql=repository.landing_model,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            rbac_option=rbac_option,
            user_id=user_id,
        )
