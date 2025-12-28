# Advice Post Template

Template for sharing something you learned that might help others.

## Structure (Based on Authentic Voice)

```
[Opening hook - observation or situation]

[Common mistake or problem you see]

[What actually works - your approach]

[Specific example or steps]

[Why this is better]

[Optional: Personal note or vulnerability]

[Call to action or question]
```

## Template

```python
def generate_advice_post(
    observation: str,      # What you're noticing
    problem: str,          # Common mistake
    solution: str,         # What actually works
    example: str,          # Specific example or steps
    why: str,              # Why this approach is better
    personal_note: str = None,  # Optional vulnerability
    cta: str = None,       # Optional call to action
) -> str:
    """Generate an advice post."""
    return f"""
{observation}

{problem}

{solution}

{example}

{why}

{personal_note or ''}

{cta or ''}

{generate_relevant_hashtags(observation, solution)}
    """.strip()
```

## Examples

### Example 1: API Key Advice
```
A small tip for all GIAIC students and learners 👇

Let's stop wasting time changing free Gemini keys again and again.
It gets annoying, breaks your workflow, and honestly… slows everything down.

If you can afford it, go for the $20 Claude Code plan.

If not, the $3 GLM 4.6 plan is more than enough.
It works almost the same and gives higher limits.

Use one paid model as your main tool (Claude or GLM).
Only switch to free Gemini when you hit limits.

If you really can't spend anything, it's okay.
We'll continue using the free Gemini key together.

I'm using the $3 GLM plan, and it's working great for me.

Here's the simple GLM setup ⬇️

How to set up GLM:
 1. Buy the GLM plan and copy your API key: https://lnkd.in/dPGF-ai5

 2. Open or create this file:
 $HOME/.claude/settings.json

 3. Paste this inside the file (add your API key):

{
 "alwaysThinkingEnabled": true,
 "env": {
 "ANTHROPIC_AUTH_TOKEN": "your api key here",
 "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
 "API_TIMEOUT_MS": "3000000",
 "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
 "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
 "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
 }
}

 4. Run Claude Code.

That's it.

Let's spend time building things, not fixing API keys every day.

#AI #ClaudeCode #GLM #Students #Developers
```

### Example 2: Learning Advice
```
I wish I knew this earlier.

When I started learning AI, I made a mistake.

I tried to learn everything at once.
- Models
- Frameworks
- Deployment
- MLOps
- Everything

Result: I knew a little about everything, but nothing well.

Here's what I wish I did:

 👉 Pick ONE thing
 👉 Go deep on it
 👉 Build something real
 👉 Then move to the next

My first real project was a simple chatbot.
Just Python + OpenAI API.
Nothing fancy.

But I finished it.
Deployed it.
Used it.

That one project taught me more than 20 tutorials.

Learning depth > breadth.

Always.

#AI #Learning #Python #Advice
```

### Example 3: Debugging Tip
```
Spent 4 hours debugging a race condition today.

Here's what I learned.

The issue: Async function wasn't actually awaiting a critical database call.

Data races are silent killers.

Here's how I fixed it:

1. Made it synchronous first (to confirm logic)
2. Added type hints (to catch issues early)
3. Made it async again (only where needed)

The lesson?

When in doubt, make it synchronous first.
Add async only when you have a proven need.

Explicit > implicit.

Always.

#Python #Async #Debugging #Coding
```

### Example 4: Career Advice
```
Something I wish someone told me earlier.

Your network isn't about collecting connections.

It's about:

 ❌ How many people you know
 ❌ How many business cards you have
 ❌ How many followers you have

It's actually about:

 ✅ Who you've helped
 ✅ Who trusts your work
 ✅ Who would vouch for you

I spent my first year trying to "network" by reaching out to strangers.

Cold messages.
Generic requests.
Silence.

Then I changed approach.

I started sharing what I was learning.
Helping in communities.
Building in public.

Slowly, people started reaching out to me.

Not because I asked.
But because they saw my work.

Build good things.
Share them.
Help others.

The network follows.

#Career #Advice #Networking #Tech
```

### Example 5: Tool Choice
``
Hackathon 2 is here.
And I'm seeing the same issue everywhere.

People aren't stuck on ideas.
They're stuck on free API limits and errors.

- Keys expiring.
- Requests failing.
- Context getting lost mid-build.

That's frustrating, especially during a hackathon.

If you're using Claude Code, here's a simple fix that's actually working:

Instead of juggling free keys, use GLM-4.7 on the $3 coding plan.

What you get for $3:
 • Stable usage (no random shutdowns)
 • Solid coding help inside Claude Code
 • Enough limits to focus on building, not retrying requests

Setup is straightforward:
 • Buy the plan
 • Get the API key
 • Plug it into Claude Code
 • Done

That's it.

- No key-swapping.
- No stress mid-hackathon.
- Just build.

If you truly can't spend anything, free options are fine.

But if Hackathon 2 matters to you, this small upgrade saves real time.

Let's focus on shipping projects, not fighting APIs.

#Hackathon2 #ClaudeCode #Developers #BuildInPublic
```

## Authentic Voice Patterns (From Real Posts)

### Sentence Structure
- **Very short** - often 2-5 words per line
- **One thought per line** - lots of vertical space
- **Fragments work** - "But then—something happened."
- **Repeat for emphasis** - "Always." (standalone line)

### Emotional Arc
1. **Doubt/Hesitation** - "I held back", "I wasn't sure"
2. **Turning Point** - "But then something happened"
3. **Action** - "So I hit record"
4. **Result** - What happened
5. **Reflection** - What you'd tell others

### Formatting Rules
- Use emoji bullets for lists: 👉 ❌ ✅ 👇
- Use emoji sparingly: 1-2 impactful ones
- Space between EVERY section
- Hashtags at the end (5-6 relevant)

### Tone Markers
| Authentic | Generic (Avoid) |
|-----------|-----------------|
| "I'm usually the quiet type" | "I'm a visionary leader" |
| "Not polished. Not scripted." | "Revolutionary content" |
| "That's it." | "Game-changing solution" |
| "Let's focus on X" | "This will transform everything" |

## Checklist

Every advice post must include:

- [ ] Clear observation or situation
- [ ] Common mistake you see
- [ ] What actually works (your approach)
- [ ] Specific example or numbered steps
- [ ] Why this is better
- [ ] Optional: personal note or vulnerability
- [ ] 5-6 relevant hashtags

## Platform Variations

### LinkedIn (up to 1300 chars)
- Generous spacing between paragraphs
- Use emoji bullets for lists
- 1-2 impactful emojis total
- End with hashtags

### Twitter (thread format for longer)
```
1/ A small tip for learners 👇

Stop wasting time changing free API keys.
It breaks your flow.

If you can afford $3, get a paid plan.
If not, it's okay.

Let's build things, not fix keys.

#AI #Coding

2/ Here's how I set up GLM:

1. Buy the plan
2. Get API key
3. Add to settings.json
4. Done

That's it.

No more key-swapping.
Just building.
```

### WhatsApp (brief advice)
```
Quick tip: If you're coding daily, the $3 GLM plan saves you
constant API key headaches. Worth it if you can afford it.
```

## Prompt Examples

When invoking the skill, describe:

1. **Observation** - What you're noticing
2. **Problem** - Common mistake you see
3. **Solution** - What actually works
4. **Example** - Specific steps or details
5. **Personal note** (optional) - Vulnerability or experience

Example prompt:
```
"Write an advice post about using paid API keys instead of
free ones during hackathons. Problem: keys expiring mid-build.
Solution: $3 GLM plan. Personal note: I use it and it works.
LinkedIn post with my authentic style."
```

---

**Template Version**: 1.0.0
**Last Updated**: 2025-01-28
**Based On**: Authentic user voice and patterns
