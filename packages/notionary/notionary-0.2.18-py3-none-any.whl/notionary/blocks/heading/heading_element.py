import re
from typing import Dict, Any, Optional

from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


class HeadingElement(NotionBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""

    # Pattern: #, ## oder ###, dann mind. 1 Leerzeichen/Tab, dann mind. 1 sichtbares Zeichen (kein Whitespace-only)
    PATTERN = re.compile(r"^(#{1,3})[ \t]+(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown heading with non-empty content."""
        match = cls.PATTERN.match(text)
        if not match:
            return False
        content = match.group(2)
        return bool(content.strip())  # Reject headings with only whitespace

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion heading."""
        block_type: str = block.get("type", "")
        return block_type.startswith("heading_") and block_type[-1] in "123"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown heading to Notion heading block with preceding empty paragraph."""
        match = cls.PATTERN.match(text)
        if not match:
            return None

        level = len(match.group(1))
        if not 1 <= level <= 3:
            return None

        content = match.group(2).lstrip()  # Entferne führende Leerzeichen im Content
        if not content.strip():
            return None  # Leerer Inhalt nach Entfernen der Whitespaces

        header_block = {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": TextInlineFormatter.parse_inline_formatting(content)
            },
        }
        return [header_block]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion heading block to markdown heading."""
        block_type = block.get("type", "")

        if not block_type.startswith("heading_"):
            return None

        try:
            level = int(block_type[-1])
            if not 1 <= level <= 3:
                return None
        except ValueError:
            return None

        heading_data = block.get(block_type, {})
        rich_text = heading_data.get("rich_text", [])

        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        prefix = "#" * level
        return f"{prefix} {text}" if text else None

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Use Markdown headings (#, ##, ###) to structure content hierarchically."
            )
            .with_usage_guidelines(
                "Use to group content into sections and define a visual hierarchy."
            )
            .with_avoidance_guidelines(
                "Only H1-H3 syntax is supported. H4 and deeper heading levels are not available."
            )
            .with_standard_markdown()
            .build()
        )
