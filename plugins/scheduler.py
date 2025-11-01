
from apscheduler.schedulers.background import BackgroundScheduler

class JobScheduler:
    def __init__(self):
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.jobs = {}
    def add_every_minutes(self, job_id:str, minutes:int, func, *args, **kwargs):
        if job_id in self.jobs: self.remove(job_id)
        job = self.sched.add_job(func, 'interval', minutes=minutes, args=args, kwargs=kwargs, id=job_id, replace_existing=True)
        self.jobs[job_id] = job; return f"Job '{job_id}' toutes {minutes} min."
    def add_cron(self, job_id:str, cron_expr:dict, func, *args, **kwargs):
        if job_id in self.jobs: self.remove(job_id)
        job = self.sched.add_job(func, 'cron', id=job_id, replace_existing=True, **cron_expr, args=args, kwargs=kwargs)
        self.jobs[job_id] = job; return f"Job '{job_id}' (cron)."
    def list(self): return [j.id for j in self.sched.get_jobs()]
    def remove(self, job_id:str):
        try: self.sched.remove_job(job_id); self.jobs.pop(job_id, None); return f"Job '{job_id}' supprimé."
        except Exception as e: return f"Erreur: {e}"
