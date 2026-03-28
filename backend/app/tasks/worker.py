from arq.connections import RedisSettings
from arq.cron import cron

from app.config import settings
from app.services.grading_service import GradingService
from app.tasks.dream_motor import async_dream_cycle
import json


async def async_grade_task(ctx, submission_id: str, fact: str, student_response: str, rubric: str):
    grader = GradingService()
    result = await grader.grade_submission(fact, student_response, rubric)
    # Logging the graded task (simulating DB save until full DB plumbing)
    print(f"Graded submission {submission_id}: {result}")
    return result


class WorkerSettings:
    functions = [async_grade_task, async_dream_cycle]
    cron_jobs = [
        cron(
            async_dream_cycle,
            hour={h % 24 for h in range(0, 24, settings.dream_interval_hours)},
            minute=0,
        ),
    ]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
