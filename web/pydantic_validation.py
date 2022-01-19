from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class MeetingSchema(BaseModel):
    title: str
    start_date_time: Optional[datetime] = None
    end_date_time: Optional[datetime] = None
    participant_emails: List[str] = []
