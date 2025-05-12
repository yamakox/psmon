from pathlib import Path
from backend import create_app
from backend.common import settings

base_path = Path(__file__).parent.resolve()
app = create_app(base_path=base_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)

