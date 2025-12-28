# Achievement Post Template

Template for sharing completed projects, shipped features, or accomplished goals.

Updated v2.0: Research-backed format from top LinkedIn creators.

## Structure (Justin Welsh 5-Step Formula)

```
1. HOOK (One-liner, under 12 words)
   → What happened

2. SETUP (2-3 lines max)
   → What you built/did

3. VALUE (2-3 lines max)
   → Numbers/metrics

4. TAKEAWAY (1-2 lines)
   → Key lesson learned

5. CTA (Required)
   → Question or prompt

[3-5 hashtags]
```

## Template (v2.0)

```python
def generate_achievement_post(
    hook: str,           # One-liner outcome (under 12 words)
    what: str,           # What you built (2-3 lines)
    metrics: str,        # Numbers/stats (2-3 lines)
    lesson: str,         # Key takeaway (1-2 lines)
    hashtags: list[str], # 3-5 relevant tags
) -> str:
    """Generate an achievement post (700-1000 chars optimal)."""
    return f"""
{hook}

{what}

{metrics}

{lesson}

What's your story?
👇

{' '.join('#' + h for h in hashtags)}
    """.strip()
```

## v2.0 Requirements

| Rule | Requirement |
|------|-------------|
| Hook | One-liner, under 12 words |
| Paragraphs | Max 3 lines each |
| Sentences | Under 12 words (most under 10) |
| Length | 700-1000 characters |
| Emojis | Max 1-2 total |
| CTA | Required at end |
| Language | Simple English |

## Examples (Updated v2.0)

### Example 1: Shipped a Project (820 chars)

```
I just shipped my first CLI app.

It's called TaskFlow.

Here's what it does:
 👉 Add tasks
 👉 List tasks
 👉 Delete tasks

Built with Python and Typer.
Took 2 weeks of evenings.

Hit plenty of bugs.
But I learned a lot.

Main takeaway:
Just build something.
The learning happens in the trenches.

What's your first project?
👇

#python #cli #webdev
```

**Analysis:**
- Hook: 7 words ✓
- Paragraphs: Max 2-3 lines ✓
- Sentences: Most 2-6 words ✓
- Length: 820 chars ✓
- Emojis: 2 ✓
- CTA: Question + 👇 ✓

### Example 2: Academic Achievement (780 chars)

```
I hit 100 percentile in Q3 today.

It wasn't easy.

Here's what it took:
 • 3 months of study
 • Countless nights coding
 • Endless cups of chai ☕

There were times I wanted to quit.
But I kept going.

The key?
Show up every day.
Even when you don't feel like it.

Grateful to my mentors and the GIAIC team.
This journey changed me.

On to the next chapter.
🚀

What goal are you working toward?
👇

#GIAIC #AI #Learning
```

**Analysis:**
- Hook: 8 words ✓
- Scannable: Bullet points, short lines ✓
- Length: 780 chars ✓
- Emojis: 2 (☕, 🚀) ✓
- CTA: Question ✓

### Example 3: Hackathon Win (850 chars)

```
Our team took 2nd place at the hackathon.

48 hours to build from scratch.

We built an AI task manager.
Using:
 • Python + FastAPI
 • React + Tailwind
 • OpenAI API

Main challenge?
API rate limits.

We hit them after 6 hours.
Had to queue requests.
Added local caching.

Judges liked the fix.
And the clean UI.

Lesson learned:
Check rate limits first.
Not after you hit them.

Ever hit a rate limit?
How did you solve it?
👇

#hackathon #ai #python
```

**Analysis:**
- Hook: 8 words ✓
- Sentences: Most 2-6 words ✓
- Length: 850 chars ✓
- Emojis: 1 ✓
- CTA: Question ✓

### Example 4: Learning Milestone (720 chars)

```
I just debugged my first race condition.

Took 4 hours.

Here's the problem:
My async function wasn't awaiting a critical DB call.

Data races are silent killers.
By the time you see them?
Damage is done.

The fix:
1. Make it synchronous first
2. Add type hints
3. Make it async only where needed

Lesson:
Start simple.
Add complexity later.

Ever hit a race condition?
What happened?
👇

#python #async #coding
```

**Analysis:**
- Hook: 8 words ✓
- Scannable: Numbered list ✓
- Length: 720 chars ✓
- Emojis: 1 ✓
- CTA: Question ✓

### Example 5: Published Content (780 chars)

```
My first article is live on Medium.

It's about building APIs.

Here's what I cover:
 👉 Authentication
 👉 Rate limiting
 👉 Error handling

Took 2 weeks to write.

Hardest part?
Explaining complex ideas simply.

I had to learn to write like I talk.
Not like a textbook.

Key takeaway:
If you can't explain it simply?
You don't understand it well enough.

Link in comments if you want to read.

What's the best advice you've gotten on writing?
👇

#writing #API #webdev
```

**Analysis:**
- Hook: 7 words ✓
- Scannable: Bullet points ✓
- Length: 780 chars ✓
- Emojis: 1 ✓
- CTA: Question ✓

## Checklist (v2.0)

Every achievement post must include:

- [ ] **One-liner hook** (under 12 words, grabs attention)
- [ ] **Max 3 lines per paragraph** (scannable on mobile)
- [ ] **White space after each line** (easy to read)
- [ ] Numbers or metrics (specific, not vague)
- [ ] Key lesson or takeaway
- [ ] **CTA at end** (question or prompt)
- [ ] 3-5 relevant hashtags
- [ ] **700-1000 characters** (optimal length)
- [ ] Max 1-2 emojis (used intentionally)
- [ ] Simple English (non-native friendly)

## Tone Guidelines

| Do | Don't |
|----|----|
| Start with the outcome | "So today I want to share..." |
| Be specific ("3 weeks") | Be vague ("a while") |
| Use simple words | Use complex words ("utilize", "leverage") |
| Sound human | Sound like PR or a bot |
| End with a question | End without CTA |

## Common Mistakes (v2.0)

1. **Weak hook**: "So today I wanted to share something..."
   - Fix: "I just shipped my first CLI app."

2. **Wall of text**: Long paragraphs without breaks
   - Fix: Max 3 lines per paragraph, add white space

3. **No CTA**: Post just ends
   - Fix: Always end with "What's your experience? 👇"

4. **Too long**: 1500+ characters
   - Fix: Aim for 700-1000 characters

5. **Complex words**: "I leveraged the synergy..."
   - Fix: "I used the combined power..."

## Platform Variations

### LinkedIn (700-1000 chars optimal)
- One-liner hook first
- Max 3 lines per paragraph
- Space between every line
- 3-5 hashtags at end
- CTA required (question + 👇)

### Twitter (200-270 chars, use thread for longer)
```
1/ I just shipped my first CLI app.
Called TaskFlow.

What it does:
• Add tasks
• List tasks
• Delete tasks

Took 2 weeks.
#python #cli

2/ Main takeaway:
Just build something.
The learning happens in the trenches.

Hit plenty of bugs.
But learned a lot.

What's your first project?
```

### WhatsApp (50-150 chars, brief)
```
Just shipped my first CLI app!
Called TaskFlow.
Took 2 weeks of evenings.
Just build stuff. That's how you learn.
```

## Prompt Examples

When invoking the skill, describe:

1. **Hook** - One-liner outcome
2. **What** - What you built (briefly)
3. **Metrics** - Numbers, timeline
4. **Lesson** - Key takeaway
5. **Platform** - LinkedIn, Twitter, or WhatsApp

Example prompt:
```
"Write a LinkedIn achievement post.
Hook: I just shipped my first CLI app
What: Built with Python and Typer, does task management
Metrics: 2 weeks of evenings, 500 lines of code
Lesson: Document as you go, saves time later
Target 800 characters, include CTA"
```

## Good vs Bad (Visual)

**GOOD (Scannable, 750 chars):**
```
I just shipped my first CLI app.

It's called TaskFlow.

Here's what it does:
 👉 Add tasks
 👉 List tasks
 👉 Delete tasks

Took 2 weeks.

Main lesson:
Just build something.
Learn by doing.

What's your first project?
👇

#python #cli
```

**BAD (Wall of text, hard to read):**
```
I just shipped my first CLI app called TaskFlow which is a task management tool that allows you to add list and delete tasks and it took me 2 weeks to build using Python and Typer and I learned a lot about CLI development along the way and the main lesson is to just build something and learn by doing.

#python #cli
```

---

**Version**: 2.0.0
**Last Updated**: 2025-01-28
**Based On**: Justin Welsh 5-step formula + user's authentic voice
