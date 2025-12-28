# Technical Deep-Dive Template

Template for explaining technical concepts, solutions, or debugging stories.

## Structure

```
[Problem statement - what you were trying to solve]

[Why existing solutions didn't work - 1-2 sentences]

[Your approach - 2-3 sentences]

[Code snippet or technical detail]

[Result - what happened]

[Key takeaway]
```

## Template

```python
def generate_technical_post(
    problem: str,           # What you were trying to solve
    context: str,           # Why existing approaches failed
    solution: str,          # Your approach
    code_snippet: str,      # Relevant code or config
    result: str,            # What happened
    takeaway: str,          # Key lesson
) -> str:
    """Generate a technical deep-dive post."""
    return f"""
{problem}

{context}

{solution}

{code_snippet}

{result}

{takeaway}

{generate_relevant_hashtags(problem, solution)}
    """.strip()
```

## Examples

### Example 1: Debugging Story
```
Spent 4 hours today debugging why my FastAPI endpoints
were returning 422 errors.

Turns out Pydantic models don't automatically handle
optional nested fields. If a field is Optional, it needs
explicit type hints at every level.

The fix:

class Item(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None

Explicit > implicit. Got it.

Lesson: Read the Pydantic docs cover to cover. The
validation rules are powerful but non-obvious.

#python #fastapi #debugging
```

### Example 2: Performance Optimization
```
Reduced API response time from 800ms to 120ms today.

Problem: Database queries were N+1-ing on every request.
User list was fetching, then fetching permissions for
each user individually.

Solution: Eager loading with select_inload.

from sqlalchemy.orm import select_inload

users = (
    session.query(User)
    .options(select_inload(User.permissions))
    .all()
)

Now all permissions load in a single query.

Lesson: Profile before optimizing. The bottleneck was
not where I expected.

#python #sqlalchemy #performance
```

### Example 3: Architecture Decision
```
Why I chose PostgreSQL over MongoDB for my latest project.

I needed:
- Complex joins across related data
- ACID transactions for payments
- Full-text search on user content
- Mature tooling and monitoring

MongoDB is great for document storage, but relational
data with foreign keys is where Postgres shines.

Added pgvector later for AI similarity search. Postgres
keeps being the right choice.

Lesson: Choose boring technology that fits your data
model, not whatever's trending.

#database #postgres #architecture
```

### Example 4: Code Pattern
```
The sentinel pattern in Python - when None isn't enough.

Problem: Distinguishing "parameter not provided" from
"parameter explicitly set to None".

Wrong way:
def update(task_id: int, assignee: Optional[int] = None):
    if assignee:  # Bug: Can't set assignee to 0!
        ...

Right way:
_UNSET = object()  # Module level

def update(task_id: int, assignee: Optional[int] = _UNSET):
    if assignee is not _UNSET:  # Works for any value
        ...

This is the pattern Typer and Pydantic use internally.

Lesson: When None is a valid value, use a sentinel.

#python #patterns #coding
```

### Example 5: Tooling Setup
```
Set up pre-commit hooks for my Python project today.

What it does:
- Runs black (formatting) on every commit
- Runs isort (import sorting)
- Runs mypy (type checking)
- Runs pytest (tests)

If any check fails, commit is rejected.

Setup in .pre-commit-config.yaml:

repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

Caught 3 type hints I missed before first push.

Lesson: Automate quality checks. Your future self will
thank you.

#python #tooling #workflow
```

## Checklist

Every technical post must include:

- [ ] Clear problem statement
- [ ] Why it was a problem (context)
- [ ] Your specific approach or solution
- [ ] Code snippet, config, or technical detail
- [ ] Result or outcome
- [ ] Key takeaway or lesson
- [ ] Relevant hashtags (2-5)

## Tone Guidelines

| Do | Don't |
|----|----|
| Explain the "why" | Just dump code |
| Show the before/after | Show only the solution |
| Admit what you got wrong | Pretend you knew all along |
| Use concrete examples | Abstract descriptions |
| Teach one thing clearly | Cover too much |

## Common Mistakes

1. **Too much code**: Posting entire files
   - Fix: Show only relevant snippets (5-15 lines)

2. **No context**: Here's how to do X
   - Fix: Start with the problem you were solving

3. **No explanation**: Just code
   - Fix: Explain what each part does

4. **Too broad**: How to build an entire API
   - Fix: Focus on one specific aspect

5. **No lesson**: Here's what I did
   - Fix: Always end with what you learned

## Twitter Thread Format

For technical content on Twitter, use a thread:

```
1/ Spent 4 hours debugging a 422 error in FastAPI.

Turns out Pydantic models don't automatically handle
optional nested fields.

The fix 👇

#python #fastapi

2/ The issue: Optional fields need explicit type hints
at every level.

Wrong:
class Item(BaseModel):
    metadata: dict  # Required

Right:
class Item(Base BaseModel):
    metadata: Optional[Dict[str, Any]] = None

3/ Explicit > implicit.

Read the Pydantic docs cover to cover. The validation
rules are powerful but non-obvious.

Lesson learned: Type hints matter.

#debugging #pydantic
```

## Platform Variations

### LinkedIn (up to 1300 chars)
- 3-5 paragraphs
- Code blocks with triple backticks
- Space between paragraphs
- End with hashtags

### Twitter (use thread format)
- Each tweet: one concept
- Number them (1/, 2/, 3/)
- End with takeaway

### WhatsApp
- Rarely used for deep technical content
- Better for: "Just fixed a tricky bug, learning: X"

## Prompt Examples

When invoking the skill, describe:

1. **Problem** you solved
2. **Context** (why it was hard)
3. **Solution** (technical approach)
4. **Result** (what happened)
5. **Lesson** learned

Example prompt:
```
"Write a technical post about fixing a race condition
in Python. Was using async but forgot to await a DB
call. Took 4 hours to debug. Fixed by adding type hints
and strict linting. Lesson: make it synchronous first,
add async when you need it. LinkedIn post."
```

---

**Template Version**: 1.0.0
**Last Updated**: 2025-01-28
