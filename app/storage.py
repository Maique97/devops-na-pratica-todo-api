"""Armazenamento em memória das tarefas (suficiente para a Fase 1)."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import Lock


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def create(self, title: str) -> Task:
        with self._lock:
            task = Task(id=self._next_id, title=title)
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def update(self, task_id: int, title: str | None = None,
               done: bool | None = None) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if title is not None:
            task.title = title
        if done is not None:
            task.done = done
        return task

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
