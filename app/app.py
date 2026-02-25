from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from app.db import Post, create_db_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()   # runs once when app starts
    yield
    # cleanup code here (if needed)

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"server_status": "running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),         # binary file from client
    caption: str = Form(...),             # text field from HTML form
    session: AsyncSession = Depends(get_async_session)  # DB session
):
    # Step 1: Create the object
    post = Post(
        caption=caption,
        url="dummy_url",
        file_type="photo",
        file_name="dummy_name"
    )

    # Step 2: Stage it (like git add)
    session.add(post)

    # Step 3: Persist it (like git commit)
    await session.commit()

    # Step 4: Refresh to populate auto-generated fields
    await session.refresh(post)

    return post

@app.get("/feed")
async def get_feed(
    sesseion:AsyncSession = Depends(get_async_session)
):
 
    result = await sesseion.execute(select(Post).order_by(Post.created_at.desc()).limit(10))

 # Extract results from cursor
    posts = [row[0] for row in result.all()]

    # Serialize to JSON-safe dicts
    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat()
        })

    return post_data

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Convert string to UUID object for comparison
        post_uuid = uuid.UUID(post_id)

        # Query for the specific post
        result = await session.execute(
            select(Post).where(Post.id == post_uuid)
        )
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Delete and commit
        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))