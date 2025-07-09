import eel
import subprocess
import threading
import logging
import re
# Configure logging
logging.basicConfig(
    filename='/var/log/mcp-human-resources-client/mcp-human-resources-client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logging.info("Starting eel.init('web')")
# Initialize the Eel application
eel.init('web')

# Global variable to hold the subprocess
process = None

def start_subprocess():
    logging.info("start_subprocess")
    global process
    # Start the subprocess
    process = subprocess.Popen(['python', 'mcp_spring_weather.py'], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               universal_newlines=True)
    # Read output in a separate thread to avoid blocking
    def read_output():
        logging.info("read_output")
        while True:
            output = process.stdout.readline()
            if output:
                # Filtered output without newline for non-matching lines
                filtered_lines = [line for line in output.strip().split('\n') 
                    if not re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}', line.strip())]

                # If no lines match the filter or if the output starts with '>', skip it
                if not filtered_lines or output.strip().startswith('>'):
                    continue

                # Join the filtered lines with newline
                filtered_output = '\n'.join(filtered_lines)
                eel.displayOutput(filtered_output)

            poll_value = process.poll()
            if poll_value is not None:
                logging.error("Subprocess failed polling check with value: " + str(poll_value) )
                eel.displayOutput("Error: Subprocess failed polling check with value: " + str(poll_value) + '\n')
                break
    threading.Thread(target=read_output).start()

@eel.expose
def send_input(user_input):
    global process
    if process:
        try:
            process.stdin.write(user_input + '\n')
            eel.displayOutput("Your input: " + user_input + '\n')
            process.stdin.flush()
            logging.info("after process.stdin.flush()")
        except Exception as e:
            logging.error("exception caught", e)
            eel.displayOutput(f"Error: {str(e)}")

@eel.expose
def start_process():
    logging.info("Before start_subprocess()")
    start_subprocess()

# Start the Eel application
eel.start('index.html', mode="Chrome", size=(600, 400))