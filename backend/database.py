from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_detection_db")

# Initialize Motor async client
client = AsyncIOMotorClient(MONGO_URI)

# Export the database object
db = client[MONGO_DB_NAME]


async def ping_db():
    """Ping MongoDB to confirm connectivity. Called on app startup."""
    await client.admin.command("ping")
    print(f"[OK] MongoDB connected -- database: '{MONGO_DB_NAME}'")
