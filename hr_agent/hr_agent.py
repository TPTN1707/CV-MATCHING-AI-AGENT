

import asyncio
import logging

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy

from hr_agent_tools import search_jobs
from hr_agent_format import MatchResponse

load_dotenv()

logger = logging.getLogger(__name__)
