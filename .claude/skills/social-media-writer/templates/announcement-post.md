# Announcement Post Template

Template for launching something new - a project, course, video, or update.

## Structure (Based on Authentic Voice)

```
[Opening hook - "Big moment" or similar]

[What's launching - clear and direct]

[The backstory - why this matters to you]

[What's included - specific details with bullets]

[Who it's for - target audience]

[Call to action - link/invite]

[Optional: Vulnerability or personal note]
```

## Template

```python
def generate_announcement_post(
    hook: str,              # Opening line
    what: str,              # What you're launching
    backstory: str,         # Why this matters
    details: list[str],     # Bullet points of what's included
    audience: str,          # Who this is for
    cta: str,               # Call to action with link
    personal_note: str = None,  # Optional vulnerability
) -> str:
    """Generate an announcement post."""
    return f"""
{hook}

{what}

{backstory}

{details}

{audience}

{cta}

{personal_note or ''}

{generate_relevant_hashtags(what, audience)}
    """.strip()
```

## Examples

### Example 1: First Video Launch
```
Big moment for me.

I just recorded my first-ever video.
Not polished.
Not scripted.
Just me… sharing what I've been building.

For a long time, I held back.
I thought:
 ❌ "Who's going to listen to me?"
 ❌ "Maybe I need to be perfect."
 ❌ "Maybe I'm not ready."

But then—something happened that changed things.
A well-known creator, Muhammad Soban Tariq Khan, reached out.

He invited me to contribute to a course on AI agents.
That message felt like a push.
Like a signal: "Hey, maybe it's time."

So, I hit record.
And I built a tiny project.
Simple, but meaningful.

Here's what I walked through in the video:
 👉 How to build a weather AI agent with free Gemini + weather API keys
 👉 How to spin up a chat frontend in ChainLit—just 28 lines of code
 👉 How to deploy the whole thing on Hugging Face Spaces—for free

All of this in under 100 lines of code.

This video is my first step into:
 ✅ Teaching
 ✅ Sharing
 ✅ Putting myself out there

I'm usually the quiet, behind-the-scenes type.

But sometimes, pressing record is harder than writing the code.
And that's why I did it.

The video is simple, not perfect.
But perfection isn't the point.
Starting is.

👉 Watch it here: https://lnkd.in/d-BTA9wN

I'd love for you to check it out—and tell me what you think.

#AI #AIagents #Python #DeveloperJourney
```

### Example 2: Course Launch
```
Something I've been working on is finally live.

I'm launching a free course on building AI agents.

Here's the backstory:

When I started learning about AI agents, I struggled.
The docs were confusing.
The examples were too complex.
I didn't know where to begin.

So I built something small.
Then another.
Then another.

And I documented everything along the way.

Now, I'm sharing what I learned.

The course covers:
 👉 What AI agents actually are (no jargon)
 👉 How to build your first agent in under 50 lines of code
 👉 How to connect agents to real tools (APIs, databases, files)
 👉 How to deploy your agent for free

This is for:
- Beginners who know some Python
- Curious developers who want to understand the hype
- Anyone who learns by building

It's free.
Always will be.

👉 Enroll here: [link]

I'll be adding more content over the coming weeks.
Would love your feedback as I improve this.

#AI #Education #FreeCourse #Python
```

### Example 3: Open Source Release
```
I just open-sourced my first project.

It's called TaskFlow.
A simple CLI task manager built with Python and Typer.

Why I built it:

I needed a task manager for my terminal.
Existing ones were either too complex or too simple.
So I built something in between.

What it does:
 • Add, list, update, and delete tasks
 • Assign tasks to team members
 • Filter by status or assignee
 • Works offline (in-memory storage)

This is for:
- Developers who live in the terminal
- Teams that want something simple
- Anyone who wants to read clean Python code

The code is well-documented.
Tests included.
Contributions welcome.

👉 Check it out: [github-link]

This is my first real open source contribution.
Excited (and a little nervous) to put it out there.

#OpenSource #Python #CLI #DevTools
```

### Example 4: Newsletter Launch
```
I'm starting a newsletter.

Here's what it's about:
Practical AI tips for developers.
No hype.
No marketing fluff.
Just stuff that actually works.

Why I'm doing this:

I learn something new about AI almost every day.
Most of it is tiny.
A trick.
A workaround.
A better way to do something.

I share some of this on LinkedIn.
But not everything.

The newsletter is where I share the deeper stuff.
The things that take more than a post to explain.

What you'll get:
- One email per week (max)
- Practical tutorials
- Code you can actually use
- No filler, no fluff

This is for developers who want to use AI, not just talk about it.

First issue goes out this Sunday.

👉 Subscribe here: [link]

#AI #Newsletter #Developers #Python
```

### Example 5: Job/Career Update
```
A quick update from my side.

I'm joining [Company] as a [Role].

I'll be working on:
- [Project/Area 1]
- [Project/Area 2]
- [Project/Area 3]

Why I'm excited:

The team is building something meaningful.
The tech stack aligns with what I love.
And there's a lot of room to grow.

I'm grateful to everyone who supported me through this journey.
You know who you are.

This is a new chapter.
Excited to see what's next.

On to the next one 🚀

#CareerUpdate #NewJob #Tech
```

## Authentic Voice Patterns (From Real Posts)

### Opening Hooks
- "Big moment for me."
- "Something I've been working on is finally live."
- "I just [did X]."
- "A quick update from my side."

### Vulnerability Markers
- "For a long time, I held back."
- "I'm usually the quiet, behind-the-scenes type."
- "Perfection isn't the point. Starting is."
- "Excited (and a little nervous)."

### Specific Details
Always include:
- Exact numbers (100 lines of code, 28 lines, $3)
- Names (Muhammad Soban Tariq Khan, not "a creator")
- Links (actual URLs, not "link in bio")
- Tech stack (Python + Typer, ChainLit, etc.)

### Bullet Style
Use emoji bullets consistently:
- 👉 for list items / what's included
- ✅ for outcomes / benefits
- ❌ for mistakes / what to avoid
- 👇 for "here's how" or steps

### Ending Patterns
- "I'd love for you to check it out—and tell me what you think."
- "Would love your feedback."
- "Let me know what you think."
- "On to the next chapter 🚀"

## Checklist

Every announcement post must include:

- [ ] Clear opening hook
- [ ] What you're launching (specific, not vague)
- [ ] Backstory or why it matters
- [ ] What's included (bullet points)
- [ ] Who it's for
- [ ] Clear call to action with link
- [ ] Optional: vulnerability or personal note
- [ ] 5-6 relevant hashtags

## Platform Variations

### LinkedIn (up to 1300 chars)
- Full story arc with vulnerability
- Detailed bullet points
- Space between every section
- Clear link with 👉

### Twitter (shorter, punchier)
```
Big moment: I just launched my first free course.

It covers building AI agents with Python.
No jargon, no fluff.
Just practical stuff.

👉 [link]

This is for beginners who learn by building.
Would love your feedback.

#AI #Education #Python
```

### WhatsApp (personal announcement)
```
Just launched my first video course! It's about building AI
agents with Python. Free forever. Link if you're interested:
[short-url]
```

## Prompt Examples

When invoking the skill, describe:

1. **What** you're launching
2. **Backstory** - why this matters
3. **Details** - what's included
4. **Audience** - who it's for
5. **CTA** - link and action
6. **Personal note** (optional) - vulnerability

Example prompt:
```
"Write an announcement post for my first YouTube video.
It's about building a weather AI agent. backstory: I was
nervous to record, but a creator encouraged me. Details:
uses Gemini + weather API, ChainLit frontend, deployed on
Hugging Face. 100 lines of code. For beginners. Link:
[youtube-link]. Include vulnerability about being nervous
to record."
```

---

**Template Version**: 1.0.0
**Last Updated**: 2025-01-28
**Based On**: Authentic user voice and patterns
