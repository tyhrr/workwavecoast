"""Debug search function"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

from services.application_service import ApplicationService
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Testing search...")
app_service = ApplicationService(logger)
app_service.initialize()

try:
    result = app_service.search_applications("", {'page': 1, 'per_page': 5})
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

try:
    result = app_service.get_advanced_filters_options()
    print(f"\nFilter options result: {result}")
except Exception as e:
    print(f"Filter Error: {e}")
    traceback.print_exc()
