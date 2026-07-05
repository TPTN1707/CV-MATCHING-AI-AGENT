"""Initialize and configure the LangChain agent for the resume matching system."""

import asyncio
import logging

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from hr_agent_tools import search_jobs
from hr_agent_format import MatchResponse

load_dotenv()

logger = logging.getLogger(__name__)

# System prompt instructing the agent to behave as a Career Coach
_SYSTEM_INSTRUCTION = (
    "You act as a seasoned talent advisor with deep knowledge of hiring practices.\n"
    "Your mission is to match a candidate's profile against available positions in the database.\n\n"
    "Follow these steps:\n"
    "1. Review the candidate's background, skills, and experience from their resume.\n"
    "2. Use the `search_jobs` tool to query relevant openings. Run multiple searches with different keywords if necessary.\n"
    "3. Compare each returned position against the candidate's strengths and gaps.\n"
    "4. Pick the 3 strongest matches overall.\n"
    "5. For each match, you MUST provide ALL of these fields:\n"
    "   - job_id: the job posting ID\n"
    "   - job_title: position title\n"
    "   - job_url: the source URL of the posting\n"
    "   - match_score: integer 0-100\n"
    "   - strengths: list of candidate strengths matching this role\n"
    "   - reasoning: a single string explaining WHY this job is a good fit (DO NOT skip this field)\n"
    "   - missing_skills: list of skills the candidate lacks for this role\n"
    "   - improvement_tips: a single string with actionable advice (NOT a list)\n\n"
    "CRITICAL: The 'reasoning' field must be a non-empty string. "
    "The 'improvement_tips' field must be a single string, NOT a list.\n"
)

# LLM configuration
_LLM_MODEL = "gemini-2.5-flash"
_LLM_TEMPERATURE = 0

def _build_llm() -> ChatGoogleGenerativeAI:
    """Create a ChatGoogleGenerativeAI instance with the predefined configuration."""
    return ChatGoogleGenerativeAI(model=_LLM_MODEL, temperature=_LLM_TEMPERATURE)



def get_agent():
    """Create and return a fully configured Career Coach agent."""
    llm = _build_llm()

    agent = create_agent(
        model=llm,
        tools=[search_jobs],
        system_prompt=_SYSTEM_INSTRUCTION,
        response_format=ToolStrategy(MatchResponse),
    )
    return agent


async def _run_demo():
    """Run the agent with a sample resume for demonstration."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Initializing agent...")

    agent = get_agent()

    # Sample resume for testing
    sample_resume = (
        "John Doe\n"
        "Senior Software Engineer\n"
        "Skills: Python, AWS, Docker, Kubernetes, FastAPI, React\n"
        "Experience: 5 years building cloud-native applications.\n"
    )

    logger.info("Sending sample resume to the agent for processing...")
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": f"Here is my resume:\n{sample_resume}"}]
    })

    # Parse the structured response
    structured_data: MatchResponse = result["structured_response"]

    print(f"\nFound {len(structured_data.matches)} matching results:\n")
    for match in structured_data.matches:
        print(f"  {match.job_title} (Score: {match.match_score}/100)")
        print(f"    Reason: {match.reasoning}")
        print(f"    Strengths: {', '.join(match.strengths)}")
        print(f"    Missing skills: {', '.join(match.missing_skills)}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(_run_demo())