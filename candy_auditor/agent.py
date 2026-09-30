"""Agent for Trick-or-Treat House & Candy Bowl Auditing."""

import os
import dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools import FunctionTool
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

try:
    from .tools.bowl_tool import get_porch_candy_data
    from .tools.preference_tool import get_kid_trade_index
except ImportError:
    from tools.bowl_tool import get_porch_candy_data
    from tools.preference_tool import get_kid_trade_index

dotenv.load_dotenv()

# --- Config Initialization ---
MODEL = os.environ.get("MODEL", "gemini-3.8-flash")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

# --- Tool & Skill Toolset Initialization ---
bowl_tool = FunctionTool(func=get_porch_candy_data)
trade_tool = FunctionTool(func=get_kid_trade_index)

skills_dir = os.path.join(os.path.dirname(__file__), "skills")
porch_tier_skill = load_skill_from_dir(os.path.join(skills_dir, "analyze-porch-tier"))
candy_value_skill = load_skill_from_dir(os.path.join(skills_dir, "analyze-candy-value"))
allergen_safety_skill = load_skill_from_dir(os.path.join(skills_dir, "analyze-allergen-safety"))

skill_toolset = SkillToolset(
    skills=[porch_tier_skill, candy_value_skill, allergen_safety_skill],
    additional_tools=[bowl_tool, trade_tool],
)

SYSTEM_INSTRUCTION = """You are the Official Trick-or-Treat Candy Sommelier & House Auditor Agent for the Neighborhood Halloween Guild.
Your task is to draft a comprehensive Halloween House Candy Audit Memorandum when the user provides a house ID (e.g., HOUSE-1031).

You have been equipped with specialized investigation skills in your SkillToolset (`analyze-porch-tier`, `analyze-candy-value`, `analyze-allergen-safety`).
Always load and follow ALL THREE of your skills (`analyze-porch-tier`, `analyze-candy-value`, `analyze-allergen-safety`) before drafting your report.

When drafting the final audit memorandum, you MUST strictly format your response using the following standard structure:

# Trick-or-Treat House Audit Memorandum: [House ID]

## Executive Porch Summary
Provide a festive, high-level summary of the house, its primary candy offering, and overall Trick-or-Treat appeal.

## Porch Summary & Candy Tier Rating
Summarize the exact House ID, candy name, size class, wrapper integrity, Guild Tier, and street trade ratio.

## Confectionery Economics & Unit Value
Detail the financial profile of the candy bowl strictly according to your `analyze-candy-value` skill.

## Allergen & Cross-Contamination Safety
Detail the allergen safety profile of the porch strictly according to your `analyze-allergen-safety` skill.

## Official Trick-or-Treat Verdict
Conclude with a clear route recommendation (e.g., Must-Visit Golden Pumpkin Stop, Proceed with Caution, or Skip House).
"""

# --- Trick-or-Treat Candy Auditor Agent ---
candy_auditor_agent = Agent(
    name="candy_auditor_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[skill_toolset],
)

app = App(
    name="candy_auditor",
    root_agent=candy_auditor_agent,
)
