import re

from typing import Optional, Any
from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)
from notionary.blocks.shared.models import RichTextObject


class CodeElement(NotionBlockElement):
    """
    Handles conversion between Markdown code blocks and Notion code blocks.

    Markdown code block syntax:
    ```language
    code content
    ```
    Caption: optional caption text

    Where:
    - language is optional and specifies the programming language
    - code content is the code to be displayed
    - Caption line is optional and must appear immediately after the closing ```
    """

    PATTERN = re.compile(
        r"```(\w*)\n([\s\S]+?)```(?:\n(?:Caption|caption):\s*(.+))?", re.MULTILINE
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text contains a markdown code block."""
        return bool(cls.PATTERN.search(text))

    @classmethod
    def match_notion(cls, block: dict[str, any]) -> bool:
        """Check if block is a Notion code block."""
        return block.get("type") == "code"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown code block to Notion code block."""
        match = cls.PATTERN.search(text)
        if not match:
            return None

        language = match.group(1) or "plain text"
        content = match.group(2)
        caption = match.group(3)

        if content.endswith("\n"):
            content = content[:-1]

        # Create code block with rich text
        content_rich_text = RichTextObject.from_plain_text(content)

        block = {
            "type": "code",
            "code": {
                "rich_text": [content_rich_text.model_dump()],
                "language": language,
            },
        }

        # Add caption if provided
        if caption and caption.strip():
            caption_rich_text = RichTextObject.from_plain_text(caption.strip())
            block["code"]["caption"] = [caption_rich_text.model_dump()]

        # Leerer Paragraph nach dem Code-Block
        empty_paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}

        return [block, empty_paragraph]

    @classmethod
    def notion_to_markdown(cls, block: dict[str, Any]) -> Optional[str]:
        """Convert Notion code block to Markdown."""
        if block.get("type") != "code":
            return None

        code_data = block.get("code", {})
        language = code_data.get("language", "")
        rich_text = code_data.get("rich_text", [])
        caption = code_data.get("caption", [])

        def extract_content(rich_text_list):
            """Extract code content from rich_text array."""
            return "".join(
                text.get("text", {}).get("content", "")
                if text.get("type") == "text"
                else text.get("plain_text", "")
                for text in rich_text_list
            )

        def extract_caption(caption_list):
            """Extract caption text from caption array."""
            return "".join(
                c.get("text", {}).get("content", "")
                for c in caption_list
                if c.get("type") == "text"
            )

        code_content = extract_content(rich_text)
        caption_text = extract_caption(caption)

        # Handle language - convert "plain text" back to empty string for markdown
        if language == "plain text":
            language = ""

        # Build markdown code block
        result = f"```{language}\n{code_content}\n```" if language else f"```\n{code_content}\n```"

        # Add caption if present
        if caption_text:
            result += f"\nCaption: {caption_text}"

        return result

    @classmethod
    def find_matches(cls, text: str) -> list[tuple[int, int, dict[str, any]]]:
        """
        Find all code block matches in the text and return their positions.

        Args:
            text: The text to search in

        Returns:
            List of tuples with (start_pos, end_pos, block)
        """
        matches = []
        for match in CodeElement.PATTERN.finditer(text):
            language = match.group(1) or "plain text"
            content = match.group(2)
            caption = match.group(3)

            # Remove trailing newline if present
            if content.endswith("\n"):
                content = content[:-1]

            block = {
                "type": "code",
                "code": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content},
                            "plain_text": content,
                        }
                    ],
                    "language": language,
                },
            }

            # Add caption if provided
            if caption and caption.strip():
                block["code"]["caption"] = [
                    {
                        "type": "text",
                        "text": {"content": caption.strip()},
                        "plain_text": caption.strip(),
                    }
                ]

            matches.append((match.start(), match.end(), block))

        return matches

    @classmethod
    def is_multiline(cls) -> bool:
        return True

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the code block element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Use fenced code blocks to format content as code. Supports language annotations like "
                "'python', 'json', or 'mermaid'. Useful for displaying code, configurations, command-line "
                "examples, or diagram syntax. Also suitable for explaining or visualizing systems with diagram languages. "
                "Code blocks can include optional captions for better documentation."
            )
            .with_usage_guidelines(
                "Use code blocks when you want to present technical content like code snippets, terminal commands, "
                "JSON structures, or system diagrams. Especially helpful when structure and formatting are essential. "
                "Add captions to provide context, explanations, or titles for your code blocks."
            )
            .with_syntax(
                "```language\ncode content\n```\nCaption: optional caption text\n\n"
                "OR\n\n"
                "```language\ncode content\n```"
            )
            .with_examples(
                [
                    "```python\nprint('Hello, world!')\n```\nCaption: Basic Python greeting example",
                    '```json\n{"name": "Alice", "age": 30}\n```\nCaption: User data structure',
                    "```mermaid\nflowchart TD\n  A --> B\n```\nCaption: Simple flow diagram",
                    '```bash\ngit commit -m "Initial commit"\n```',
                ]
            )
            .with_avoidance_guidelines(
                "NEVER EVER wrap markdown content with ```markdown. Markdown should be written directly without code block formatting. "
                "NEVER use ```markdown under any circumstances. "
                "For Mermaid diagrams, use ONLY the default styling without colors, backgrounds, or custom styling attributes. "
                "Keep Mermaid diagrams simple and minimal without any styling or color modifications. "
                "Captions must appear immediately after the closing ``` on a new line starting with 'Caption:' - "
                "no empty lines between the code block and the caption."
            )
            .build()
        )

    @staticmethod
    def extract_content(rich_text_list: list[dict[str, Any]]) -> str:
        """Extract code content from rich_text array."""
        return "".join(
            text.get("text", {}).get("content", "")
            if text.get("type") == "text"
            else text.get("plain_text", "")
            for text in rich_text_list
        )

    @staticmethod
    def extract_caption(caption_list: list[dict[str, Any]]) -> str:
        """Extract caption text from caption array."""
        return "".join(
            c.get("text", {}).get("content", "")
            for c in caption_list
            if c.get("type") == "text"
        )