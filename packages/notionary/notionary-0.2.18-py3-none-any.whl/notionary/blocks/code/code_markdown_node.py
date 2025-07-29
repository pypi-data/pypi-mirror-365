from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class CodeMarkdownBlockParams(BaseModel):
    code: str
    language: Optional[str] = None
    caption: Optional[str] = None


class CodeMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown code blocks.
    Example:
        ```python
        print("Hello, world!")
        ```
        Caption: Basic usage
    """

    def __init__(
        self,
        code: str,
        language: Optional[str] = None,
        caption: Optional[str] = None,
    ):
        self.code = code
        self.language = language or ""
        self.caption = caption

    @classmethod
    def from_params(cls, params: CodeMarkdownBlockParams) -> CodeMarkdownNode:
        return cls(code=params.code, language=params.language, caption=params.caption)

    def to_markdown(self) -> str:
        lang = self.language or ""
        content = f"```{lang}\n{self.code}\n```"
        if self.caption:
            content += f"\nCaption: {self.caption}"
        return content
