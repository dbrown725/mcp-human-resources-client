from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
import logfire
from dotenv import load_dotenv
import logging
import servers as servers
import Tools.tools as tools
import os
from logging_config import configure_app_logging

# Load environment variables from .env file
load_dotenv()

configure_app_logging()

logger = logging.getLogger("mcp_human_resources_client_agent")


def _log_preview(text: str, max_chars: int = 120) -> str:
    if text is None:
        return ""
    sanitized = text.replace("\n", "\\n").replace("\r", "")
    return sanitized[:max_chars]

load_dotenv()
#logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.configure()

try:
    # model = OpenAIChatModel(
    #     'moonshotai/kimi-k2.5', #  x-ai/grok-4-fast moonshotai/kimi-k2.5
    #     provider=OpenRouterProvider(api_key=os.getenv('OPENROUTER_API_KEY')),
    # )

    model = GoogleModel(
        'gemini-3-flash-preview', #  gemini-3-pro-preview gemini-2.5-flash 
        provider=GoogleProvider(api_key=os.getenv('GEMINI_API_KEY'))
    )
    
    agent = Agent(model, 
        instrument=True,
        retries=3,
        tools=[tools.add, tools.get_geo_location, tools.upload_file_to_cloud, 
            tools.download_file_from_cloud, tools.summarize_images_in_folder, tools.create_expense_report,
            tools.create_employee_badge, tools.onboard_new_employee,
            tools.query_company_policies_tool, tools.save_draft_email_new], #, tools.save_draft_email_local_files
        system_prompt=(
            ' You are an assistant who answers all questions. '
        ),
        toolsets=[servers.playwright_mcp_server, servers.mcp_human_resources_server, servers.filesystem_mcp_server])

except Exception as e:
    logger.error(f"Failed to create agent: {e}")
    print(f"\n Error: Failed to create agent: {e}")

async def main():
    async with agent:
        initial_prompt = 'Introduce yourself and list all tools/functions separated into a category-based layout with each category title having a category speific icon' \
        'Note that all prompts which reference a local file or directory should be assumed relative to the allowed directory: ' + os.getenv('LOCAL_FILE_STORAGE')

        logger.info("Before agent.run()")
        result = await agent.run(initial_prompt)
        output_text = str(result.output)
        logger.info(
            "Initial run completed (output_length=%d, preview='%s')",
            len(output_text),
            _log_preview(output_text),
        )
        
        while True:
            try:
                print(f"\n {result.output}")
                user_input = input("\n> ")
                logger.info(
                    "User input received (length=%d, preview='%s')",
                    len(user_input),
                    _log_preview(user_input),
                )
                user_input = user_input.strip()
                if(user_input == "NEW_CHAT"):
                    result = await agent.run("Display: 'Message history cleared, a new chat session has now started.'",message_history="")
                elif(user_input == "KEEP_ALIVE"):
                    logger.info("KEEP_ALIVE command received")
                    result = await agent.run("Execute Keep Alive command one time only, do not repeat this command again.",)
                else:
                    result = await agent.run(user_input, 
                                            message_history=result.new_messages())
            except (EOFError, KeyboardInterrupt):
                logger.info("Input stream closed or interrupted, exiting.")
                break
            except Exception as e:
                logger.error(f"Failed while agent.run: {e}")
                print(f"\n Error: Failed while agent.run: {str(e)[:150]}...")
                break          
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())