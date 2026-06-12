from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sqlite_partial_email_index_exists(connection) -> bool:
    row = connection.execute(
        text(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name='uq_employees_email_active'"
        )
    ).fetchone()
    return row is not None


def _sqlite_employees_table_has_column_unique_email(connection) -> bool:
    row = connection.execute(
        text("SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'")
    ).fetchone()
    if not row or not row[0]:
        return False
    table_sql = row[0].upper()
    return "EMAIL" in table_sql and "UNIQUE" in table_sql


def _migrate_sqlite_email_uniqueness(connection) -> None:
    """Rebuild employees table so email is unique among active records only."""
    connection.execute(text("PRAGMA foreign_keys=OFF"))

    connection.execute(
        text(
            """
            CREATE TABLE employees_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                job_title VARCHAR(100) NOT NULL,
                department VARCHAR(100) NOT NULL,
                country VARCHAR(100) NOT NULL,
                hire_date DATE NOT NULL,
                exit_date DATE,
                exit_reason VARCHAR(20),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
            """
        )
    )
    connection.execute(
        text(
            """
            INSERT INTO employees_new (
                id, full_name, email, job_title, department, country,
                hire_date, exit_date, exit_reason, created_at, updated_at
            )
            SELECT
                id, full_name, email, job_title, department, country,
                hire_date, exit_date, exit_reason, created_at, updated_at
            FROM employees
            """
        )
    )
    connection.execute(text("DROP TABLE employees"))
    connection.execute(text("ALTER TABLE employees_new RENAME TO employees"))

    connection.execute(text("CREATE INDEX ix_employees_full_name ON employees (full_name)"))
    connection.execute(text("CREATE INDEX ix_employees_country ON employees (country)"))
    connection.execute(text("CREATE INDEX ix_employees_job_title ON employees (job_title)"))
    connection.execute(text("CREATE INDEX ix_employees_department ON employees (department)"))
    connection.execute(
        text(
            "CREATE UNIQUE INDEX uq_employees_email_active "
            "ON employees (email) WHERE exit_date IS NULL"
        )
    )

    connection.execute(text("PRAGMA foreign_keys=ON"))


def apply_migrations() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "employees" not in inspector.get_table_names():
        return

    with engine.begin() as connection:
        if _sqlite_partial_email_index_exists(connection):
            return
        if not _sqlite_employees_table_has_column_unique_email(connection):
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_employees_email_active "
                    "ON employees (email) WHERE exit_date IS NULL"
                )
            )
            return
        _migrate_sqlite_email_uniqueness(connection)


def create_tables():
    Base.metadata.create_all(bind=engine)
    apply_migrations()
