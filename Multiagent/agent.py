import os
import sys
import json
import psycopg
from typing import Dict, Any, Optional

# --- ADK imports ---
from google.adk.agents import LlmAgent
from google.adk.agents import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.genai import types as genai_types

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash-lite") # Any supported model string works.

planner_agent = Agent(
name="SqlPlanner",
model=MODEL,
description="Creates a structured plan to translate a question into SQL.",
instruction="""
You are a SQL planning assistant. Given a user's question, produce a concise JSON plan
describing how to build a single, safe, read-only SELECT query.

Return ONLY valid JSON 
""",
output_key="sql_plan",
generate_content_config=genai_types.GenerateContentConfig(temperature=0.1, max_output_tokens=700),
)

executor_agent = Agent(
name="SqlExecutor",
model=MODEL,
description="Generates SQL from a plan and executes it on PostgreSQL using a tool.",
instruction="""
You are a SQL generator and executor.

INPUT PLAN (JSON):
{sql_plan?}

TASK:
From the plan, craft exactly ONE read-only SQL SELECT statement
""",
# tools=[run_postgres_sql],
output_key="query_result",
generate_content_config=genai_types.GenerateContentConfig(temperature=0.1, max_output_tokens=1200),
)

root_agent = SequentialAgent(
name="SqlPipeline",
sub_agents=[planner_agent, executor_agent],
)

root_agent