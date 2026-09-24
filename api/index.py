import sys
import os

# Add ml-pipeline directory to Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml-pipeline")))

from main import app
