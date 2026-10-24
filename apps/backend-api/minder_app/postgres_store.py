"""Native PostgreSQL persistence for the existing Store/service contracts.

The finite SQL compatibility layer covers inspected application statements, not a
SQLite emulator. Short writes retain SQLite's serialized-check/write semantics via
one transaction-scoped advisory lock in this application's schema. No model call
belongs in a transaction; visible history reads use a repeatable-read snapshot.
"""
from contextlib import contextmanager
import os
import re
from .store import Store, AppError


def _error(error, fallback="postgres_statement_failed"):
    state=getattr(error,"sqlstate",None)
    if state in ("40001","40P01","55P03","57014","23505"):
        value=AppError("postgres_concurrency_conflict",409)
    elif state and (state.startswith("22") or state in ("23502","23503","23514")):
        value=AppError("invalid_persistent_state",422)
    elif state and state.startswith("08"):
        value=AppError("postgres_unavailable",503)
    else:
        value=AppError(fallback,500)
    value.sqlstate=state # safe diagnostics only; never retain SQL/DSN/parameters.
    return value


class PostgresRow:
    """sqlite3.Row-compatible key/index access and dict(row), without data repr."""
    def __init__(self,names,values):
        self._names=names;self._values=tuple(values);self._by_name=dict(zip(names,values))
    def __getitem__(self,key):
        return self._values[key] if isinstance(key,int) else self._by_name[key]
    def __iter__(self):
        return iter(self._values)
    def __len__(self):
        return len(self._values)
    def keys(self):
        return list(self._names)
    def get(self,key,default=None):
        return self._by_name.get(key,default)
    def __repr__(self):
        return "<PostgresRow redacted>"


def _row_factory(cursor):
    names=tuple(column.name for column in cursor.description or ())
    return lambda values:PostgresRow(names,values)


def _segments(query):
    """Separate SQL syntax from quoted/comment data before replacing qmarks."""
    pattern=r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|--[^\n]*(?:\n|$)|/\*[\s\S]*?\*/)"
    for index,part in enumerate(re.split(pattern,query)):
        yield index%2==0,part


def postgres_sql(query,params_present=False):
    original=query.strip().rstrip(';')
    if original.upper()=="BEGIN":
        return "BEGIN ISOLATION LEVEL REPEATABLE READ"
    ignored=bool(re.match(r"INSERT\s+OR\s+IGNORE\s+INTO\b",original,re.I))
    replaced=bool(re.match(r"INSERT\s+OR\s+REPLACE\s+INTO\s+documents\b",original,re.I))
    if ignored:
        original=re.sub(r"INSERT\s+OR\s+IGNORE\s+INTO", "INSERT INTO",original,count=1,flags=re.I)
    if replaced:
        original=re.sub(r"INSERT\s+OR\s+REPLACE\s+INTO", "INSERT INTO",original,count=1,flags=re.I)
    if re.match(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(?:proposals|agent_events)\b",original,re.I):
        end=original.rfind(')')
        original=original[:end]+", _minder_order BIGSERIAL"+original[end:]
    pieces=[]
    for syntax,part in _segments(original):
        if params_present:
            part=part.replace('%','%%')
        if syntax:
            part=re.sub(r"\browid\b","_minder_order",part,flags=re.I)
            part=part.replace('?', '%s')
        pieces.append(part)
    result=''.join(pieces)
    if ignored:
        result+=" ON CONFLICT DO NOTHING"
    if replaced:
        result+=" ON CONFLICT(owner,kind,id) DO UPDATE SET version=EXCLUDED.version,body=EXCLUDED.body"
    return result


class PostgresConnection:
    def __init__(self,raw):
        self._raw=raw
    def execute(self,query,params=None):
        try:
            return self._raw.execute(postgres_sql(query,params is not None),params)
        except Exception as error:
            raise _error(error) from None
    def commit(self):
        try:
            self._raw.commit()
        except Exception:
            raise AppError("postgres_commit_outcome_unconfirmed",503) from None
    def rollback(self):
        self._raw.rollback()
    def close(self):
        self._raw.close()
    def __enter__(self):
        return self
    def __exit__(self,kind,error,traceback):
        try:
            self.rollback() if kind else self.commit()
        finally:
            self.close()


class PostgresStore(Store):
    engine="postgresql"
    persistence_mode="managed-postgresql"
    durability_status="configured_host_acceptance_pending"
    volume_root=None
    path=None # A DATABASE_URL is never a filesystem path or public/logged value.

    def __init__(self,dsn,*,schema="minder"):
        if not isinstance(dsn,str) or not dsn.strip():
            raise AppError("postgres_database_url_required",503)
        if not isinstance(schema,str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,62}",schema):
            raise AppError("postgres_schema_invalid",503)
        try:
            import psycopg
            from psycopg.conninfo import conninfo_to_dict
            config=conninfo_to_dict(dsn)
        except ImportError:
            raise AppError("postgres_driver_unavailable",503) from None
        except Exception:
            raise AppError("postgres_database_url_invalid",503) from None
        self.schema=schema
        self._dsn=dsn
        self._sslmode=config.get("sslmode") or ("disable" if config.get("host","").startswith('/')
            or config.get("host") in ("localhost","127.0.0.1","::1") else "require")
        self._initialize()

    def __repr__(self):
        return "<PostgresStore managed-postgresql redacted>"

    @classmethod
    def from_environment(cls,environ=None):
        env=os.environ if environ is None else environ
        return cls(env.get("DATABASE_URL"),schema=env.get("MINDER_DB_SCHEMA","minder"))

    def connect(self):
        raw = None
        try:
            import psycopg
            from psycopg import sql
            raw=psycopg.connect(self._dsn,sslmode=self._sslmode,connect_timeout=5,
                autocommit=True,row_factory=_row_factory)
            raw.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
            raw.execute("SET statement_timeout='15000ms'")
            raw.execute("SET lock_timeout='10000ms'")
            return PostgresConnection(raw)
        except Exception:
            if raw is not None:
                raw.close()
            raise AppError("postgres_unavailable",503) from None

    @contextmanager
    def transaction(self):
        db=self.connect()
        try:
            db.execute("BEGIN ISOLATION LEVEL READ COMMITTED")
            db.execute("SELECT pg_advisory_xact_lock(hashtext(current_database()),hashtext(?))",(self.schema,))
            yield db
            db.commit()
        except BaseException:
            try:db.rollback()
            except Exception:pass
            raise
        finally:
            db.close()

    def _initialize(self):
        from psycopg import sql
        with self.transaction() as db:
            try:
                db._raw.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(self.schema)))
                statements=(
                    "CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY)",
                    "CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,owner TEXT NOT NULL,created_at TEXT NOT NULL)",
                    "CREATE TABLE IF NOT EXISTS documents(owner TEXT,kind TEXT,id TEXT,version TEXT,body TEXT NOT NULL,PRIMARY KEY(owner,kind,id))",
                    "CREATE TABLE IF NOT EXISTS history(owner TEXT,kind TEXT,id TEXT,version TEXT,body TEXT NOT NULL,created_at TEXT,PRIMARY KEY(owner,kind,id,version))",
                    "CREATE TABLE IF NOT EXISTS drafts(owner TEXT,id TEXT,body TEXT,status TEXT,PRIMARY KEY(owner,id))")
                for statement in statements:
                    db.execute(statement)
                db.execute("INSERT OR IGNORE INTO migrations VALUES(1)")
                # Only current notice ordering uses these SQLite expressions.
                db._raw.execute("""CREATE OR REPLACE FUNCTION json_extract(document_value text,json_path text)
                    RETURNS text LANGUAGE SQL IMMUTABLE AS $$
                    SELECT CASE WHEN json_path LIKE '$.%' THEN document_value::jsonb #>>
                        string_to_array(substring(json_path from 3),'.') ELSE NULL END $$""")
                db._raw.execute("""CREATE OR REPLACE FUNCTION julianday(time_value text)
                    RETURNS double precision LANGUAGE SQL STABLE AS $$
                    SELECT coalesce(extract(epoch from time_value::timestamptz)::double precision/86400.0+2440587.5,
                        '-Infinity'::double precision) $$""")
            except AppError:
                raise
            except Exception as error:
                raise _error(error,"postgres_schema_unavailable") from None

    def backup(self,destination):
        raise AppError("postgres_backup_requires_provider_snapshot_or_pg_dump",503)

    @classmethod
    def on_volume(cls,*args,**kwargs):
        raise AppError("postgres_database_is_not_a_volume_path",503)
