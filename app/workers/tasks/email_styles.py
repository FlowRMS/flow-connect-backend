from commons.db.v6.enums import WorkflowStatus

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


def get_status_config(status: WorkflowStatus) -> dict[str, str]:
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
