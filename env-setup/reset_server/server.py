import argparse
import http.server
import logging
import os
import pathlib
import socketserver
import subprocess
import sys
import threading
import json
import time

print("Starting server...")
print("INSTANCE_NUM in server.py:", os.environ.get("INSTANCE_NUM", "<UNKNOWN>"))
print("CUSTOM_INSTANCE_NUM in server.py:", os.environ.get("CUSTOM_INSTANCE_NUM", "<UNKNOWN>"))
print("CF_TUNNEL_FOR_WEBARENA  in server.py:", os.environ.get("CF_TUNNEL_FOR_WEBARENA"))

# setup logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# setup files config

def write_fail_message(message: str, custom_instance_num):
    fail_file_path = f"fail_message-{custom_instance_num}"
    with open(fail_file_path, 'w') as f:
        f.write(message)

def read_fail_message(custom_instance_num):
    fail_file_path = f"fail_message-{custom_instance_num}"

    with open(fail_file_path, 'r') as f:
        fail_message = f.read()
    return fail_message

def reset_ongoing(custom_instance_num):
    lock_file_path = f"reset-{custom_instance_num}.lock"
    return os.path.exists(lock_file_path)

def initiate_reset():

    custom_instance_num = os.getenv("CUSTOM_INSTANCE_NUM", "<UNKNOWN>")
    lock_file_path = f"reset-{custom_instance_num}.lock"
    # Attempt to acquire lock (create lock file atomically)
    try:
        fd = os.open(lock_file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, 'w') as file:
            file.write('')  # empty file
    except FileExistsError:
        return False

    # Execute reset (and then release lock) in a separate thread
    def reset_fun():
        try:
            env_ = {}
            if 'CUSTOM_INSTANCE_NUM' in os.environ:
                env_['CUSTOM_INSTANCE_NUM'] = os.environ['CUSTOM_INSTANCE_NUM']
            
            if len(env_) == 0:
                env_ = None
            
            # Execute the reset script
            if os.environ.get("CF_TUNNEL_FOR_WEBARENA") == "true":
                env_['HOST_WITH_CLOUDFLARE'] = "true"
                logger.info("Resetting using reset.sh with cloudflare")
                subprocess.run(['bash', 'reset.sh'], check=True, env=env_)
            else:
                env_['HOST_WITH_CLOUDFLARE'] = "false"
                logger.info("Resetting using reset.sh without cloudflare")
                subprocess.run(['bash', 'reset.sh'], check=True, env=env_)
            
            logger.info("Reset successful!")
            write_fail_message("", custom_instance_num=custom_instance_num)
        
        except subprocess.CalledProcessError as e:
            logger.info("Reset failed :(")
            write_fail_message(str(e), custom_instance_num=custom_instance_num)

        # Release lock (remove lock file)
        lock_file_path = f"reset-{custom_instance_num}.lock"
        pathlib.Path(lock_file_path).unlink(missing_ok=True)

    thread = threading.Thread(target=reset_fun)
    thread.start()

    return True


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = self.path
        logger.info(f"{parsed_path} request received")
        match parsed_path:
            case '/reset':
                if initiate_reset():
                    logger.info("Running reset script...")
                    self.send_response(200)  # OK
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'Reset initiated, check status <a href="/status">here</a>'.encode())
                else:
                    logger.warning("Reset already running, ignoring request.")
                    self.send_response(418)  # I'm a teapot
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'Reset already running, check status <a href="/status">here</a>'.encode())
            case "/status":
                instance_num = os.environ.get("INSTANCE_NUM", "<UNKNOWN>")
                custom_instance_num = os.environ.get("CUSTOM_INSTANCE_NUM", "<UNKNOWN>")
                fail_message = read_fail_message(custom_instance_num=custom_instance_num)
                if reset_ongoing(custom_instance_num=custom_instance_num):
                    logger.info("Returning ongoing status")
                    logger.info("INSTANCE_NUM: " + instance_num)
                    logger.info("CUSTOM_INSTANCE_NUM: " + custom_instance_num)

                    if not os.path.exists(f"reset-status-{custom_instance_num}.json"):
                        status = {"status": "Unknown (reset-status.json not found)"}
                    else:
                        with open(f"reset-status-{custom_instance_num}.json", "r") as f:
                            status = json.load(f)

                    self.send_response(200)  # OK
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'<br>Instance number: {instance_num}'.encode())
                    self.wfile.write(f'<br>Custom instance number: {custom_instance_num}'.encode())
                    self.wfile.write(f'<br>Reset ongoing. Status: {status["status"]}'.encode())
                elif fail_message:
                    logger.error("Returning error status")
                    self.send_response(500)  # Internal Server Error
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'<br>Instance number: {instance_num}'.encode())
                    self.wfile.write(f'<br>Custom instance number: {custom_instance_num}'.encode())
                    self.wfile.write(f'<br>Error executing reset script:<p>{fail_message}</p>'.encode())
                else:
                    logger.info("Returning ready status")
                    self.send_response(200)  # OK
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'Ready for duty!'.encode())
            
            case "/logs":
                custom_instance_num = os.environ.get("CUSTOM_INSTANCE_NUM", "<UNKNOWN>")
                if not os.path.exists(f"reset-logs-{custom_instance_num}.txt"):
                    logger.warning("No logs found")
                    self.send_response(404)
                
                if os.path.exists(f"reset-logs-{custom_instance_num}.txt"):

                    with open(f"reset-logs-{custom_instance_num}.txt", "r") as f:
                        logs = f.read()
                        logs = logs.replace("\n", "<br>")
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(logs.encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f'Logs not found'.encode())
            
            case _:
                logger.info("Wrong request")
                self.send_response(404)  # Not Found
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'Endpoint not found'.encode())


# Parse command-line arguments
parser = argparse.ArgumentParser(description='Start a simple HTTP server to execute a reset script.')
parser.add_argument('--port', type=int, help='Port number the server will listen to')
args = parser.parse_args()

# Clear fail and lock files
custom_instance_num = os.environ.get("CUSTOM_INSTANCE_NUM", "<UNKNOWN>")
write_fail_message("", custom_instance_num=custom_instance_num)
if reset_ongoing(custom_instance_num=custom_instance_num):
    lock_file_path = f"reset-{custom_instance_num}.lock"
    os.remove(lock_file_path)

# Run the server
with http.server.ThreadingHTTPServer(('', args.port), CustomHandler) as httpd:
    logger.info(f'Serving on port {args.port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
