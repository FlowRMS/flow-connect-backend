from datetime import datetime

from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from commons.db.v6.enums import WorkflowStatus
from commons.db.v6.user import User

from .email_components import (
    build_cta_button,
    build_document_details_table,
    build_processing_results_html,
)
from .email_styles import (
    BACKGROUND,
    BACKGROUND_LIGHT,
    BORDER,
    BORDER_LIGHT,
    CARD_BG,
    CARD_INNER,
    PRIMARY,
    PRIMARY_LIGHT,
    SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    get_status_config,
)


def build_pending_document_status_email(
    pending_document: PendingDocument,
    processing_records: list[PendingDocumentProcessing],
    user: User | None,
    tenant: str,
    frontend_base_url: str,
) -> str:
    status = pending_document.workflow_status or WorkflowStatus.IN_PROGRESS
    config = get_status_config(status)

    entity_type = (
        pending_document.entity_type.name.replace("_", " ").title()
        if pending_document.entity_type
        else "Unknown"
    )
    user_name = user.full_name if user else "User"
    doc_url = (
        f"{frontend_base_url}/flow-ai/upload-complete?pendingId={pending_document.id}"
    )
    processing_html = build_processing_results_html(processing_records)

    header_section = _build_header_section()
    status_section = _build_status_section(config)
    details_section = _build_details_section(
        user_name,
        entity_type,
        tenant,
        str(pending_document.id),
        processing_html,
        doc_url,
    )
    footer_section = _build_footer_section()

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>FlowAI - Document Processing Status</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0;
        background: linear-gradient(180deg, {BACKGROUND} 0%, #0C1322 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
        Roboto, 'Helvetica Neue', Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale; min-height: 100vh;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0"
            width="100%" style="background: linear-gradient(180deg,
            {BACKGROUND} 0%, #0C1322 100%);">
            <tr>
                <td style="padding: 40px 20px;">
                    <table role="presentation" cellspacing="0" cellpadding="0"
                        border="0" width="600"
                        style="max-width: 600px; margin: 0 auto;">
                        <tr>
                            <td style="height: 4px;
                                background: linear-gradient(90deg, {PRIMARY} 0%,
                                {SECONDARY} 50%, {PRIMARY_LIGHT} 100%);
                                border-radius: 4px 4px 0 0;"></td>
                        </tr>
                        {header_section}
                        {status_section}
                        {details_section}
                        {footer_section}
                        <tr>
                            <td style="height: 4px;
                                background: linear-gradient(90deg, {SECONDARY} 0%,
                                {PRIMARY} 50%, {PRIMARY_LIGHT} 100%);
                                border-radius: 0 0 4px 4px;"></td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def _build_header_section() -> str:
    return f"""
        <tr>
            <td style="background: linear-gradient(135deg,
                {BACKGROUND_LIGHT} 0%, {CARD_BG} 100%);
                padding: 32px 32px 40px 32px;
                border-left: 1px solid {BORDER};
                border-right: 1px solid {BORDER};">
                <table role="presentation" cellspacing="0"
                    cellpadding="0" border="0" width="100%">
                    <tr>
                        <td style="background: linear-gradient(135deg,
                            rgba(80, 72, 230, 0.15) 0%,
                            rgba(11, 132, 199, 0.1) 100%);
                            border: 1px solid rgba(80, 72, 230, 0.2);
                            border-radius: 16px; padding: 28px;
                            text-align: center;">
                            <h1 style="margin: 0 0 8px 0;
                                color: {TEXT_PRIMARY};
                                font-size: 26px; font-weight: 700;
                                letter-spacing: -0.5px;">
                                Document Processing Status
                            </h1>
                            <p style="margin: 0;
                                color: {TEXT_MUTED};
                                font-size: 15px; font-weight: 400;">
                                Your document has finished processing
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    """


def _build_status_section(config: dict[str, str]) -> str:
    return f"""
        <tr>
            <td style="background: {CARD_BG}; padding: 0 32px;
                border-left: 1px solid {BORDER};
                border-right: 1px solid {BORDER};">
                <table role="presentation" cellspacing="0"
                    cellpadding="0" border="0" width="100%"
                    style="margin-top: -20px;">
                    <tr>
                        <td style="background: {CARD_INNER};
                            border-radius: 16px; padding: 24px;
                            text-align: center;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                            0 0 0 1px rgba(255, 255, 255, 0.05);
                            border: 1px solid {BORDER};">
                            <table role="presentation" cellspacing="0"
                                cellpadding="0" border="0"
                                style="margin: 0 auto 16px auto;">
                                <tr>
                                    <td style="width: 64px;
                                        height: 64px;
                                        background: {config["bg"]};
                                        border: 2px solid {config["border"]};
                                        border-radius: 50%;
                                        text-align: center;
                                        vertical-align: middle;
                                        box-shadow: 0 0 24px {config["glow"]};">
                                        <span style="color: {config["color"]};
                                            font-size: 28px;
                                            line-height: 60px;">
                                            {config["icon"]}</span>
                                    </td>
                                </tr>
                            </table>
                            <div style="display: inline-block;
                                background: {config["gradient"]};
                                padding: 10px 28px;
                                border-radius: 50px;
                                box-shadow: 0 4px 16px {config["glow"]};">
                                <span style="color: #FFFFFF;
                                    font-size: 14px;
                                    font-weight: 700;
                                    text-transform: uppercase;
                                    letter-spacing: 1.5px;">
                                    {config["label"]}</span>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    """


def _build_details_section(
    user_name: str,
    entity_type: str,
    tenant: str,
    doc_id: str,
    processing_html: str,
    doc_url: str,
) -> str:
    return f"""
        <tr>
            <td style="background: {CARD_BG}; padding: 32px;
                border-left: 1px solid {BORDER};
                border-right: 1px solid {BORDER};">
                <p style="margin: 0 0 24px 0;
                    color: {TEXT_SECONDARY};
                    font-size: 15px; line-height: 1.7;">
                    Hi <strong style="color: {TEXT_PRIMARY};">
                        {user_name}</strong>,<br>
                    Here's the status of your document processing:
                </p>
                {build_document_details_table(entity_type, tenant, doc_id)}
                {processing_html}
                {build_cta_button(doc_url)}
            </td>
        </tr>
    """


def _build_footer_section() -> str:
    return f"""
        <tr>
            <td style="background: linear-gradient(180deg,
                {CARD_BG} 0%, {BACKGROUND_LIGHT} 100%);
                padding: 28px 32px; text-align: center;
                border-left: 1px solid {BORDER};
                border-right: 1px solid {BORDER};
                border-bottom: 1px solid {BORDER};
                border-radius: 0 0 16px 16px;">
                <div style="height: 1px;
                    background: linear-gradient(90deg,
                    transparent 0%, {BORDER} 50%,
                    transparent 100%); margin-bottom: 24px;"></div>
                <p style="margin: 0 0 6px 0;
                    color: {TEXT_MUTED}; font-size: 13px;">
                    Powered by <strong
                        style="background: linear-gradient(135deg,
                        {PRIMARY} 0%, {SECONDARY} 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;">FlowAI</strong>
                </p>
                <p style="margin: 0 0 20px 0;
                    color: {BORDER_LIGHT}; font-size: 12px;">
                    {datetime.now().strftime("%B %d, %Y at %I:%M %p")} UTC
                </p>
                <p style="margin: 0; color: {BORDER_LIGHT};
                    font-size: 11px;">
                    &copy; {datetime.now().year} FlowAI. All rights reserved.
                </p>
            </td>
        </tr>
    """
