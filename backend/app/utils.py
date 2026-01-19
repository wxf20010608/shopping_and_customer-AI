from passlib.context import CryptContext
import os
from pathlib import Path

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # bcrypt 限制密码长度不超过 72 字节
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt 限制密码长度不超过 72 字节
    if isinstance(plain_password, str):
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def load_env(path: str | None = None) -> None:
    candidates = []
    if path:
        candidates.append(Path(path))
    base = Path(__file__).resolve().parent
    # backend/.env
    candidates.append(base.parent / ".env")
    # app/.env（备选）
    candidates.append(base / ".env")
    # 项目根目录 .env（备选）
    candidates.append(base.parent.parent / ".env")
    # 工作目录 .env（备选）
    candidates.append(Path.cwd() / ".env")
    loaded = False
    loaded_path = None
    for p in candidates:
        try:
            if p.is_file():
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        key = k.strip()
                        val = v.strip()
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        # 避免后续重复项用空值覆盖已有非空值
                        if val == "" and os.environ.get(key):
                            continue
                        os.environ[key] = val
                loaded = True
                loaded_path = str(p)
                break
        except Exception:
            pass
    if not loaded:
        return
    try:
        os.environ["ENV_LOADED_PATH"] = loaded_path or ""
    except Exception:
        pass

