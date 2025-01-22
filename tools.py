"""
title: R1 Formatter
author: ex0dus
author_url: https://github.com/roryeckel/open-webui-r1-formatter-function
version: 0.0.2
"""

from typing import Optional
from pydantic import BaseModel, Field
import re


class Filter:
    class Valves(BaseModel):
        THINK_XML_TAG: str = Field(
            default="think",
            description="The XML tag to use for matching thinking segments.",
        )
        CLICK_TO_EXPAND: bool = Field(
            default=True,
            description="When enabled, the thoughts will be collapsed until clicked to expand. When disabled, thoughts will always be visible in a Markdown quote format.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        messages = body.get("messages", [])

        if not messages:
            return body

        for message in messages:
            content = message.get("content", "")

            # Format thinking segments using details and summary tags
            formatted_content = self.format_thinking_tags(content)
            message["content"] = formatted_content

        body["messages"] = messages
        return body

    def format_thinking_tags(self, text: str) -> str:
        # Regular expression to find <THINK_XML_TAG>...</THINK_XML_TAG> segments
        pattern = r"<{}>(.*?)</{}>".format(
            self.valves.THINK_XML_TAG, self.valves.THINK_XML_TAG
        )

        # Function to replace each found segment with the new format
        def replacer(match):
            thinking_content = match.group(1)

            if (
                not thinking_content
                or not isinstance(thinking_content, str)
                or thinking_content.isspace()
            ):
                return ""

            # Split content into lines and add proper formatting
            split_lines = thinking_content.splitlines()

            # Add "> " to each line for Markdown quote when click to expand is disabled
            if not self.valves.CLICK_TO_EXPAND:
                split_lines = [f"> {line}" for line in split_lines]
            formatted_content = "\n".join(split_lines)

            # Add <details> and <summary> tags if click to expand is enabled
            if self.valves.CLICK_TO_EXPAND:
                return f"<details>\n<summary>Thought</summary>\n{formatted_content}\n</details>"
            else:
                return formatted_content

        # Replace all occurrences using the regex pattern
        formatted_text = re.sub(pattern, replacer, text, flags=re.DOTALL)

        return formatted_text
