import os
import sys
import eel
import subprocess
import threading
import logging
import re
import time

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

# Global variable to track the last time send_input was executed (user activity)
last_send_input_time = time.time()

# Global variable to track the last time we sent a KEEP_ALIVE
last_keepalive_time = last_send_input_time

# Global timeout in seconds (default 30 minutes)
DEFAULT_KEEP_ALIVE_MINUTES = 30
env_minutes = os.getenv('SESSION_KEEP_ALIVE_MINUTES')

try:
    if env_minutes is None or env_minutes.strip() == "":
        raise ValueError("SESSION_KEEP_ALIVE_MINUTES not set")
    minutes = float(env_minutes)
    if minutes <= 0:
        raise ValueError("SESSION_KEEP_ALIVE_MINUTES must be positive")
    GLOBAL_TIMEOUT_SECONDS = int(minutes * 60)
    logging.info("GLOBAL_TIMEOUT_SECONDS set from SESSION_KEEP_ALIVE_MINUTES: %s minutes (%d seconds)",
                 env_minutes, GLOBAL_TIMEOUT_SECONDS)
except Exception:
    GLOBAL_TIMEOUT_SECONDS = DEFAULT_KEEP_ALIVE_MINUTES * 60
    logging.info("SESSION_KEEP_ALIVE_MINUTES unavailable/invalid; using default GLOBAL_TIMEOUT_SECONDS=%d",
                 GLOBAL_TIMEOUT_SECONDS)

def start_subprocess():
    logging.info("start_subprocess")
    global process
    # Start the subprocess
    process = subprocess.Popen(['python', 'agent.py'],
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
                logging.error("Subprocess failed polling check with value: %s", str(poll_value))
                eel.displayOutput("Error: Subprocess failed polling check with value: " + str(poll_value) + '\n')
                break
    threading.Thread(target=read_output, daemon=True).start()

def stop_thread():
    """
    Terminates subprocess and notifies UI.
    """
    global process
    try:
        if process and process.poll() is None:
            process.terminate()
            logging.info("Terminated subprocess")
            try:
                eel.sessionExpired()
            except Exception:
                logging.exception("Failed to call eel.sessionExpired()")
    except Exception as term_exc:
        logging.error("Error terminating subprocess: %s", term_exc)
    process = None
    try:
        eel.displayOutput("Stopping thread.\n")
    except Exception:
        logging.exception("Failed to call eel.displayOutput() in stop_thread")
    return True

def check_send_input_time():
    """
    Background thread that:
    - Sends KEEP_ALIVE every 2 minutes when no user activity.
    - Does not cap KEEP_ALIVE calls.
    - If no user activity for GLOBAL_TIMEOUT_SECONDS, calls stop_thread() and exits.
    """
    global last_send_input_time
    global last_keepalive_time
    while True:
        time.sleep(10)  # check frequently but enforce intervals below
        elapsed_since_user = time.time() - last_send_input_time

        # If global timeout exceeded, stop and exit
        if elapsed_since_user >= GLOBAL_TIMEOUT_SECONDS:
            logging.error("Global timeout (%d seconds) exceeded (elapsed: %d). Stopping thread and exiting.",
                          GLOBAL_TIMEOUT_SECONDS, int(elapsed_since_user))
            try:
                stop_thread()
            except Exception:
                logging.exception("Exception while stopping thread on global timeout")
            # Ensure process exit
            os._exit(0)

        # If at least 2 minutes since last user activity and at least 2 minutes since last keepalive, send KEEP_ALIVE
        if elapsed_since_user >= 120 and (time.time() - last_keepalive_time) >= 120:
            if process:
                try:
                    process.stdin.write("KEEP_ALIVE\n")
                    process.stdin.flush()
                    last_keepalive_time = time.time()
                    logging.info("KEEP_ALIVE command sent")
                    try:
                        eel.displayOutput("Sent KEEP_ALIVE\n")
                    except Exception:
                        logging.exception("Failed to call eel.displayOutput() after KEEP_ALIVE")
                except Exception as e:
                    logging.error("Exception caught sending KEEP_ALIVE: %s", e)
                    try:
                        eel.displayOutput(f"Error: {str(e)}")
                    except Exception:
                        logging.exception("Failed to call eel.displayOutput() after KEEP_ALIVE exception")
                    # If sending fails, stop the thread/process to avoid endless errors and exit
                    try:
                        stop_thread()
                    except Exception:
                        logging.exception("Exception while stopping thread after KEEP_ALIVE failure")
                    os._exit(0)

# Start the check_send_input_time thread
threading.Thread(target=check_send_input_time, daemon=True).start()

@eel.expose
def send_input(user_input):
    global last_send_input_time
    global process
    # Reset global timeout timer on user request
    last_send_input_time = time.time()
    if process:
        try:
            process.stdin.write(user_input + '\n')
            eel.displayOutput("Your input: " + user_input + '\n')
            process.stdin.flush()
            logging.info("after process.stdin.flush()")
        except Exception as e:
            logging.error("Exception caught while sending user input: %s", e)
            try:
                eel.displayOutput(f"Error: {str(e)}")
            except Exception:
                logging.exception("Failed to call eel.displayOutput() after input exception")

@eel.expose
def start_process():
    logging.info("Before start_subprocess()")
    start_subprocess()

# Start the Eel application
eel.start('index.html', mode="Chrome", size=(600, 400))