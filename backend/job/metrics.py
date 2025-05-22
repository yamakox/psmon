import psutil
from ..db import database
from ..common import settings
import time

def collect_metrics():
    '''psutilで取得したデータをDBに保存する。'''
    t = time.time_ns()
    database.write_system_stats_record(
        t,
        cpu_percent=psutil.cpu_percent(), 
        mem_available=float(psutil.virtual_memory().available), 
        disk_used=float(psutil.disk_usage(settings.DISK_USAGE_PATH).used), 
    )
    database.write_process_cpu_record(
        t,
        _get_top_cpu_processes(),
    )

def get_mem_total():
    '''メモリの総容量を取得する。'''
    return psutil.virtual_memory().total

def get_disk_total():
    '''ディスクの総容量を取得する。'''
    return psutil.disk_usage(settings.DISK_USAGE_PATH).total

def _get_top_cpu_processes(top_n: int = 10) -> list[tuple[float, int, str]]:
    '''CPU使用率が高いプロセスを取得する。

    Args:
        top_n (int): 上位何位までを取得するか

    Returns:
        list[tuple[float, int, str]]: プロセスのCPU使用率、PID、プロセス名
    '''
    # 1回目の呼び出し（キャッシュ用）
    process_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent = proc.cpu_percent(interval=None)
            process_list.append((cpu_percent, proc.pid, proc.name()))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # CPU使用率でソート（降順）し、上位top_nを返す
    top_processes = sorted(process_list, key=lambda x: x[0], reverse=True)[:top_n]

    return top_processes
