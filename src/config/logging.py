import logging
import os


def custom_path_filter(path):
    # Define the project root name
    project_root = "react-from-scratch"
    
    # Find the index of the project root in the path
    idx = path.find(project_root)
    if idx != -1:
        # Extract the portion of the path after the project root
        path = path[idx+len(project_root):]
    return path

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pathname = custom_path_filter(self.pathname)


def setup_logger(log_filename="app.log", log_dir="logs"):
    # Ensure the logging directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_filepath = os.path.join(log_dir, log_filename)

    # Define the logging configuration
    logging.setLogRecordFactory(CustomLogRecord)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(module)s] [%(pathname)s]: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filepath)
        ]
    )

    # Return the configured logger
    return logging.getLogger()

logger = setup_logger()