from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
import logfire
from dotenv import load_dotenv
import logging
import servers as servers
import Tools.tools as tools
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='/var/log/mcp-human-resources-client/mcp-human-resources-client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("mcp_human_resources_client_agent")

load_dotenv()
#logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.configure()

try:
    model = OpenAIModel(
        'x-ai/grok-4-fast',
        provider=OpenRouterProvider(api_key=os.getenv('OPENROUTER_API_KEY')),
    )
    
    agent = Agent(model, 
        instrument=True,
        retries=3,
        tools=[tools.add, tools.save_draft_email_content, tools.get_geo_location, tools.upload_file_to_cloud, 
                tools.download_file_from_cloud, tools.summarize_images_in_folder, tools.create_expense_report,
                tools.create_employee_badge, tools.query_employee_code_of_conflict],
        system_prompt=(
            ' You are an assistant who answers all questions. '
        ),
        mcp_servers=[servers.playwright_mcp_server, servers.mcp_human_resources_server, servers.filesystem_mcp_server])

except Exception as e:
    logger.error(f"Failed to create agent: {e}")
    print(f"\n Error: Failed to create agent: {e}")

async def main():
    async with agent.run_mcp_servers():
        initial_prompt = 'Introduce yourself and list all tools/functions separated into a category-based layout with each category title having a category speific icon' \
        'Note that all prompts which reference a local file or directory should be assumed relative to the allowed directory: ' + os.getenv('LOCAL_FILE_STORAGE')

        logger.info("Before agent.run()")
        result = await agent.run(initial_prompt)
        logger.info(f"In Main result: {result.output}")
        
        while True:
            try:
                print(f"\n {result.output}")
                user_input = input("\n> ")
                logger.info(f"User input: {user_input}")
                user_input = user_input.strip()
                if(user_input == "NEW_CHAT"):
                    result = await agent.run("Display: 'Message history cleared, a new chat session has now started.'",message_history="")
                elif(user_input == "KEEP_ALIVE"):
                    logger.info(f"In KEEP_ALIVE, User input: {user_input}")
                    result = await agent.run("Execute Keep Alive command one time only, do not repeat this command again.",)
                else:
                    result = await agent.run(user_input, 
                                            message_history=result.new_messages())
            except Exception as e:
                logger.error(f"Failed while agent.run: {e}")
                print(f"\n Error: Failed while agent.run: {str(e)[:150]}...")
                # raise          
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())