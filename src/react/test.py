from vertexai.generative_models import HarmBlockThreshold 
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory
from vertexai.generative_models import Part
from google.api_core.retry import Retry
from src.config.logging import logger
from src.config.setup import config
from typing import Optional
from typing import Union
from typing import Dict
from typing import List 
import requests 
import json
import re
import os




