from nautobot.apps.jobs import register_jobs

from frame_surfer.jobs.jobs import jobs

register_jobs(*jobs)
