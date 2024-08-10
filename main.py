from fastapi import (
    FastAPI,
)

from database import (
    engine,
)

from models import (
    Base,
)

from routers import (
    auth,
    todos
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)


