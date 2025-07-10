# mcp-human-resources-client
Python EEL UI based MCP Host app for Pydantic AI MCP interaction and testing with the mcp-human-resources Spring Boot app.

## Installation
Assumes Linux with the latest python, node and npm

1. Install uv (A fast Python package installer and resolver):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
You may need to close your terminal and open a new one afterwards.
```

2. Clone the repository:

```bash
git clone https://github.com/dbrown725/mcp-human-resources-client.git
cd mcp-human-resources-client
```

3. Create a new virtual environment and activate it:

```bash
uv venv
source .venv/bin/activate
#Later to exit your virtual environment
deactivate
```
4. Install Node module(s):
```bash
npm i @executeautomation/playwright-mcp-server
```

5. Install dependencies:

```bash
uv pip install -r requirements.txt
```

6. Export API Keys for your preferred LLM, tested with GROQ and Google Gemini:

```bash
export GROQ_API_KEY=<YOUR_GROQ_API_KEY>
or
export GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
```

7. If using GMAIL<br>
Email configuration, currently only Save Draft is fully hooked up.<br>
Password in NOT your normal gmail password, the password needs to be an APP password: https://support.google.com/mail/answer/185833?hl=en
```bash
export GMAIL_EMAIL_ADDRESS=<GMAIL_ADDRESSS>
export GMAIL_EMAIL__APP_PASSWORD=<GMAIL_APP_PASSWORD>
```

8. Setup log directory and file
```bash
sudo mkdir /var/log/mcp-human-resources-client
sudo touch /var/log/mcp-human-resources-client/mcp-human-resources-client.log
sudo chmod -R 777 /var/log/mcp-human-resources-client
```

9. Setup Logfire<br>
    Follow Logfire Getting Started instructions: https://logfire.pydantic.dev/docs/

10. If testing against the mcp-human-resources Spring Boot app<br>
    Clone, build and run: https://github.com/dbrown725/mcp-human-resources

11. Update the agent object instantiation in agent.py with specific tools, model and mcp servers you are using.<br><br>
    For instance if you aren't using gmail then:<br>
        tools=[tools.add, tools.saveDraftEmailContent, tools.getGeoLocation],<br>
    changes to<br>
        tools=[tools.add, tools.getGeoLocation], <br><br>
    if you aren't using the mcp-human-resources Spring Boot app then<br>
    mcp_servers=[servers.playwright_mcp_server, servers.mcp_human_resources_server])<br>
    changes to<br>
    mcp_servers=[servers.playwright_mcp_server])<br><br>
    Configure your preferred model, see Pydantic AI guide:<br>
    https://ai.pydantic.dev/models/

12. To Run<br>
        If using mcp_human_resources_server make sure the app is started<br>
        then<br>
        python3 main.py

13. For sample prompts see:<br>
        prompts.txt        