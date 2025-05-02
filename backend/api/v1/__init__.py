import importlib
import pkgutil
from fastapi import APIRouter
from pathlib import Path

# MARK: /api/v1
router = APIRouter(prefix="/api/v1", tags=['API v1'])

# モジュールを探索し、routerを取得してマウント
package_name = __name__
package_path = Path(__file__).parent
for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
    module = importlib.import_module(f"{package_name}.{module_name}")
    if hasattr(module, "router"):
        router.include_router(module.router)
