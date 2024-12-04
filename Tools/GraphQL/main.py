from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from typing import List, Optional
import strawberry
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter


DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(DATABASE_URL, echo=True)


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="posts")




class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

    
    posts: List[Post] = Relationship(back_populates="author")


SQLModel.metadata.create_all(engine)


@strawberry.type
class PostType:
    id: int
    title: str
    content: str

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    posts: List[PostType]


@strawberry.type
class Query:
    @strawberry.field
    def get_user(self, id: int) -> UserType:
        with Session(engine) as session:
            user = session.get(User, id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return UserType(id=user.id, name=user.name, email=user.email, posts=user.posts)
    
    @strawberry.field
    def get_post(self, id: int) -> PostType:
        with Session(engine) as session:
            post = session.get(Post, id)
            if not post:
                raise HTTPException(status_code=404, detail="Post Not found")
            return PostType(id=post.id, title=post.title, content=post.content)
        

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name:str, email:str) -> UserType:
        with Session(engine) as session:
            new_user = User(name=name, email=email)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return UserType(id=new_user.id, name=new_user.name, email=new_user.email, posts=[])
    
    @strawberry.mutation
    def create_post(self, title: str, content: str, author_id: int) -> PostType:
        with Session(engine) as session:
            new_post = Post(title=title, content=content, author_id=author_id)
            session.add(new_post)
            session.commit()
            session.refresh(new_post)
            return PostType(id=new_post.id, title=new_post.title, content=new_post.content)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app = FastAPI()

app.include_router(graphql_app, prefix='/graphql')
