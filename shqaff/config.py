import os


DB_HOST = os.getenv("SHAQAFF_DB_HOST", "localhost")
DB_PORT = os.getenv("SHAQAFF_DB_PORT", "5432")
DB_NAME = os.getenv("SHAQAFF_DB_NAME", "shqaff")
DB_USER = os.getenv("SHAQAFF_DB_USER", "postgres")
DB_PASS = os.getenv("SHAQAFF_DB_PASS", "")


# psycopg2 is the driver shqaff declares; name it, because SQLAlchemy 2.1 made
# psycopg (v3) the default for a bare "postgresql://" URL.
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
