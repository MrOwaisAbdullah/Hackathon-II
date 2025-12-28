---
id: 003
title: Upgrade social-media-writer skill to v2.0 with top creator research
stage: misc
date: 2025-01-28
surface: agent
model: glm-4.7
feature: none
branch: 001-console-task-distribution
user: owais
command: User provided additional guidelines and requested internet research on top LinkedIn creators to improve the skill: "now use the internet visit, top content creators on linkedin there posts, advices for writing good length, and improve the skill, also here is some other advices for you..."
labels: [skill-improvement, social-media, research-based, v2-upgrade]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/skills/social-media-writer/SKILL.md
 - .claude/skills/social-media-writer/lessons/WRITING_CHECKLIST.md
 - .claude/skills/social-media-writer/scripts/validator.py
tests: []
---

## Prompt

User requested improvements to the social-media-writer skill based on:

1. **Internet research** on top LinkedIn creators' post length and writing advice
2. **Additional guidelines**:
   - Use very simple English (non-native friendly)
   - Expand concepts when not clear
   - No banned words
   - Start with one-liner hook
   - Make posts scannable (max 3 lines per paragraph, white space after each line, numbers/arrows)
   - Limit emojis (not too many)
   - Keep posts between 700-1000 characters
   - Include CTA with questions/prompts

Research conducted on:
- LinkedIn optimal post length (900-1200 chars, but user preferred 700-1000)
- Top creator structures (Justin Welsh 5-step, Aisha Riaz Problem-Process-Outcome-Lesson)
- Sentence length impact (<12 words performs 20% better)
- Scannability best practices

## Response Summary

Upgraded `social-media-writer` skill to v2.0 with research-backed improvements from top LinkedIn creators.

**Research Findings:**
- Justin Welsh: 5-step formula (Hook → Setup → Value Bomb → Takeaway → CTA), 162M+ impressions
- Aisha Riaz: Problem → Process → Outcome → Lesson structure
- AuthoredUp stats: Sentences under 12 words perform 20% better
- LinkedIn marketing: 900-1200 chars optimal, 700-1000 sweet spot per user
- "See More" cutoff at ~140 characters makes hook critical

**Key Changes in v2.0:**

### 1. SKILL.md Updates
- Added **Simple English principle** (non-native friendly)
- Added **Optimal length table** (700-1000 LinkedIn, 200-270 Twitter)
- Added **Scannability Rules section** with good/bad examples
- Added **4 viral post structures** from top creators
- Updated examples to follow new guidelines

### 2. WRITING_CHECKLIST.md Overhaul
- Added **Hook Validation section** (one-liner check, <12 words)
- Added **Simple English Check** (avoid complex words)
- Updated sentence length to **max 15 words** (strict: <12 performs better)
- Added **Scannability Rules** (max 3 lines per paragraph, white space)
- Added **CTA Validation** (required, not optional)
- Added **Viral Structure Validation** (must use one of 4 structures)
- Updated optimal ranges table

### 3. validator.py Enhancements
New validation functions:
- `validate_hook()`: Checks first line is strong hook, detects weak patterns
- `validate_scannability()`: Max 3 lines per paragraph, wall of text detection
- `validate_cta()`: Ensures CTA present at end
- `validate_simple_english()`: Flags complex words (utilize → use, etc.)

Updated existing functions:
- `validate_sentence_length()`: Stricter (max 15, <10 optimal, <12 performs 20% better)
- `validate_emojis()`: Reduced limits (2 LinkedIn, 1 Twitter)
- `validate_length()`: Added optimal range warnings (700-1000 LinkedIn)

## Key New Rules

| Rule | Old | New (v2.0) |
|------|-----|-----------|
| LinkedIn length | Up to 1300 | 700-1000 optimal |
| Sentence length | Max 25 words | Max 15 words (<12 optimal) |
| Emojis (LinkedIn) | Max 3 | Max 2 |
| Paragraph lines | Not specified | Max 3 lines |
| Hook | Not required | Required, first line |
| CTA | Optional | Required |
| Simple English | Not checked | Validated |

## Research Sources Cited

- Justin Welsh: 5-step copywriting formula, 162M+ impressions
- Aisha Riaz: Problem → Process → Outcome → Lesson structure
- LinkedIn Marketing research: 900-1200 chars optimal reach
- AuthoredUp statistics: Short sentences (<12 words) perform 20% better
- Top creator analysis: Hook-first, scannable format wins

## Outcome

- **Impact**: Skill now produces posts that follow proven viral structures from top creators
- **Version bump**: 1.0.0 → 2.0.0
- **Files modified**: 3 core files (SKILL.md, WRITING_CHECKLIST.md, validator.py)
- **New validations**: Hook, scannability, CTA, simple English
- **Stricter limits**: Sentence length (25→15), emojis (3→2 LinkedIn), optimal length targeting
- **Research-backed**: All changes based on analysis of top performing posts

## Evaluation Notes

- Research sources are credible (Justin Welsh 162M+ impressions, AuthoredUp data)
- User's 700-1000 char preference aligns with mobile reading patterns
- Simple English requirement expands accessibility to non-native speakers
- Hook-first approach aligns with "See More" cutoff (~140 chars on LinkedIn)
- Max 3 lines per paragraph is critical for mobile (70%+ LinkedIn traffic)

---

**Version**: 2.0.0
**Skill Path**: `.claude/skills/social-media-writer/`
**Research Based On**: Justin Welsh, Aisha Riaz, LinkedIn Marketing, AuthoredUp
**User Guidelines**: Simple English, scannable format, hook-first, CTA required
