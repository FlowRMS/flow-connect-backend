from datetime import datetime

from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from commons.db.v6.enums import ProcessingResultStatus, WorkflowStatus
from commons.db.v6.user import User

PRIMARY = "#5048E6"
PRIMARY_LIGHT = "#8D86FF"
SECONDARY = "#0B84C7"
SECONDARY_LIGHT = "#38B6FF"
SUCCESS = "#10B981"
SUCCESS_LIGHT = "#6BD194"
WARNING = "#F59E0B"
WARNING_LIGHT = "#FCD34D"
ERROR = "#EF4444"
ERROR_LIGHT = "#FCA5A5"
BACKGROUND = "#0F172A"
BACKGROUND_LIGHT = "#1E293B"
CARD_BG = "#1E293B"
CARD_INNER = "#334155"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#E2E8F0"
TEXT_MUTED = "#94A3B8"
BORDER = "#475569"
BORDER_LIGHT = "#64748B"
LOGO_URL = "https://i.imgur.com/zj5k4wy.png"


def _get_status_config(status: WorkflowStatus) -> dict[str, str]:
    configs = {
        WorkflowStatus.COMPLETED: {
            "color": SUCCESS,
            "color_light": SUCCESS_LIGHT,
            "bg": "rgba(16, 185, 129, 0.15)",
            "border": "rgba(16, 185, 129, 0.4)",
            "glow": "rgba(16, 185, 129, 0.3)",
            "icon": "&#10003;",
            "label": "Completed",
            "gradient": f"linear-gradient(135deg, {SUCCESS} 0%, #059669 100%)",
        },
        WorkflowStatus.FAILED: {
            "color": ERROR,
            "color_light": ERROR_LIGHT,
            "bg": "rgba(239, 68, 68, 0.15)",
            "border": "rgba(239, 68, 68, 0.4)",
            "glow": "rgba(239, 68, 68, 0.3)",
            "icon": "&#10005;",
            "label": "Failed",
            "gradient": f"linear-gradient(135deg, {ERROR} 0%, #DC2626 100%)",
        },
        WorkflowStatus.PAUSED: {
            "color": WARNING,
            "color_light": WARNING_LIGHT,
            "bg": "rgba(245, 158, 11, 0.15)",
            "border": "rgba(245, 158, 11, 0.4)",
            "glow": "rgba(245, 158, 11, 0.3)",
            "icon": "&#10074;&#10074;",
            "label": "Paused",
            "gradient": f"linear-gradient(135deg, {WARNING} 0%, #D97706 100%)",
        },
        WorkflowStatus.IN_PROGRESS: {
            "color": SECONDARY,
            "color_light": SECONDARY_LIGHT,
            "bg": "rgba(11, 132, 199, 0.15)",
            "border": "rgba(11, 132, 199, 0.4)",
            "glow": "rgba(11, 132, 199, 0.3)",
            "icon": "&#8635;",
            "label": "In Progress",
            "gradient": f"linear-gradient(135deg, {SECONDARY} 0%, #0369A1 100%)",
        },
    }
    return configs.get(
        status,
        {
            "color": TEXT_MUTED,
            "color_light": TEXT_SECONDARY,
            "bg": "rgba(148, 163, 184, 0.15)",
            "border": "rgba(148, 163, 184, 0.4)",
            "glow": "rgba(148, 163, 184, 0.3)",
            "icon": "&#128196;",
            "label": str(status.name) if status else "Unknown",
            "gradient": f"linear-gradient(135deg, {TEXT_MUTED} 0%, #64748B 100%)",
        },
    )


def _build_processing_results_html(
    processing_records: list[PendingDocumentProcessing],
) -> str:
    if not processing_records:
        return ""

    created = sum(
        1 for r in processing_records if r.status == ProcessingResultStatus.CREATED
    )
    skipped = sum(
        1 for r in processing_records if r.status == ProcessingResultStatus.SKIPPED
    )
    errors = [r for r in processing_records if r.status == ProcessingResultStatus.ERROR]

    error_items = ""
    for i, err in enumerate(errors[:5]):
        error_items += f"""
            <tr>
                <td style="padding: 14px 16px; background: rgba(239, 68, 68, 0.08);
                    border-left: 3px solid {ERROR};
                    border-bottom: 1px solid rgba(239, 68, 68, 0.1);">
                    <table role="presentation" cellspacing="0" cellpadding="0"
                        border="0" width="100%">
                        <tr>
                            <td style="width: 24px; vertical-align: top;
                                padding-right: 12px;">
                                <div style="width: 20px; height: 20px;
                                    background: rgba(239, 68, 68, 0.2);
                                    border-radius: 50%; text-align: center;
                                    line-height: 20px; font-size: 10px;
                                    color: {ERROR}; font-weight: 600;">{i + 1}</div>
                            </td>
                            <td style="vertical-align: top;">
                                <p style="margin: 0; color: {TEXT_SECONDARY};
                                    font-size: 13px; line-height: 1.5;">
                                    {err.error_message or "Unknown error"}</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        """

    more_errors = ""
    if len(errors) > 5:
        more_errors = f"""
            <tr>
                <td style="padding: 12px 16px;
                    background: rgba(148, 163, 184, 0.08);
                    text-align: center; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0; color: {TEXT_MUTED}; font-size: 12px;">
                        + {len(errors) - 5} more errors</p>
                </td>
            </tr>
        """

    errors_section = ""
    if errors:
        errors_section = f"""
            <table role="presentation" cellspacing="0" cellpadding="0" border="0"
                width="100%" style="margin-top: 16px; border-radius: 8px;
                overflow: hidden;">
                {error_items}
                {more_errors}
            </table>
        """

    return f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0"
            width="100%" style="margin-top: 24px;">
            <tr>
                <td style="padding: 20px; background: {CARD_INNER};
                    border-radius: 12px; border: 1px solid {BORDER};">
                    <table role="presentation" cellspacing="0" cellpadding="0"
                        border="0" width="100%" style="margin-bottom: 16px;">
                        <tr>
                            <td style="width: 4px;
                                background: linear-gradient(180deg, {PRIMARY} 0%,
                                {SECONDARY} 100%); border-radius: 2px;"></td>
                            <td style="padding-left: 12px;">
                                <h3 style="margin: 0; color: {TEXT_PRIMARY};
                                    font-size: 15px; font-weight: 600;">
                                    Processing Results</h3>
                            </td>
                        </tr>
                    </table>
                    <table role="presentation" cellspacing="0" cellpadding="0"
                        border="0" width="100%">
                        <tr>
                            <td style="padding: 8px 0;">
                                <span style="display: inline-block;
                                    background: rgba(16, 185, 129, 0.15);
                                    color: {SUCCESS}; padding: 6px 14px;
                                    border-radius: 50px; font-size: 13px;
                                    font-weight: 600; margin-right: 8px;">
                                    {created} Created</span>
                                <span style="display: inline-block;
                                    background: rgba(245, 158, 11, 0.15);
                                    color: {WARNING}; padding: 6px 14px;
                                    border-radius: 50px; font-size: 13px;
                                    font-weight: 600; margin-right: 8px;">
                                    {skipped} Skipped</span>
                                <span style="display: inline-block;
                                    background: rgba(239, 68, 68, 0.15);
                                    color: {ERROR}; padding: 6px 14px;
                                    border-radius: 50px; font-size: 13px;
                                    font-weight: 600;">
                                    {len(errors)} Errors</span>
                            </td>
                        </tr>
                    </table>
                    {errors_section}
                </td>
            </tr>
        </table>
    """


def build_pending_document_status_email(
    pending_document: PendingDocument,
    processing_records: list[PendingDocumentProcessing],
    user: User | None,
    tenant: str,
    frontend_base_url: str,
) -> str:
    status = pending_document.workflow_status or WorkflowStatus.IN_PROGRESS
    config = _get_status_config(status)

    entity_type = (
        pending_document.entity_type.name.replace("_", " ").title()
        if pending_document.entity_type
        else "Unknown"
    )
    user_name = user.full_name if user else "User"

    doc_url = (
        f"{frontend_base_url}/flow-ai/upload-complete?pendingId={pending_document.id}"
    )

    processing_html = _build_processing_results_html(processing_records)

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
                                <table role="presentation" cellspacing="0"
                                    cellpadding="0" border="0" width="100%"
                                    style="background: {CARD_INNER};
                                    border-radius: 12px; border: 1px solid {BORDER};
                                    overflow: hidden;">
                                    <tr>
                                        <td style="padding: 16px 20px;
                                            background: linear-gradient(135deg,
                                            rgba(80, 72, 230, 0.1) 0%,
                                            rgba(11, 132, 199, 0.05) 100%);
                                            border-bottom: 1px solid {BORDER};">
                                            <table role="presentation" cellspacing="0"
                                                cellpadding="0" border="0" width="100%">
                                                <tr>
                                                    <td style="width: 4px;
                                                        background: linear-gradient(180deg,
                                                        {PRIMARY} 0%, {SECONDARY} 100%);
                                                        border-radius: 2px;"></td>
                                                    <td style="padding-left: 12px;">
                                                        <h3 style="margin: 0;
                                                            color: {TEXT_PRIMARY};
                                                            font-size: 14px;
                                                            font-weight: 600;
                                                            text-transform: uppercase;
                                                            letter-spacing: 0.5px;">
                                                            Document Details</h3>
                                                    </td>
                                                    <td style="text-align: right;">
                                                        <span style="display: inline-block;
                                                            background: linear-gradient(135deg,
                                                            {PRIMARY} 0%, {PRIMARY_LIGHT} 100%);
                                                            color: #FFFFFF;
                                                            padding: 4px 12px;
                                                            border-radius: 50px;
                                                            font-size: 11px;
                                                            font-weight: 600;
                                                            text-transform: uppercase;">
                                                            {entity_type}</span>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 6px 20px;">
                                            <table role="presentation" cellspacing="0"
                                                cellpadding="0" border="0" width="100%">
                                                <tr>
                                                    <td style="padding: 14px 0;
                                                        border-bottom: 1px solid
                                                        rgba(71, 85, 105, 0.5);">
                                                        <span style="color: {TEXT_MUTED};
                                                            font-size: 12px;
                                                            text-transform: uppercase;
                                                            letter-spacing: 0.5px;
                                                            font-weight: 500;">
                                                            Tenant</span>
                                                    </td>
                                                    <td style="padding: 14px 0;
                                                        border-bottom: 1px solid
                                                        rgba(71, 85, 105, 0.5);
                                                        text-align: right;">
                                                        <span style="display: inline-block;
                                                            background: rgba(11, 132, 199, 0.15);
                                                            color: {SECONDARY_LIGHT};
                                                            padding: 3px 10px;
                                                            border-radius: 6px;
                                                            font-size: 13px;
                                                            font-weight: 500;">
                                                            {tenant}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 14px 0;">
                                                        <span style="color: {TEXT_MUTED};
                                                            font-size: 12px;
                                                            text-transform: uppercase;
                                                            letter-spacing: 0.5px;
                                                            font-weight: 500;">
                                                            Document ID</span>
                                                    </td>
                                                    <td style="padding: 14px 0;
                                                        text-align: right;">
                                                        <code style="background:
                                                            rgba(80, 72, 230, 0.15);
                                                            color: {PRIMARY_LIGHT};
                                                            padding: 4px 10px;
                                                            border-radius: 6px;
                                                            font-size: 10px;
                                                            font-family: 'SF Mono', Monaco,
                                                            'Courier New', monospace;
                                                            border: 1px solid
                                                            rgba(80, 72, 230, 0.2);">
                                                            {pending_document.id}</code>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                {processing_html}
                                <table role="presentation" cellspacing="0"
                                    cellpadding="0" border="0" width="100%"
                                    style="margin-top: 32px;">
                                    <tr>
                                        <td style="text-align: center;">
                                            <a href="{doc_url}"
                                                style="display: inline-block;
                                                background: linear-gradient(135deg,
                                                {PRIMARY} 0%, {PRIMARY_LIGHT} 50%,
                                                {SECONDARY} 100%); color: #FFFFFF;
                                                text-decoration: none;
                                                padding: 16px 48px;
                                                border-radius: 50px;
                                                font-size: 14px; font-weight: 700;
                                                letter-spacing: 0.5px;
                                                box-shadow: 0 8px 24px
                                                rgba(80, 72, 230, 0.4),
                                                0 0 0 1px rgba(255, 255, 255, 0.1) inset;">
                                                View in FlowAI
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
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
