import os
import subprocess
import sys

from scripts.pr_review.collector import collect_context, detect_plan_docs
from scripts.pr_review.notifier import (
    determine_linear_action,
    format_pr_comment,
    post_linear_comment,
    post_pr_comment,
    resolve_linear_issue,
    resolve_linear_state,
    update_linear_status,
)
from scripts.pr_review.reviewer import (
    build_prompt,
    call_claude_api,
    check_missing_linear_task,
    parse_response,
)


def _get_changed_files(base_ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def _get_diff(base_ref: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _get_commits(base_ref: str) -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", f"{base_ref}..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def _set_github_output(name: str, value: str) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")


def main() -> None:
    base_ref = f"origin/{os.environ.get('GITHUB_BASE_REF', 'main')}"
    pr_number = int(os.environ.get("PR_NUMBER", "0"))
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    linear_api_key = os.environ.get("LINEAR_API_KEY", "")

    changed_files = _get_changed_files(base_ref)
    plan_docs = detect_plan_docs(changed_files)

    if not plan_docs:
        print("No plan/hotfix documents found in changed files. Skipping review.")
        _set_github_output("review_status", "skipped")
        return

    for plan_path in plan_docs:
        print(f"Reviewing: {plan_path}")
        plan_content = _read_file(plan_path)
        diff = _get_diff(base_ref)
        commits = _get_commits(base_ref)

        context = collect_context(
            plan_path=plan_path,
            plan_content=plan_content,
            diff=diff,
            commits=commits,
        )

        prompt = build_prompt(context)
        response_text = call_claude_api(prompt, anthropic_api_key)
        result = parse_response(response_text)

        missing_task_check = check_missing_linear_task(context)
        if missing_task_check:
            result.checks.append(missing_task_check)

        comment = format_pr_comment(result)
        if pr_number and github_token:
            post_pr_comment(pr_number, repo, comment, github_token)

        if context.linear_task_id and linear_api_key:
            issue_info = resolve_linear_issue(
                context.linear_task_id, linear_api_key,
            )
            if issue_info:
                issue_uuid, team_id = issue_info
                action = determine_linear_action(result)
                post_linear_comment(issue_uuid, action.comment, linear_api_key)
                state_id = resolve_linear_state(
                    team_id, action.target_status, linear_api_key,
                )
                if state_id:
                    update_linear_status(issue_uuid, state_id, linear_api_key)

        status = result.overall_level.value
        _set_github_output("review_status", status)
        print(f"Review complete: {status}")

        if status == "concern":
            sys.exit(1)


if __name__ == "__main__":
    main()
