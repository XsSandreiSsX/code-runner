from app.models.submission import Submission

class JudgeService:
    @classmethod
    async def process(cls, submission_id: int):
        """Business logic will be here soon. :)"""
        print(f"process submission: {submission_id}")
        from time import sleep

        sleep(30) # An example of executing long logic
        print("running finished")