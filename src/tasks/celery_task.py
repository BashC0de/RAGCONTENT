from celery import Celery
from src.config import settings
from src.generation.orchestrator import run_rag_pipeline

celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"

@celery.task(name="tasks.run_rag")
def async_run_rag(payload):
    return run_rag_pipeline(payload)
# celery_task.py
from celery import Celery
from src.config import settings
import subprocess
import sys

celery = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

def start_celery_worker():
    """
    Starts a Celery worker process from Python (optional).
    """
    subprocess.Popen([
        sys.executable, '-m', 'celery', '-A', 'src.tasks.celery_task.celery',
        'worker', '--loglevel=info'
    ])
from celery import Celery
from src.config import settings

celery = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

if __name__ == "__main__":
    celery.start()  