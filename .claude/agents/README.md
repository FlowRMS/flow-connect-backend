# Flow AI - Claude Code Agents

This directory contains specialized agent configurations for Claude Code to assist with development on the Flow AI codebase.

## Available Agents

### Senior Dev Agent

**File:** `senior-dev.md`

**Purpose:** A senior Python developer agent that enforces strict coding standards and best practices for the Flow AI codebase.

**Key Features:**
- Enforces 300-line maximum per file
- Prevents redundant docstrings
- Ensures full type safety with Python 3.13 syntax
- Applies SOLID principles rigorously
- Validates code with `task all` before completion
- References ARCHITECTURE_GUIDE.md patterns

**How to Use:**

When starting a coding task with Claude Code, invoke the agent:

```
@senior-dev please implement a new repository for handling user preferences
```

Or during a conversation:

```
Use the senior-dev agent to refactor this service
```

The agent will:
1. Write code following all project conventions
2. Keep files under 300 lines
3. Use proper type hints (Python 3.13 syntax)
4. Apply SOLID principles
5. Run `task all` to verify code quality
6. Split large files into focused modules

**Common Commands:**

```bash
# After agent writes code, verify everything passes
task all

# Check specific aspects
task lint              # Ruff formatting and linting
task typecheck-basedpy # Type checking
task file-length       # File length validation
task gql              # GraphQL schema export
```

## Agent Configuration

Agents are markdown files that provide specialized instructions to Claude Code. Each agent:
- Defines a specific role/persona
- Provides context-specific guidelines
- References project documentation
- Enforces coding standards

## Creating New Agents

To create a new agent:

1. Create a new `.md` file in `.claude/agents/`
2. Define the agent's role and expertise
3. Provide specific instructions and examples
4. Reference relevant project documentation
5. Include verification steps

**Example Structure:**

```markdown
# [Agent Name]

You are a [role] working on the Flow AI codebase.

## Responsibilities
- [What the agent does]

## Guidelines
- [Specific rules]

## Examples
- [Code examples]

## Verification
- [How to verify work]
```

## Tips

- **Be specific**: The more detailed your request, the better the agent performs
- **Reference examples**: Point to existing code as examples
- **Iterative refinement**: Review agent output and provide feedback
- **Run checks**: Always verify with `task all` before committing

## Troubleshooting

**Agent not available:**
- Ensure the agent file is in `.claude/agents/`
- Check file has `.md` extension
- Restart Claude Code if needed

**Agent not following guidelines:**
- Be more explicit in your request
- Reference specific sections of the agent instructions
- Provide examples of what you want

**Code quality issues:**
- Always run `task all` after agent writes code
- Review the output and iterate
- Reference ARCHITECTURE_GUIDE.md for patterns
