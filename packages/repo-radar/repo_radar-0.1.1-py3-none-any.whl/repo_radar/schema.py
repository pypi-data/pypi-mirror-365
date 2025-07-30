from repo_radar.schemas.tools import GetLargePRsInput, GetStaleOrLongLivedPRsInput
from typing import List, Dict

def pydantic_schema_to_tool(name: str, description: str, model) -> Dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": model.schema()
        }
    }

def get_tool_schemas() -> List:
    return [
        pydantic_schema_to_tool(
            name="get_large_prs",
            description="Get PRs (open and/or closed) with large number of changed files.",
            model=GetLargePRsInput
        ),
        pydantic_schema_to_tool(
            name="get_stale_or_long_lived_prs",
            description="Get PRs that were open for too long or are still open.",
            model=GetStaleOrLongLivedPRsInput
        )
    ]
