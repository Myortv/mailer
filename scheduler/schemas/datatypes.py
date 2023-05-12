from typing import List, Optional

from dataclasses import dataclass, field
from datetime import datetime


from scheduler.schemas.client import ClientInDB

import asyncio


@dataclass
class Message:
    start_window: datetime
    end_window: datetime
    client_id: int
    phone: int
    shifted: bool = False


@dataclass
class Mailing:
    id: int
    start_at: datetime
    end_at: datetime
    body: str
    message_queue: List[Message] = field(default_factory=lambda: [])
    task: asyncio.Task | None = None
    timeout: datetime | None = None

    def generate_message_queue(
        self,
        clients: List[ClientInDB],
    ):
        for client in clients:
            self.message_queue.append(Message(
                max(self.start_at, client.start_recieve),
                min(self.end_at, client.start_recieve + client.recieve_duration),
                client_id=client.id,
                phone=int(client.phone_number),
            ))
