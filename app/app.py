from fastapi import FastAPI

app= FastAPI()

@app.get("/")
def read_root():
    return {"server_status": "running"}


text_posts = {
    1: {"name": "prajwal", "title": "cool_pic", "content": "full chill mood at goa beach"},
    2: {"name": "ananya", "title": "morning_vibes", "content": "sunrise and coffee make the best combo"},
    3: {"name": "rohit", "title": "gym_day", "content": "leg day done and dusted"},
    4: {"name": "megha", "title": "road_trip", "content": "long drive through the hills"},
    5: {"name": "arjun", "title": "coding_night", "content": "debugging till 2 am but worth it"},
    6: {"name": "sneha", "title": "foodie_life", "content": "trying out a new pasta recipe"},
    7: {"name": "vikram", "title": "match_win", "content": "our team won the finals today"},
    8: {"name": "kiran", "title": "rainy_day", "content": "love the smell of fresh rain"},
    9: {"name": "pooja", "title": "book_time", "content": "reading a thriller novel tonight"},
    10: {"name": "rahul", "title": "tech_event", "content": "attended an AI conference in bangalore"},
    11: {"name": "nisha", "title": "family_time", "content": "weekend lunch with cousins"},
    12: {"name": "manoj", "title": "startup_idea", "content": "brainstorming new app concepts"},
    13: {"name": "divya", "title": "fitness_goal", "content": "completed 5km run today"},
    14: {"name": "akash", "title": "movie_night", "content": "watched a sci-fi blockbuster"},
    15: {"name": "lavanya", "title": "art_work", "content": "finished my latest painting"},
    16: {"name": "suraj", "title": "music_jam", "content": "learning a new guitar chord"},
    17: {"name": "harsha", "title": "camping_fun", "content": "spent the night under the stars"},
    18: {"name": "priya", "title": "exam_prep", "content": "studying hard for upcoming tests"},
    19: {"name": "deepak", "title": "market_day", "content": "fresh veggies from local market"},
    20: {"name": "isha", "title": "pet_love", "content": "my dog learned a new trick today"}
}
#all without parameter
@app.get("/posts")
def get_all_posts():
    return text_posts

#with parameter
#this will give error if id is not present in text_posts
@app.get("/posts/{id}")
def get_post_id(id:int):
    return text_posts[id]

#this will not give error if id is not present in text_posts, it will return null
@app.get("/posts-2/{id}")
def get_post_id(id:int):
    return text_posts.get(id)

#handling error if id is not present in text_posts
from fastapi import HTTPException

@app.get("/posts-3/{id}")
def get_post_id(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="id not found") 
    return text_posts.get(id)


#Query Parameters
@app.get("/posts-with-limit")
def get_posts_with_limit(limit: int = None):
    if limit is None:
        return None
    return dict(list(text_posts.items())[:limit])

#Request Body
from app.schema import PostCreate,PostReturn

@app.post("/create_post") 
def create_post(post: PostCreate) ->PostReturn :
    new_id = max(text_posts.keys()) + 1
    body={
        'name': post.name,
        'title': post.title,
        'content': post.content
    }
    text_posts[new_id] = body
    return text_posts[new_id]