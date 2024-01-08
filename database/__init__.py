from sqlalchemy import update, delete, and_, text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ssl import create_default_context
from dotenv import load_dotenv
from os import getenv

load_dotenv()

DB_URL = getenv('DB_URL')
SSL = getenv('SSL')

connect_args = {}
if SSL: connect_args['ssl'] =  create_default_context(cafile = SSL)

engine = create_async_engine(
    DB_URL, 
    connect_args = connect_args,
    pool_pre_ping = True
)

AsyncSessionLocal = sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

class Base(DeclarativeBase):
    def dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    @classmethod
    async def update(cls, id: int, **kwargs):
        async with AsyncSessionLocal() as db:
            stmt = update(cls).where(getattr(cls, 'id') == id).values(**kwargs)
            result = await db.execute(stmt)
            await db.commit()
            
            if result.rowcount != 0:
                data = await cls.find_one(id = id)
                return data
    
    @classmethod
    async def delete(cls, **kwargs):
        async with AsyncSessionLocal() as db:
            stmt = delete(cls).where(and_(*[getattr(cls, col) == value for col, value in kwargs.items()]))
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount != 0

            
    @classmethod
    async def find_one(cls, **kwargs):
        async with AsyncSessionLocal() as db:
            stmt = select(cls).filter_by(**kwargs)
            result = await db.execute(stmt)
            return result.scalars().first()

        
    @classmethod
    async def find_many(cls, **kwargs):
        async with AsyncSessionLocal() as db:
            stmt = select(cls).filter_by(**kwargs)
            result = await db.execute(stmt)
            return result.scalars().all()

        
    @classmethod    
    async def find_many_regex(cls, **kwargs):
        async with AsyncSessionLocal() as db:
            col, re = list(kwargs.items())[0]
            
            stmt = select(cls).filter(text(f'{col} REGEXP "{re}"'))
            result = await db.execute(stmt)
            return result.scalars().all()


    @classmethod
    async def create(cls, **kwargs):
        async with AsyncSessionLocal() as db:
            query = cls(**kwargs)
            db.add(query)
            await db.commit()
            await db.refresh(query)

        return query