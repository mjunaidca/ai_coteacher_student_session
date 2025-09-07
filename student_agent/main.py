import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, ModelSettings, SQLiteSession
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from openai.types.shared import Reasoning

from prompt import STUDY_MODE_V2

_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


async def main():
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
    async with MCPServerStreamableHttp(params=mcp_params, name="MCP_STUDENT_TOOLBOX", cache_tools_list=False) as mcp_server_client:
        try:

            session = SQLiteSession(session_id="mjunaid_ca")

            await session.clear_session()

            study_assistant = Agent(
                name="Study Mode Teacher Co-Assistant",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
                instructions=STUDY_MODE_V2.format(user_id="mjunaid_ca", course_id="AI-101", auth_token="1234567890", co_teacher_name="Muhammad", assistant_name="KevinAI"),
                model_settings=ModelSettings(temperature=1, reasoning=Reasoning(effort="high")),
            )
            
            result = await Runner.run(study_assistant, "hello", session=session)
            print(f"\n\n[AGENT]: {result.final_output}")

            while True:
                user_input = input("[USER]: ")
                if user_input == "exit":
                    break
                result = await Runner.run(study_assistant, user_input, session=session)
                print(f"\n\n[AGENT]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")

if __name__ == "__main__":
    asyncio.run(main())