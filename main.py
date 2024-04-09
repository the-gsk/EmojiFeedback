from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from all origins (you might want to restrict this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize SQLite database
conn = sqlite3.connect('feedback.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS feedback
             (id INTEGER PRIMARY KEY AUTOINCREMENT, emoji TEXT)''')
conn.commit()

def create_ratings_table():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                 (vote INTEGER, time INTEGER)''')
    conn.commit()
    conn.close()

# Call the function to create the table before using it
create_ratings_table()
# Model for feedback
class Feedback(BaseModel):
    emoji: str

# Endpoint to store feedback
@app.post("/feedback/")
async def store_feedback(feedback: Feedback):
    with conn:
        c.execute("INSERT INTO feedback (emoji) VALUES (?)", (feedback.emoji,))
    return {"message": "Feedback stored successfully"}

# Endpoint to retrieve all feedback (for demonstration purposes)
@app.get("/feedback/")
async def get_feedback():
    with conn:
        c.execute("SELECT * FROM feedback")
        return c.fetchall()


class Rating(BaseModel):
    vote: int
    time: int

# Function to save rating data to SQLite database
def save_rating_data(rating: Rating):
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute("INSERT INTO ratings (vote, time) VALUES (?, ?)", (rating.vote, rating.time))
    conn.commit()
    conn.close()


# Function to fetch rating data from SQLite database
def get_rating_data():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute("SELECT vote, COUNT(*) FROM ratings GROUP BY vote")
    rating_data = dict(c.fetchall())
    conn.close()
    return rating_data


@app.post("/api/postRating")
async def post_rating(rating: Rating):
    save_rating_data(rating)
    return {"message": "Rating received successfully"}


@app.get("/api/getTotalRating")
async def get_total_rating():
    rating_data = get_rating_data()
    print("rating_data",type(rating_data))
    return rating_data

# @app.post("/api/postRating")
# async def post_rating(rating: Rating):
#     # Here you would save the rating data to your database
#     # For demonstration purposes, let's just print the received data
#     print("Received rating:", rating)
#     return {"message": "Rating received successfully"}


# Example function to fetch rating data from the database
# def get_rating_data():
#     # This is a placeholder function to simulate fetching data from the database
#     # You should replace this with actual database queries
#     return {
#         1: 5,   # Example: 5 votes with rating 1
#         2: 10,  # Example: 10 votes with rating 2
#         3: 8,    # Example: 8 votes with rating 3
#         4: 12,    # Example: 8 votes with rating 3
#         5: 20    # Example: 8 votes with rating 3
#     }

# Endpoint to get total rating and update counters
# @app.get("/api/getTotalRating")
# async def get_total_rating():
#     rating_data = get_rating_data()  # Fetch rating data from the database
#     return rating_data