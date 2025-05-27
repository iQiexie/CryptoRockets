from sqlalchemy import case
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Task
from app.db.models import TaskUser
from app.db.repos.base.base import BaseRepo


class UserTaskRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_user_tasks(self, telegram_id: int) -> list[Task]:
        stmt = (
            select(Task)
            .add_columns(
                case(
                    (TaskUser.user_id.isnot(None), True),
                    else_=False
                ).label("completed")
            )
            .outerjoin(TaskUser, (Task.id == TaskUser.task_id) & (TaskUser.user_id == telegram_id))
        )

        from sqlalchemy.dialects import postgresql;
        print(stmt.compile(compile_kwargs={"literal_binds": True}, dialect=postgresql.dialect()))

        query = await self.session.execute(stmt)
        tasks = query.mappings().all()

        response = []
        for row_mapping in tasks:
            task, completed = row_mapping.values()
            task.completed = completed
            response.append(task)

        return response
