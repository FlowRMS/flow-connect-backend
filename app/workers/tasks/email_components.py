from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from commons.db.v6.enums import ProcessingResultStatus

from .email_styles import (
    BORDER,
    CARD_INNER,
    ERROR,
    PRIMARY,
    PRIMARY_LIGHT,
    SECONDARY,
    SECONDARY_LIGHT,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WARNING,
)


def build_processing_results_html(
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

    error_items = _build_error_items(errors[:5])
    more_errors = _build_more_errors_note(errors)
    errors_section = _build_errors_section(error_items, more_errors) if errors else ""

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
                                <h3 style="margin: 0; color: #F8FAFC;
                                    font-size: 15px; font-weight: 600;">
                                    Processing Results</h3>
                            </td>
                        </tr>
                    </table>
                    {_build_status_badges(created, skipped, len(errors))}
                    {errors_section}
                </td>
            </tr>
        </table>
    """


def _build_status_badges(created: int, skipped: int, error_count: int) -> str:
    return f"""
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
                        {error_count} Errors</span>
                </td>
            </tr>
        </table>
    """


def _build_error_items(errors: list[PendingDocumentProcessing]) -> str:
    items = ""
    for i, err in enumerate(errors):
        items += f"""
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
    return items


def _build_more_errors_note(errors: list[PendingDocumentProcessing]) -> str:
    if len(errors) <= 5:
        return ""
    return f"""
        <tr>
            <td style="padding: 12px 16px;
                background: rgba(148, 163, 184, 0.08);
                text-align: center; border-radius: 0 0 8px 8px;">
                <p style="margin: 0; color: {TEXT_MUTED}; font-size: 12px;">
                    + {len(errors) - 5} more errors</p>
            </td>
        </tr>
    """


def _build_errors_section(error_items: str, more_errors: str) -> str:
    return f"""
        <table role="presentation" cellspacing="0" cellpadding="0" border="0"
            width="100%" style="margin-top: 16px; border-radius: 8px;
            overflow: hidden;">
            {error_items}
            {more_errors}
        </table>
    """


def build_document_details_table(entity_type: str, tenant: str, doc_id: str) -> str:
    return f"""
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
                                    {doc_id}</code>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    """


def build_cta_button(doc_url: str) -> str:
    return f"""
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
    """
