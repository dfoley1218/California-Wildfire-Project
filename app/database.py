from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv()

# Single connection URL. Works with hosted Postgres (e.g. Neon), whose
# connection strings bake in SSL params like ?sslmode=require.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set — add it to your .env (see .env.example)."
    )

engine = create_engine(DATABASE_URL)
