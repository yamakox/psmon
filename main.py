from pathlib import Path
from backend import create_app

base_path = Path(__file__).parent.resolve()
app = create_app(base_path=base_path)
