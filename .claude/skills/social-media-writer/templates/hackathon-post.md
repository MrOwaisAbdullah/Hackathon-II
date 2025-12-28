# Hackathon Recap Template

Template for sharing hackathon experiences, what you built, and what you learned.

## Structure

```
[What we built - one sentence summary]

[The challenge we hit - what went wrong]

[How we solved it - technical approach]

[What I'd do differently - lesson learned]

[Result/award if applicable]

[Fun/relatable moment]
```

## Template

```python
def generate_hackathon_post(
    project_name: str,       # What you built
    challenge: str,          # Main problem faced
    solution: str,           # How you solved it
    lesson: str,             # What you'd do differently
    result: str = None,      # Award/placement (optional)
    fun_moment: str = None,  # Fun detail (optional)
) -> str:
    """Generate a hackathon recap post."""
    return f"""
{project_name}

{challenge}

{solution}

{lesson}

{result or ''}

{fun_moment or ''}

{generate_relevant_hashtags(project_name, solution)}
    """.strip()
```

## Examples

### Example 1: Won a Placement
```
Our team took 2nd place at the regional hackathon this
weekend.

48 hours to build something from scratch. We made an
AI-powered task prioritization tool using:
- OpenAI API for analysis
- FastAPI backend
- React + Tailwind frontend

Main challenge was handling API rate limits. We hit the
free tier cap after 6 hours. Fixed it by implementing
request queuing and local caching.

Would do differently: Check rate limits before starting,
not after. Cost us 3 hours of debugging.

Judges liked the clean UI and the technical approach to
API constraints.

Fun moment: We ordered pizza at 3 AM and it arrived
just as we deployed. Perfect timing.

#hackathon #ai #webdev
```

### Example 2: Built Something Cool
```
Just finished a 24-hour hackathon. Built a real-time
collaborative code editor.

Tech stack:
- WebSocket server (Node.js + Socket.io)
- Monaco Editor for the IDE interface
- Operational Transformation for conflict resolution

Biggest challenge: Handling concurrent edits. When two
people type at once, whose change wins?

We used OT (same tech as Google Docs). Each edit becomes
a transformation operation that can be composed with
others in any order.

Would do differently: Start with OT, don't try to build
your own conflict resolution. We lost 4 hours on that.

Didn't win anything but learned a ton about distributed
systems.

#hackathon #websocket #collaboration
```

### Example 3: Learning Experience
```
First time participating in a hackathon. We didn't finish
the project, but I learned more in 24 hours than in a
month of tutorials.

Idea: Plant disease detector using computer vision.
Upload photo of leaf, get diagnosis.

Reality: Our model had 40% accuracy. Turns out plant
diseases look very similar in photos, and we didn't
have quality training data.

What worked: Built a working React Native app with image
upload. Integrated with a Flask backend. Learned about
TensorFlow Lite for mobile inference.

Would do differently: Pick a smaller problem. We tried
to do too much. A working MVP beats an ambitious failure.

Still had fun. Team was great.

#hackathon #ml #mobiledev
```

### Example 4: Team Experience
```
Hackathons are less about code, more about people.

We were 4 strangers who met at the event. By hour 6,
we'd figured out:
- Who can ship frontend fast (Sarah)
- Who handles the complex backend (Mike)
- Who keeps the team calm and fed (Jamal)
- Who tests everything (me)

We built a habit-tracker app with gamification.
Nothing revolutionary, but it worked.

Challenge: Merge conflicts at hour 20. Everyone had been
working on different branches. Solution: One person
handled merges, others kept building features.

Won "Best Team Collaboration" - apparently the judges
noticed we weren't arguing.

Lesson: A good team beats a good idea.

#hackathon #teamwork #collaboration
```

### Example 5: Failure Post
```
We didn't finish our hackathon project. Here's what went
wrong.

Idea: Voice-controlled smart home dashboard.
Reality: Speech recognition is hard.

Problems we hit:
1. Background noise at the venue broke our model
2. API latency made it feel unresponsive
3. Battery drain on continuous listening

We pivoted twice. Started with Web Speech API, switched
to a service, ran out of time trying to optimize.

What I'd do differently:
- Test core assumptions early (we tested at hour 18)
- Have a smaller MVP ready
- Focus on one feature, not three

Still worth it. I now know more about audio processing
than I did Friday.

#hackathon #failures #lessonslearned
```

## Checklist

Every hackathon post should include:

- [ ] What you built (one-line summary)
- [ ] Tech stack (brief list)
- [ ] Main challenge faced
- [ ] How you solved it
- [ ] What you'd do differently
- [ ] Result (placement, what you learned, or fun moment)
- [ ] 3-5 relevant hashtags

## Tone Guidelines

| Do | Don't |
|----|----|
| Share failures too | Only post wins |
| Be honest about challenges | Pretend it was smooth |
| Give credit to team | Say "I built this" |
| Include fun moments | Make it sound like work |
| Focus on learning | Focus only on winning |

## Common Mistakes

1. **Too much hype**: "We built the most revolutionary app!"
   - Fix: Describe what it actually does

2. **No tech details**: "Used cutting-edge technology"
   - Fix: List actual stack (FastAPI, React, etc.)

3. **Fake modesty**: "I don't mean to brag but..."
   - Fix: Own the achievement or share the failure honestly

4. **No lesson learned**: Just what you built
   - Fix: Always include what you'd do differently

5. **Too long**: 2000+ words
   - Fix: Keep it under 1300 chars (LinkedIn)

## Platform Variations

### LinkedIn (up to 1300 chars)
- 4-6 paragraphs
- Space between paragraphs
- Include tech stack as bulleted list
- End with hashtags

### Twitter (use thread format)
```
1/ Just finished a 24-hour hackathon. Built a real-time
collaborative code editor.

Tech stack: Node.js + Socket.io, Monaco Editor, OT
for conflict resolution.

#hackathon #websocket

2/ Biggest challenge: Handling concurrent edits.

When two people type at once, whose change wins?

We used Operational Transformation (same tech as Google
Docs). Each edit composes with others in any order.

3/ Would do differently: Start with OT, don't try to
build your own conflict resolution.

Lost 4 hours on that. Lesson learned.

#collaboration #lessonslearned
```

### WhatsApp (brief recap)
```
Hackathon done! Built an AI task manager with the team.
Didn't win but learned about rate limiting the hard way.
Exhausted but worth it.
```

## Prompt Examples

When invoking the skill, describe:

1. **What** you built
2. **Challenge** faced
3. **Solution** approach
4. **Lesson** learned
5. **Result** (optional)

Example prompt:
```
"Write a hackathon recap. Built an AI task manager with
FastAPI and React. Hit API rate limits, fixed with request
queuing. Lesson: check limits before starting. Took 2nd
place. LinkedIn post."
```

---

**Template Version**: 1.0.0
**Last Updated**: 2025-01-28
