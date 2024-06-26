import json
from datetime import datetime
from .redis_client import redis_client

def store_course_progress(student_id: int, course_id: int, progress: float, is_completed: bool, enrolled_time: datetime):
    key = f"student:{student_id}:course:{course_id}"
    data = {
        "progress": progress,
        "is_completed": is_completed,
        "enrolled_time": enrolled_time.isoformat()
    }
    redis_client.set(key, json.dumps(data))

def get_course_progress(student_id: int, course_id: int):
    key = f"student:{student_id}:course:{course_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def store_chapter_progress(student_id: int, chapter_id: int, is_completed: bool, start_time: datetime, end_time: Optional[datetime]):
    key = f"student:{student_id}:chapter:{chapter_id}"
    data = {
        "is_completed": is_completed,
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None
    }
    redis_client.set(key, json.dumps(data))

def get_chapter_progress(student_id: int, chapter_id: int):
    key = f"student:{student_id}:chapter:{chapter_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None
