from pydantic_ai import Agent
import logfire
from dotenv import load_dotenv
import logging
import servers as servers
import Tools.tools as tools

# Configure logging
logging.basicConfig(
    filename='/var/log/mcp-human-resources-client/mcp-human-resources-client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("mcp_spring_weather")

load_dotenv()
#logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.configure()

try:
    # agent = Agent('groq:deepseek-r1-distill-llama-70b',
    agent = Agent('groq:moonshotai/kimi-k2-instruct', 
    # agent = Agent('google-gla:gemini-2.5-flash-preview-05-20',    
    # agent = Agent('google-gla:gemini-2.5-flash-preview-06-17',
    # agent = Agent('google-gla:gemini-2.5-flash-lite-preview-06-17',            
    # agent = Agent('google-gla:gemini-2.0-flash', 
                    instrument=True,
                    retries=3,
                    tools=[tools.add, tools.saveDraftEmailContent, tools.getGeoLocation],
                    system_prompt=(
                        ' You are an assistant who answers all questions. '
                    ),
                   mcp_servers=[servers.playwright_mcp_server, servers.mcp_human_resources_server])

except Exception as e:
    logger.error(f"Failed to create agent: {e}")
    print(f"\n Error: Failed to create agent: {e}")

async def main():
    async with agent.run_mcp_servers():
        initial_prompt = 'Introduce yourself and list all tools/functions separated into a category-based layout with each category title having a category speific icon'
        
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