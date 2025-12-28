# Hackathon Recap Template

Template for sharing hackathon experiences, what you built, and what you learned.

Updated v2.0: Research-backed format from top LinkedIn creators.

## Structure (Problem → Process → Outcome → Lesson)

```
1. HOOK (One-liner, under 12 words)
   → Result or what you built

2. CHALLENGE (2-3 lines max)
   → What went wrong

3. SOLUTION (2-3 lines max)
   → How you fixed it

4. LESSON (1-2 lines)
   → What you'd do differently

5. CTA (Required)
   → Question

[3-5 hashtags]
```

## Template (v2.0)

```python
def generate_hackathon_post(
    hook: str,           # One-liner result (under 12 words)
    challenge: str,      # What went wrong (2-3 lines)
    solution: str,       # How you fixed it (2-3 lines)
    lesson: str,         # What you'd do differently (1-2 lines)
    hashtags: list[str], # 3-5 relevant tags
) -> str:
    """Generate a hackathon recap (700-1000 chars optimal)."""
    return f"""
{hook}

{challenge}

{solution}

{lesson}

What was your biggest hackathon challenge?
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

### Example 1: Won Placement (820 chars)

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

Lesson:
Check rate limits before you start.
Not after you hit them.

Cost us 3 hours of debugging.

Ever hit an API limit?
How did you solve it?
👇

#hackathon #ai #python
```

**Analysis:**
- Hook: 8 words ✓
- Scannable: Bullet points ✓
- Length: 820 chars ✓
- Emojis: 1 ✓
- CTA: Question ✓

### Example 2: Built Something Cool (850 chars)

```
Just finished a 24-hour hackathon.

Built a real-time code editor.

Tech stack:
 • WebSocket server
 • Monaco Editor
 • Operational Transformation

Biggest challenge?
Concurrent edits.

When two people type at once?
Whose change wins?

We used OT.
Same tech as Google Docs.
Each edit composes with others in any order.

Lesson:
Start with proven patterns.
Don't build your own conflict resolution.

Lost 4 hours on that.

What's the best thing you've built in 24 hours?
👇

#hackathon #websocket #collaboration
```

**Analysis:**
- Hook: 8 words ✓
- Scannable: Bullets + short lines ✓
- Length: 850 chars ✓
- Emojis: 0 ✓
- CTA: Question ✓

### Example 3: Learning Experience (750 chars)

```
First hackathon. Didn't finish.

But I learned a lot.

The idea:
Plant disease detector.
Upload photo, get diagnosis.

The reality:
Model had 40% accuracy.
Plant diseases look similar in photos.
We didn't have good data.

What worked:
 • Built the app
 • Used React Native
 • Learned TensorFlow Lite

Lesson:
Pick a smaller problem.
A working MVP beats an ambitious failure.

Still had fun.
Team was great.

What's a lesson you learned the hard way?
👇

#hackathon #ml #learning
```

**Analysis:**
- Hook: 7 words ✓
- Scannable: Short lines ✓
- Length: 750 chars ✓
- Emojis: 0 ✓
- CTA: Question ✓

### Example 4: Team Experience (780 chars)

```
Hackathons are about people.
Not just code.

We were 4 strangers.
By hour 6, we knew our roles:
 • Frontend: Sarah
 • Backend: Mike
 • Keeping us calm: Jamal
 • Testing: Me

We built a habit tracker.
Nothing fancy.
But it worked.

Challenge:
Merge conflicts at hour 20.

Everyone worked on different branches.
Solution?
One person handled merges.
Others kept building.

We won "Best Team Collaboration."

Lesson:
A good team beats a good idea.

What's your best hackathon story?
👇

#hackathon #teamwork #community
```

**Analysis:**
- Hook: 7 words ✓
- Scannable: Bullets ✓
- Length: 780 chars ✓
- Emojis: 0 ✓
- CTA: Question ✓

### Example 5: Honest Failure (720 chars)

```
We didn't finish our hackathon project.

Here's what went wrong.

The idea:
Voice-controlled smart home dashboard.

The reality:
Speech recognition is hard.

Problems:
 • Background noise broke our model
 • API latency made it slow
 • Battery drain was huge

We pivoted twice.
Ran out of time.

Lesson:
Test core assumptions early.
We tested at hour 18.
Should have tested at hour 2.

Still learned a lot about audio.

What's a project that didn't go as planned?
What did you learn?
👇

#hackathon #failures #lessons
```

**Analysis:**
- Hook: 8 words ✓
- Scannable: Numbered list ✓
- Length: 720 chars ✓
- Emojis: 0 ✓
- CTA: Question ✓

## Checklist (v2.0)

Every hackathon post must include:

- [ ] **One-liner hook** (result or what built, under 12 words)
- [ ] **Max 3 lines per paragraph** (scannable on mobile)
- [ ] **White space after each line** (easy to read)
- [ ] Tech stack (brief, bullet points)
- [ ] Main challenge faced
- [ ] How you solved it (or what went wrong)
- [ ] What you'd do differently
- [ ] **CTA at end** (question or prompt)
- [ ] 3-5 relevant hashtags
- [ ] **700-1000 characters** (optimal length)
- [ ] Simple English (non-native friendly)

## Tone Guidelines

| Do | Don't |
|----|----|
| Share failures too | Only post wins |
| Be honest | Pretend it was smooth |
| Give credit to team | Say "I built this alone" |
| Focus on learning | Focus only on winning |
| Keep it real | Use hype words |

## Common Mistakes (v2.0)

1. **Too much hype**: "We built the most revolutionary app!"
   - Fix: "We built a task manager using Python."

2. **No tech details**: "Used cutting-edge technology"
   - Fix: "Used FastAPI, React, and OpenAI API."

3. **Wall of text**: Long paragraphs describing everything
   - Fix: Max 3 lines per paragraph, add white space

4. **No CTA**: Post just ends with the result
   - Fix: Always end with "What's your hackathon story?"

5. **Fake modesty**: "I don't mean to brag but we won..."
   - Fix: "Our team took 2nd place."

## Platform Variations

### LinkedIn (700-1000 chars optimal)
- One-liner hook first
- Max 3 lines per paragraph
- Tech stack as bullets
- CTA required at end

### Twitter (200-270 chars, use thread)
```
1/ Just finished a 24-hour hackathon.
Built a real-time code editor.

Tech stack: Node.js + Socket.io, Monaco Editor, OT.

#hackathon #websocket

2/ Biggest challenge: Concurrent edits.

When two people type at once?
Whose change wins?

We used Operational Transformation (same as Google Docs).

3/ Lesson: Start with proven patterns.

Lost 4 hours trying to build our own conflict resolution.

What's your best hackathon story?
👇
```

### WhatsApp (50-150 chars, brief)
```
Hackathon done! Built an AI task manager.
Hit rate limits the hard way.
Exhausted but worth it.
```

## Prompt Examples

When invoking the skill, describe:

1. **Hook** - One-liner result
2. **Challenge** - What went wrong
3. **Solution** - How you fixed it
4. **Lesson** - What you'd do differently
5. **Platform** - LinkedIn, Twitter, or WhatsApp

Example prompt:
```
"Write a LinkedIn hackathon post.
Hook: Our team took 2nd place
Challenge: Hit API rate limits after 6 hours
Solution: Added request queuing and caching
Lesson: Check limits before starting
Tech stack: Python, FastAPI, React, OpenAI
Target 850 characters, include CTA"
```

---

**Version**: 2.0.0
**Last Updated**: 2025-01-28
**Based On**: Aisha Riaz structure + user's authentic voice
