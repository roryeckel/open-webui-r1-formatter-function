"""
title: R1 Formatter
author: ex0dus
author_url: https://github.com/roryeckel/open-webui-r1-formatter-function
version: 0.0.1
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

    def __init__(self):
        self.valves = self.Valves()

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        messages = body.get("messages", [])

        if not messages:
            return body

        for message in messages:
            content = message.get("content", "")

            # Find all <thinking>...</thinking> segments
            formatted_content = self.format_thinking_tags(content)

            # Modify the content with formatted thinking tags
            message["content"] = formatted_content

        body["messages"] = messages
        return body

    def format_thinking_tags(self, text: str) -> str:
        # Regular expression to find <THINK_XML_TAG>...</THINK_XML_TAG> segments
        pattern = r"<{}>(.*?)</{}>".format(
            self.valves.THINK_XML_TAG, self.valves.THINK_XML_TAG
        )

        # Function to replace each found segment with formatted markdown
        def replacer(match):
            thinking_content = match.group(1)
            # Split content into lines and prefix each line with >
            formatted_lines = [f"> {line}" for line in thinking_content.splitlines()]
            return "\n".join(formatted_lines)

        # Replace all occurrences using the regex pattern
        formatted_text = re.sub(pattern, replacer, text, flags=re.DOTALL)

        return formatted_text
