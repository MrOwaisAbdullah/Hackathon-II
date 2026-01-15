"""System prompts and language detection for TeamFlow AI Assistant.

This module provides:
- Base system prompt for the "TeamFlow Assistant" AI agent
- Language detection helpers (English vs Urdu)
- Context-aware prompt construction
"""
from typing import Literal, Optional


# Language types supported
Language = Literal["en", "ur"]


# Language detection threshold
URDU_CHARACTER_THRESHOLD = 0.3  # 30% Urdu characters trigger Urdu mode


def detect_language(text: str) -> Language:
    """
    Detect if text is primarily Urdu or English using character-based heuristic.

    Urdu Unicode range: U+0600 to U+06FF (Arabic/Persian script)
    This includes common Urdu characters.

    Args:
        text: Input text to analyze

    Returns:
        "ur" if Urdu characters exceed threshold, "en" otherwise
    """
    if not text:
        return "en"

    # Count Urdu characters (Arabic script range)
    urdu_char_count = 0
    total_chars = 0

    for char in text:
        # Check if character is in Arabic script range (used for Urdu)
        if '\u0600' <= char <= '\u06FF':
            urdu_char_count += 1
        # Skip whitespace and punctuation for total count
        if char.isalnum():
            total_chars += 1

    if total_chars == 0:
        return "en"

    urdu_ratio = urdu_char_count / total_chars
    return "ur" if urdu_ratio >= URDU_CHARACTER_THRESHOLD else "en"


def get_base_system_prompt(language: Language = "en") -> str:
    """
    Get the base system prompt for TeamFlow Assistant.

    Args:
        language: Target language ("en" or "ur")

    Returns:
        System prompt string
    """
    if language == "ur":
        return _get_urdu_system_prompt()
    return _get_english_system_prompt()


def _get_english_system_prompt() -> str:
    """English system prompt for TeamFlow Assistant."""
    return """You are the TeamFlow Assistant, an action-oriented project management AI. EXECUTE tasks directly.

**CRITICAL: Extract task info from user message - NEVER ask for title if user provided a description**

**Information Extraction Rules:**
- User says "create a task for creating a new website" → Extract title: "Create a new website"
- User says "task for building a mobile app" → Extract title: "Build a mobile app"
- User says "deadline 1 week" → Calculate date from today
- User says "assign to owais" → Use assignee: "Owais"
- ONLY ask for title if message is COMPLETELY empty like "create a task" with no details

**Action-First Behavior:**
- When user asks to create/assign/complete tasks → Extract info from message, execute immediately
- Be concise: "✅ Task created" not "I'll help you..."
- Confirm ONLY before delete/archive operations

**Tools Available:**
- add_task(), assign_task(), complete_task(), list_tasks()
- suggest_assignee(), get_profitability(), workload_summary()

**Defaults:**
- Tasks: priority=MEDIUM, status=TODO, no assignee/deadline if unspecified
- Execute actions without asking for optional details

DO NOT provide welcome messages or list capabilities unless asked."""


def _get_urdu_system_prompt() -> str:
    """Urdu system prompt for TeamFlow Assistant (Roman script)."""
    return """Aap TeamFlow Assistant hain, action-oriented project management AI. Tasks ko directly execute karein.

**CRITICAL: User message se task info extract karein - Agar user ne description di hai to title kabhi mat poochein**

**Information Extraction Rules:**
- User kehta hai "create a task for creating a new website" → Title extract karein: "Create a new website"
- User kehta hai "task for building a mobile app" → Title extract karein: "Build a mobile app"
- User kehta hai "deadline 1 week" → Aaj se date calculate karein
- User kehta hai "assign to owais" → Assignee use karein: "Owais"
- Sirf tab title poochein jab message bilkul khaali ho jaise "create a task" koi details ke bina

**Action-First Behavior:**
- Jab user create/assign/complete tasks mange → Message se info extract karein, immediately execute karein
- Concise rahein: "✅ Task banaya" not "Main madad karunga..."
- Sirf delete/archive se pehle confirm karein

**Tools Available:**
- add_task(), assign_task(), complete_task(), list_tasks()
- suggest_assignee(), get_profitability(), workload_summary()

**Defaults:**
- Tasks: priority=MEDIUM, status=TODO, agar assignee/deadline specify na ho to mat lagayein
- Actions ko optional details poochein bina execute karein

Welcome messages ya capabilities list mat dein jab tak specifically na poocha jaye."""


def build_context_prompt(
    user_message: str,
    conversation_history: Optional[list[dict]] = None,
    language_override: Optional[Language] = None,
) -> str:
    """
    Build a complete context prompt including conversation history.

    Args:
        user_message: The current user message
        conversation_history: Previous messages in the conversation
        language_override: Force a specific language (auto-detect if None)

    Returns:
        Complete prompt string with history context
    """
    # Detect language unless overridden
    language = language_override or detect_language(user_message)
    system_prompt = get_base_system_prompt(language)

    # Add conversation history context if available
    if conversation_history and len(conversation_history) > 0:
        history_context = "\n\n**Recent Conversation Context**\n"
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                if role == "user":
                    history_context += f"User: {content}\n"
                else:
                    history_context += f"Assistant: {content}\n"
        system_prompt += history_context

    system_prompt += f"\n\n**Current User Message**\n{user_message}"

    return system_prompt
