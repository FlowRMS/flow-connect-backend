from datetime import date
from decimal import Decimal

from commons.db.v6.common.creation_type import CreationType
from commons.db.v6.crm.pre_opportunities.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.quotes import (
    PipelineStage,
    Quote,
    QuoteDetail,
    QuoteDetailStatus,
    QuoteInsideRep,
    QuoteSplitRate,
    QuoteStatus,
)


class QuoteFactory:
    @staticmethod
    def from_pre_opportunity(
        pre_opportunity: PreOpportunity,
        quote_number: str,
    ) -> Quote:
        return Quote(
            factory_per_line_item=False,
            inside_per_line_item=True,
            outside_per_line_item=True,
            end_user_per_line_item=False,
            quote_number=quote_number,
            entity_date=date.today(),
            sold_to_customer_id=pre_opportunity.sold_to_customer_id,
            bill_to_customer_id=pre_opportunity.bill_to_customer_id,
            payment_terms=pre_opportunity.payment_terms,
            customer_ref=pre_opportunity.customer_ref,
            freight_terms=pre_opportunity.freight_terms,
            exp_date=pre_opportunity.exp_date,
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROSPECT,
            creation_type=CreationType.API,
            published=False,
            blanket=False,
            details=QuoteFactory._map_pre_opp_details(pre_opportunity.details),
        )

    @staticmethod
    def duplicate(source_quote: Quote, new_quote_number: str) -> Quote:
        return Quote(
            factory_per_line_item=source_quote.factory_per_line_item,
            inside_per_line_item=source_quote.inside_per_line_item,
            outside_per_line_item=source_quote.outside_per_line_item,
            end_user_per_line_item=source_quote.end_user_per_line_item,
            quote_number=new_quote_number,
            entity_date=date.today(),
            sold_to_customer_id=source_quote.sold_to_customer_id,
            bill_to_customer_id=source_quote.bill_to_customer_id,
            payment_terms=source_quote.payment_terms,
            customer_ref=source_quote.customer_ref,
            freight_terms=source_quote.freight_terms,
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROSPECT,
            creation_type=CreationType.DUPLICATION,
            duplicated_from=source_quote.id,
            blanket=source_quote.blanket,
            published=False,
            details=QuoteFactory._deep_copy_details(source_quote.details),
        )

    @staticmethod
    def _map_pre_opp_details(
        pre_opp_details: list[PreOpportunityDetail],
    ) -> list[QuoteDetail]:
        return [
            QuoteDetail(
                item_number=detail.item_number,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal,
                discount_rate=detail.discount_rate,
                discount=detail.discount,
                total=detail.total,
                product_id=detail.product_id,
                factory_id=detail.factory_id,
                end_user_id=detail.end_user_id,
                lead_time=detail.lead_time,
                status=QuoteDetailStatus.OPEN,
                commission_rate=Decimal("0"),
                commission=Decimal("0"),
                commission_discount_rate=Decimal("0"),
                commission_discount=Decimal("0"),
                total_line_commission=Decimal("0"),
            )
            for detail in pre_opp_details
        ]

    @staticmethod
    def _deep_copy_details(details: list[QuoteDetail]) -> list[QuoteDetail]:
        return [
            QuoteDetail(
                item_number=d.item_number,
                quantity=d.quantity,
                unit_price=d.unit_price,
                subtotal=d.subtotal,
                discount_rate=d.discount_rate,
                discount=d.discount,
                total=d.total,
                total_line_commission=d.total_line_commission,
                commission_rate=d.commission_rate,
                commission=d.commission,
                commission_discount_rate=d.commission_discount_rate,
                commission_discount=d.commission_discount,
                product_id=d.product_id,
                product_name_adhoc=d.product_name_adhoc,
                product_description_adhoc=d.product_description_adhoc,
                factory_id=d.factory_id,
                end_user_id=d.end_user_id,
                lead_time=d.lead_time,
                note=d.note,
                status=QuoteDetailStatus.OPEN,
                outside_split_rates=[
                    QuoteSplitRate(
                        user_id=sr.user_id,
                        split_rate=sr.split_rate,
                        position=sr.position,
                    )
                    for sr in d.outside_split_rates
                ],
                inside_split_rates=[
                    QuoteInsideRep(
                        user_id=ir.user_id,
                        split_rate=ir.split_rate,
                        position=ir.position,
                    )
                    for ir in d.inside_split_rates
                ],
            )
            for d in details
        ]
