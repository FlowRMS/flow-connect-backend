"""
Seed script for creating default PDF templates.

This script populates the database with system templates that serve as starting points
for users to create their own custom templates.

Usage:
    cd flow-py-crm1
    uv run python scripts/seed_pdf_templates.py [--env dev|staging|prod]
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config.base_settings import get_settings_local
from app.core.config.settings import Settings
from app.core.db.db_provider import create_multitenant_controller
from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate
from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


# Default template configurations
# Each template has a type code, name, description, and list of modules
DEFAULT_TEMPLATES = [
    {
        "name": "Quote Template",
        "template_type_code": "quote",
        "description": "Standard quote template with company header, customer info, line items, and pricing summary.",
        "global_styles": {
            "primaryColor": "#1E3A5F",
            "secondaryColor": "#4A5568",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True, "showAddress": True, "showContact": True}},
            {"module_type": "customer-info", "position": 1, "config": {"layout": "side-by-side", "showSoldTo": True, "showBillTo": False, "showShipTo": True}},
            {"module_type": "job-info", "position": 2, "config": {"showJobName": True, "showJobNumber": True, "showJobAddress": True}},
            {"module_type": "line-items-table", "position": 3, "config": {"showLineNumbers": True, "showQuantity": True, "showUnitPrice": True, "showExtendedPrice": True, "alternateRowColors": True}},
            {"module_type": "pricing-summary", "position": 4, "config": {"showSubtotal": True, "showTax": True, "showDiscount": False, "showTotal": True}},
            {"module_type": "notes-block", "position": 5, "config": {"notesSource": "record"}},
            {"module_type": "signature-block", "position": 6, "config": {"numberOfBlocks": 2, "layout": "horizontal"}},
        ],
    },
    {
        "name": "Sales Order Template",
        "template_type_code": "order",
        "description": "Sales order template with customer info, line items, and shipping details.",
        "global_styles": {
            "primaryColor": "#2563EB",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True, "showAddress": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True, "showPONumber": True}},
            {"module_type": "customer-info", "position": 2, "config": {"layout": "side-by-side", "showSoldTo": True, "showBillTo": True, "showShipTo": True}},
            {"module_type": "order-line-items", "position": 3, "config": {"showLineNumbers": True, "showQuantity": True, "showUnitPrice": True, "showExtendedPrice": True}},
            {"module_type": "pricing-summary", "position": 4, "config": {"showSubtotal": True, "showTax": True, "showTotal": True}},
            {"module_type": "shipping-details", "position": 5, "config": {"showCarrier": True, "showShipDate": True, "showFreightTerms": True}},
            {"module_type": "notes-block", "position": 6, "config": {"notesSource": "record"}},
        ],
    },
    {
        "name": "Invoice Template",
        "template_type_code": "invoice",
        "description": "Invoice template with billing info, line items, and payment details.",
        "global_styles": {
            "primaryColor": "#059669",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True, "showAddress": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True, "showPONumber": True}},
            {"module_type": "bill-to-info", "position": 2, "config": {}},
            {"module_type": "invoice-line-items", "position": 3, "config": {"showLineNumbers": True, "showQuantity": True, "showUnitPrice": True, "showExtendedPrice": True}},
            {"module_type": "amount-due-block", "position": 4, "config": {"showInvoiceTotal": True, "showPaymentsReceived": True, "showBalanceDue": True}},
            {"module_type": "payment-terms-block", "position": 5, "config": {"showDueDate": True, "showAcceptedPaymentMethods": True}},
            {"module_type": "notes-block", "position": 6, "config": {"notesSource": "record"}},
        ],
    },
    {
        "name": "Packing Slip Template",
        "template_type_code": "packing_slip",
        "description": "Packing slip for shipments - no pricing information shown.",
        "global_styles": {
            "primaryColor": "#7C3AED",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True}},
            {"module_type": "ship-to-info", "position": 2, "config": {"showDeliveryInstructions": True}},
            {"module_type": "fulfillment-line-items", "position": 3, "config": {"showLineNumbers": True, "showQuantity": True, "showPartNumber": True, "showDescription": True}},
            {"module_type": "package-summary", "position": 4, "config": {"showNumberOfPackages": True, "showTotalWeight": True}},
            {"module_type": "notes-block", "position": 5, "config": {"notesSource": "record"}},
        ],
    },
    {
        "name": "Pick List Template",
        "template_type_code": "pick_list",
        "description": "Warehouse pick list with bin locations and quantities.",
        "global_styles": {
            "primaryColor": "#DC2626",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "wave-information", "position": 1, "config": {"showWaveId": True, "showTotalPicks": True, "showAssignedPicker": True}},
            {"module_type": "ship-to-info", "position": 2, "config": {}},
            {"module_type": "pick-list-line-items", "position": 3, "config": {"showPickSequence": True, "showBinLocation": True, "showQuantity": True}},
            {"module_type": "signature-block", "position": 4, "config": {"numberOfBlocks": 1, "signatureBlocks": [{"signatureLine": True, "printedNameLine": True, "dateLine": True}]}},
        ],
    },
    {
        "name": "Shipping Label Template",
        "template_type_code": "shipping_label",
        "description": "Compact shipping label with address and tracking info.",
        "global_styles": {
            "primaryColor": "#000000",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 12,
            "headerFontSize": 16,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True, "showAddress": True}},
            {"module_type": "ship-to-info", "position": 1, "config": {"showDeliveryInstructions": False}},
            {"module_type": "shipping-details", "position": 2, "config": {"showCarrier": True, "showTrackingNumbers": True, "showServiceLevel": True}},
        ],
    },
    {
        "name": "Commission Check Stub Template",
        "template_type_code": "commission_check",
        "description": "Commission statement with breakdown and check amount.",
        "global_styles": {
            "primaryColor": "#0891B2",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "commission-statement-header", "position": 1, "config": {"showCommissionPeriod": True, "showRepName": True}},
            {"module_type": "commission-breakdown", "position": 2, "config": {}},
            {"module_type": "check-amount-block", "position": 3, "config": {"showGrossCommission": True, "showDeductions": True, "showNetAmount": True}},
        ],
    },
    {
        "name": "Credit Memo Template",
        "template_type_code": "credit_memo",
        "description": "Credit memo for returns and adjustments.",
        "global_styles": {
            "primaryColor": "#DC2626",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True}},
            {"module_type": "bill-to-info", "position": 2, "config": {}},
            {"module_type": "credit-line-items", "position": 3, "config": {"showQuantity": True, "showUnitPrice": True, "showCreditAmount": True}},
            {"module_type": "amount-due-block", "position": 4, "config": {"showCreditsApplied": True, "showBalanceDue": True}},
            {"module_type": "notes-block", "position": 5, "config": {"notesSource": "record"}},
        ],
    },
    {
        "name": "RMA Document Template",
        "template_type_code": "rma",
        "description": "Return Merchandise Authorization document.",
        "global_styles": {
            "primaryColor": "#EA580C",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True}},
            {"module_type": "return-shipping-info", "position": 2, "config": {"showRmaNumber": True, "showReturnInstructions": True}},
            {"module_type": "rma-line-items", "position": 3, "config": {"showReturnQty": True, "showReason": True, "showCondition": True}},
            {"module_type": "notes-block", "position": 4, "config": {"notesSource": "record"}},
            {"module_type": "acknowledgment-checkbox", "position": 5, "config": {"showSignatureLine": True}},
        ],
    },
    {
        "name": "Submittal Cover Sheet Template",
        "template_type_code": "submittal",
        "description": "Submittal transmittal cover sheet with stakeholders and items.",
        "global_styles": {
            "primaryColor": "#4F46E5",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "transmittal-header", "position": 1, "config": {"showProjectName": True, "showSubmittalNumber": True, "showSubmittalDate": True}},
            {"module_type": "job-stakeholders", "position": 2, "config": {"displayFormat": "table"}},
            {"module_type": "submittal-items-table", "position": 3, "config": {}},
            {"module_type": "approval-status-block", "position": 4, "config": {"showApprovalSignature": True}},
        ],
    },
    {
        "name": "Cycle Count Sheet Template",
        "template_type_code": "cycle_count",
        "description": "Inventory cycle count worksheet.",
        "global_styles": {
            "primaryColor": "#16A34A",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "inventory-location", "position": 1, "config": {"showWarehouseName": True, "showLocationPath": True}},
            {"module_type": "cycle-count-line-items", "position": 2, "config": {"showBinLocation": True, "showSystemQty": True, "showCountedQty": True, "showVariance": True}},
            {"module_type": "inspection-checklist", "position": 3, "config": {"showInspectorSignature": True}},
        ],
    },
    {
        "name": "Receiving Document Template",
        "template_type_code": "receiving",
        "description": "Receiving document for incoming shipments.",
        "global_styles": {
            "primaryColor": "#0D9488",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 10,
            "headerFontSize": 14,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True}},
            {"module_type": "receiving-summary", "position": 1, "config": {"showPoNumber": True, "showVendorName": True, "showExpectedDate": True, "showCarrier": True}},
            {"module_type": "fulfillment-line-items", "position": 2, "config": {"showPartNumber": True, "showDescription": True, "showExpectedQty": True, "showReceivedQty": True}},
            {"module_type": "inspection-checklist", "position": 3, "config": {"showExceptionNotesArea": True, "showInspectorSignature": True}},
        ],
    },
    {
        "name": "Bill of Lading Template",
        "template_type_code": "bol",
        "description": "Bill of Lading for freight shipments.",
        "global_styles": {
            "primaryColor": "#1E3A5F",
            "secondaryColor": "#4B5563",
            "fontFamily": "Helvetica",
            "bodyFontSize": 9,
            "headerFontSize": 12,
        },
        "modules": [
            {"module_type": "company-header", "position": 0, "config": {"logoPosition": "left", "showCompanyName": True, "showAddress": True}},
            {"module_type": "document-header", "position": 1, "config": {"showDocumentType": True, "showDocumentNumber": True, "showDocumentDate": True}},
            {"module_type": "customer-info", "position": 2, "config": {"layout": "side-by-side", "showSoldTo": True, "showShipTo": True}},
            {"module_type": "fulfillment-line-items", "position": 3, "config": {"showPartNumber": True, "showDescription": True, "showQuantity": True, "showWeight": True}},
            {"module_type": "freight-classification", "position": 4, "config": {"showFreightClass": True, "showNmfcCode": True, "showHazmatIndicators": True}},
            {"module_type": "shipping-details", "position": 5, "config": {"showCarrier": True, "showFreightTerms": True, "showNumberOfPackages": True}},
            {"module_type": "signature-block", "position": 6, "config": {"numberOfBlocks": 2, "layout": "horizontal", "signatureBlocks": [{"signatureLine": True, "printedNameLine": True, "titleLine": True}, {"signatureLine": True, "printedNameLine": True, "titleLine": True}]}},
        ],
    },
]


async def get_existing_templates(
    session: AsyncSession, template_type_code: str
) -> list[PdfTemplate]:
    """Check if system templates already exist for a given type."""
    stmt = select(PdfTemplate).where(
        PdfTemplate.template_type_code == template_type_code,
        PdfTemplate.is_system == True,
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def seed_templates(session: AsyncSession) -> dict[str, int]:
    """Seed the database with default templates."""
    from commons.db.models import User
    
    created_count = 0
    skipped_count = 0
    
    # Get first available user for created_by_id (required field)
    user_result = await session.execute(select(User).limit(1))
    user = user_result.scalar_one_or_none()
    
    if not user:
        logger.error("No users found in database. Please create a user first before seeding templates.")
        logger.info("You can create a user by running the application and signing up, or by running migrations.")
        return {"created": 0, "skipped": 0, "error": "No users found"}
    
    logger.info(f"Using user '{user.full_name or user.id}' for template creation")
    
    for template_config in DEFAULT_TEMPLATES:
        template_type_code = template_config["template_type_code"]
        
        # Check if system template already exists
        existing = await get_existing_templates(session, template_type_code)
        if existing:
            logger.info(f"Skipping {template_config['name']} - system template already exists")
            skipped_count += 1
            continue
        
        # Create the template
        template = PdfTemplate(
            name=template_config["name"],
            description=template_config.get("description"),
            template_type_code=template_type_code,
            template_type_id=None,  # Will be set if template types exist
            is_default=True,
            is_system=True,
            global_styles=template_config.get("global_styles", {}),
        )
        # Set created_by_id manually (required field)
        template.created_by_id = user.id
        
        session.add(template)
        await session.flush()
        
        # Create modules
        for module_config in template_config.get("modules", []):
            module = PdfTemplateModule(
                template_id=str(template.id),
                module_type=module_config["module_type"],
                position=module_config["position"],
                config=module_config.get("config", {}),
            )
            session.add(module)
        
        await session.flush()
        logger.info(f"Created system template: {template_config['name']}")
        created_count += 1
    
    return {"created": created_count, "skipped": skipped_count}


async def main(env: str = "dev") -> None:
    """Main entry point for the seed script."""
    logging.basicConfig(level=logging.INFO)
    
    # Load settings
    settings = get_settings_local(env=env, cls=Settings)
    
    # Create multi-tenant controller
    controller = await create_multitenant_controller(settings)
    
    # Try multi-tenant first
    tenant_list = list(controller.engines.keys())
    
    if tenant_list:
        # Use the first available tenant
        tenant = tenant_list[0]
        logger.info(f"Using tenant: {tenant}")
        
        async with controller.scoped_session(tenant) as session:
            async with session.begin():
                result = await seed_templates(session)
                logger.info(f"Seeding complete. Created: {result['created']}, Skipped: {result['skipped']}")
    else:
        # Fallback to direct connection for dev environments without multi-tenancy
        logger.info("No tenants found. Using direct database connection.")
        
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        # Create direct connection
        engine = create_async_engine(
            settings.pg_url.unicode_string(),
            echo=settings.log_level == "DEBUG",
        )
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            async with session.begin():
                result = await seed_templates(session)
                logger.info(f"Seeding complete. Created: {result['created']}, Skipped: {result['skipped']}")
        
        # Cleanup
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed default PDF templates")
    parser.add_argument(
        "--env",
        type=str,
        default="dev",
        help="Environment to run against (dev, staging, prod)",
    )
    args = parser.parse_args()
    
    asyncio.run(main(env=args.env))
