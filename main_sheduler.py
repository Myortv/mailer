import datetime
import asyncio

from scheduler.core.logger import printt, filelogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.interval import IntervalTrigger

from scheduler.db.base import DatabaseManager


from scheduler.core.configs import settings

from scheduler.jobs.jobs import check_free_mailing, clean_tasks


DEFAULT_TIMEZONE = datetime.datetime.now().tzinfo

scheduler = AsyncIOScheduler()

settings.SCHEDULER = scheduler
# trigger_check_free = IntervalTrigger(seconds=60*5)
# trigger_clean_tasks = IntervalTrigger(seconds=20)
trigger_check_free = IntervalTrigger(seconds=6)
trigger_clean_tasks = IntervalTrigger(seconds=2)


scheduler.configure(
    jobstores={'default': MemoryJobStore()},
    executors={'default': AsyncIOExecutor()},
    timezone=DEFAULT_TIMEZONE,
)

async def shutdown():
    printt('DATABASE CONNECTION CLOSING')
    await DatabaseManager.stop()
    printt('DATABASE CONNECTION CLOSED')
    filelogger.warning('server stopped')

async def startup():
    printt('START CONNECTING DATABASE')
    await DatabaseManager.start(
        settings.POSTGRES_DB,
        settings.POSTGRES_USER,
        settings.POSTGRES_PASSWORD,
        settings.POSTGRES_HOST,
    )
    printt('DATABASE CONNECTED')
    printt('START SHEDULER')
    scheduler.start()
    printt('ADD SHEDULER JOBS')
    scheduler.add_job(check_free_mailing, trigger_check_free, max_instances=1)
    scheduler.add_job(clean_tasks, trigger_clean_tasks, max_instances=1)
    printt('STARTUP COMPLETED')
    filelogger.warning('server started')

if __name__== '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(startup())
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        printt('INTERRUPTED')
        asyncio.get_event_loop().run_until_complete(shutdown())
        import sys
        sys.exit()
    except Exception as e:
        printt('INTERRUPTED WITH ERROR')
        filelogger(e)
        asyncio.get_event_loop().run_until_complete(shutdown())
        raise e
