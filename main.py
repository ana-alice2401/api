from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from asyncio import create_task, gather 
from typing import List

from models.invite import Invite
from database.invite import InviteORM

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

@app.post('/invite', response_model = List[Invite])
async def invite(invite: List[Invite]):
    tasks = [create_task(InviteORM.create(**i.dict())) for i in invite if i.name]
    gather(*tasks)

    return invite

if __name__ == '__main__':
    from uvicorn import run
    run(app, host = '0.0.0.0', port = 8000)