from dataclasses import dataclass

import httpx

from scripts.pr_review.models import ConcernLevel, ReviewResult

_LEVEL_ICONS = {
    ConcernLevel.PASS: ":green_circle:",
    ConcernLevel.WARNING: ":yellow_circle:",
    ConcernLevel.CONCERN: ":red_circle:",
}


@dataclass
class LinearAction:
    target_status: str
    comment: str


def format_pr_comment(result: ReviewResult) -> str:
    overall = result.overall_level
    icon = _LEVEL_ICONS[overall]

    lines = [
        f"## PR Plan Review {icon}",
        "",
        "| # | Check | Level | Notes |",
        "|---|-------|-------|-------|",
    ]

    for i, check in enumerate(result.checks, 1):
        check_icon = _LEVEL_ICONS[check.level]
        lines.append(f"| {i} | {check.name} | {check_icon} | {check.notes} |")

    lines.extend([
        "",
        f"**Overall**: {icon} {overall.value.upper()}",
    ])

    return "\n".join(lines)


def determine_linear_action(result: ReviewResult) -> LinearAction:
    overall = result.overall_level

    if overall == ConcernLevel.CONCERN:
        notes = "; ".join(
            f"{c.name}: {c.notes}"
            for c in result.checks
            if c.level == ConcernLevel.CONCERN
        )
        return LinearAction(
            target_status="Todo",
            comment=f"PR review flagged concerns: {notes}",
        )

    notes = "; ".join(
        f"{c.name}: {c.notes}"
        for c in result.checks
        if c.level == ConcernLevel.WARNING
    )
    summary = f" Warnings: {notes}" if notes else ""
    return LinearAction(
        target_status="Ready to merge to staging",
        comment=f"PR review passed.{summary}",
    )


def post_pr_comment(
    pr_number: int,
    repo: str,
    comment: str,
    token: str,
) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    httpx.post(
        url,
        json={"body": comment},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    ).raise_for_status()


def resolve_linear_issue(
    identifier: str,
    api_key: str,
) -> tuple[str, str] | None:
    query = """
    query Issue($id: String!) {
        issue(id: $id) {
            id
            team { id }
        }
    }
    """
    response = httpx.post(
        "https://api.linear.app/graphql",
        json={
            "query": query,
            "variables": {"id": identifier},
        },
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    issue = response.json().get("data", {}).get("issue")
    if not issue:
        return None
    return issue["id"], issue["team"]["id"]


def resolve_linear_state(
    team_id: str,
    state_name: str,
    api_key: str,
) -> str | None:
    query = """
    query WorkflowStates($filter: WorkflowStateFilter!) {
        workflowStates(filter: $filter, first: 1) {
            nodes { id }
        }
    }
    """
    response = httpx.post(
        "https://api.linear.app/graphql",
        json={
            "query": query,
            "variables": {
                "filter": {
                    "name": {"eq": state_name},
                    "team": {"id": {"eq": team_id}},
                },
            },
        },
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    nodes = (
        response.json().get("data", {}).get("workflowStates", {}).get("nodes", [])
    )
    if not nodes:
        return None
    return nodes[0]["id"]


def post_linear_comment(
    task_id: str,
    comment: str,
    api_key: str,
) -> None:
    query = """
    mutation CommentCreate($input: CommentCreateInput!) {
        commentCreate(input: $input) {
            success
        }
    }
    """
    httpx.post(
        "https://api.linear.app/graphql",
        json={
            "query": query,
            "variables": {"input": {"issueId": task_id, "body": comment}},
        },
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30,
    ).raise_for_status()


def update_linear_status(
    issue_id: str,
    state_id: str,
    api_key: str,
) -> None:
    query = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
        issueUpdate(id: $id, input: $input) {
            success
        }
    }
    """
    httpx.post(
        "https://api.linear.app/graphql",
        json={
            "query": query,
            "variables": {
                "id": issue_id,
                "input": {"stateId": state_id},
            },
        },
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=30,
    ).raise_for_status()
