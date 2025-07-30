from multiprocessing import cpu_count
from os import getenv
from exsclaim.api import settings

bind = f"0.0.0.0:{getenv('DASHBOARD_PORT')}"
workers = max(cpu_count() // 2, 1)

if settings.DEBUG:
	reload = True
