
from .imports import *

def job_status(idx, job_uuid):
    if job_uuid not in idx:
        return "finished"
    job = idx[job_uuid]
    result = job.get_status(refresh=True)
    if result is None:
        return "finished"
    return result