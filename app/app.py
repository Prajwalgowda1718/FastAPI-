from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from app.db import Post, create_db_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from imagekitio import ImageKit
import uuid
import shutil
import os
from dotenv import load_dotenv
import tempfile
from app.users import auth_backend, fastapi_users, current_active_user
from app.schema import UserRead, UserCreate, UserUpdate
from app.db import User



load_dotenv()
imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY")
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan=lifespan)

# JWT Login/Logout routes 
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

# Registration routes 
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# Password reset routes 
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

# Email verification routes 
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

# User management routes 
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)


@app.get("/")
def read_root():
    return {"server_status": "running"}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)   #  protects the route
):
    temp_file_path = None

    try:
        # 1. Create a temp file with the same extension as the upload
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # 2. Upload to ImageKit (v5 SDK)
        upload_result = imagekit.files.upload(  #  lowercase, instance
        file=open(temp_file_path, "rb"),
        file_name=file.filename,
        use_unique_file_name=True,
        tags=["backend_upload"]
        )
        

        # 3. Save to DB
        post = Post(
            caption=caption,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name,
            user_id=user.id    #  link post to authenticated user
)

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # Get all posts
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = [row[0] for row in result.all()]

    # Build a user lookup dictionary
    user_result = await session.execute(select(User))
    users = [row[0] for row in user_result.all()]
    user_dict = {u.id: u.email for u in users}

    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "user_id": str(post.user_id),
            "email": user_dict.get(post.user_id, "unknown"),
            "is_owner": post.user_id == user.id   # can this user delete it?
        })

    return post_data

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    post_uuid = uuid.UUID(post_id)
    result = await session.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Authorization check — must be the post's owner
    if post.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this post"
        )

    await session.delete(post)
    await session.commit()
    return {"success": True, "message": "Post deleted successfully"}

