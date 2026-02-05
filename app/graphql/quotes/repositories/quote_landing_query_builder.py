from typing import Any

from commons.db.v6 import User
from commons.db.v6.core import Customer, Factory, Product
from commons.db.v6.core.products import ProductCategory
from commons.db.v6.crm.quotes import (
    Quote,
    QuoteBalance,
    QuoteDetail,
    QuoteSplitRate,
)
from sqlalchemy import Select, String, cast, func, select, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, array_agg
from sqlalchemy.orm import aliased, lazyload
from sqlalchemy.sql.selectable import Subquery


class QuoteLandingQueryBuilder:
    def _sales_reps_subquery(self) -> Subquery[Any]:
        sales_rep = aliased(User)
        per_user_agg = (
            select(
                QuoteDetail.quote_id,
                sales_rep.full_name.label("full_name"),
                func.sum(QuoteDetail.total).label("total"),
                func.avg(QuoteSplitRate.split_rate).label("avg_split_rate"),
            )
            .select_from(QuoteDetail)
            .join(QuoteSplitRate, QuoteSplitRate.quote_detail_id == QuoteDetail.id)
            .join(sales_rep, sales_rep.id == QuoteSplitRate.user_id)
            .group_by(QuoteDetail.quote_id, sales_rep.id, sales_rep.full_name)
        ).subquery()

        return (
            select(
                per_user_agg.c.quote_id,
                func.jsonb_agg(
                    func.jsonb_build_object(
                        text("'full_name'"),
                        per_user_agg.c.full_name,
                        text("'total'"),
                        per_user_agg.c.total,
                        text("'avg_split_rate'"),
                        per_user_agg.c.avg_split_rate,
                    )
                ).label("sales_reps"),
            )
            .select_from(per_user_agg)
            .group_by(per_user_agg.c.quote_id)
        ).subquery()

    def build(self) -> Select[Any]:
        sold_to = aliased(Customer)
        end_user = aliased(Customer)

        empty_str_array = cast(text("ARRAY[]::text[]"), ARRAY(String))

        end_users_agg = func.coalesce(
            array_agg(end_user.company_name.distinct()).filter(
                end_user.company_name.isnot(None)
            ),
            empty_str_array,
        ).label("end_users")

        factories_agg = func.coalesce(
            array_agg(Factory.title.distinct()).filter(Factory.title.isnot(None)),
            empty_str_array,
        ).label("factories")

        categories_agg = func.coalesce(
            array_agg(ProductCategory.title.distinct()).filter(
                ProductCategory.title.isnot(None)
            ),
            empty_str_array,
        ).label("categories")

        part_numbers_agg = func.coalesce(
            array_agg(
                func.coalesce(
                    Product.factory_part_number, QuoteDetail.product_name_adhoc
                ).distinct()
            ).filter(
                func.coalesce(
                    Product.factory_part_number, QuoteDetail.product_name_adhoc
                ).isnot(None)
            ),
            empty_str_array,
        ).label("part_numbers")

        sales_reps_subq = self._sales_reps_subquery()
        sales_reps_agg = func.coalesce(
            sales_reps_subq.c.sales_reps,
            cast(text("'[]'"), JSONB),
        ).label("sales_reps")

        return (
            select(
                Quote.id,
                Quote.created_at,
                User.full_name.label("created_by"),
                Quote.quote_number,
                Quote.status,
                Quote.pipeline_stage,
                Quote.entity_date,
                Quote.exp_date,
                QuoteBalance.total.label("total"),
                QuoteBalance.commission.label("commission"),
                Quote.published,
                Quote.user_ids,
                sold_to.company_name.label("sold_to_customer_name"),
                end_users_agg,
                factories_agg,
                categories_agg,
                part_numbers_agg,
                sales_reps_agg,
            )
            .select_from(Quote)
            .options(lazyload("*"))
            .join(User, User.id == Quote.created_by_id)
            .join(QuoteBalance, QuoteBalance.id == Quote.balance_id)
            .outerjoin(sold_to, sold_to.id == Quote.sold_to_customer_id)
            .outerjoin(QuoteDetail, QuoteDetail.quote_id == Quote.id)
            .outerjoin(end_user, end_user.id == QuoteDetail.end_user_id)
            .outerjoin(Factory, Factory.id == QuoteDetail.factory_id)
            .outerjoin(Product, Product.id == QuoteDetail.product_id)
            .outerjoin(
                ProductCategory, ProductCategory.id == Product.product_category_id
            )
            .outerjoin(sales_reps_subq, sales_reps_subq.c.quote_id == Quote.id)
            .group_by(
                Quote.id,
                Quote.created_at,
                User.first_name,
                User.last_name,
                Quote.quote_number,
                Quote.status,
                Quote.pipeline_stage,
                Quote.entity_date,
                Quote.exp_date,
                QuoteBalance.total,
                QuoteBalance.commission,
                Quote.published,
                Quote.user_ids,
                sold_to.company_name,
                sales_reps_subq.c.sales_reps,
            )
        )
