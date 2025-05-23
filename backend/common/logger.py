import logging
from . import settings

# MARK: logger "psmon"
logger: logging.Logger|None = logging.getLogger('psmon')

logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s", 
)
logger.setLevel(logging.DEBUG if settings.APP_DEBUG else logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.WARNING)  # 毎秒ログ出力されるため抑止する
