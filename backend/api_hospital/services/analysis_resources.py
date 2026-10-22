"""Container-aware admission control; inspect the real cgroup, not host RAM."""
import os
from pathlib import Path
import psutil

MIB = 1024 * 1024
SPARK_MIN_TOTAL = 2048 * MIB
SPARK_MIN_AVAILABLE = 1536 * MIB


def memory_snapshot():
    for limit_path, usage_path in (
        ('/sys/fs/cgroup/memory.max', '/sys/fs/cgroup/memory.current'),
        ('/sys/fs/cgroup/memory/memory.limit_in_bytes', '/sys/fs/cgroup/memory/memory.usage_in_bytes'),
    ):
        try:
            limit = int(Path(limit_path).read_text().strip())
            used = int(Path(usage_path).read_text().strip())
            if 0 < limit < (1 << 60):
                return limit, max(0, limit - used)
        except (OSError, ValueError):
            continue
    if os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'):
        # Unknown container limits must never be mistaken for the host's large RAM.
        return 512 * MIB, None
    memory = psutil.virtual_memory()
    return memory.total, memory.available


def choose_engine():
    mode = os.getenv('ANALYSIS_ENGINE', 'auto').strip().lower()
    if mode not in ('auto', 'spark', 'lightweight'):
        raise ValueError('ANALYSIS_ENGINE debe ser auto, lightweight o spark.')
    total, available = memory_snapshot()
    capable = total >= SPARK_MIN_TOTAL and available is not None and available >= SPARK_MIN_AVAILABLE
    if mode == 'spark' and not capable:
        raise ValueError('Spark no tiene memoria suficiente para ejecutarse junto a la API. Usa ANALYSIS_ENGINE=auto o un trabajador separado con más memoria.')
    if mode == 'auto':
        mode = 'spark' if capable else 'lightweight'
    if mode == 'lightweight' and available is not None and available < 96 * MIB:
        raise ValueError('El servidor tiene poca memoria disponible. Espera a que se liberen recursos y vuelve a intentar el análisis.')
    return mode


def memory_pressure():
    total, available = memory_snapshot()
    return available is not None and available < max(48 * MIB, total // 10)
