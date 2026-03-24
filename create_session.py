import os
from pathlib import Path

from dotenv import dotenv_values
from telethon import TelegramClient


def main():
    project_root = Path(__file__).resolve().parent
    env_path = project_root / ".env"

    if not env_path.exists():
        raise FileNotFoundError(f".env topilmadi: {env_path}")

    env = dotenv_values(env_path)

    api_id_raw = env.get("TG_API_ID")
    api_hash = env.get("TG_API_HASH")

    if not api_id_raw or not api_hash:
        raise ValueError(".env ichida TG_API_ID va TG_API_HASH bo'lishi shart")

    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise ValueError("TG_API_ID raqam bo'lishi kerak") from exc

    default_session = env.get("TG_SESSION_NAME", "sessions/userbot_session")

    session_name = input(
        f"Session nomi kiriting (default: {default_session}_2): "
    ).strip()
    if not session_name:
        session_name = f"{default_session}_2"

    session_path = (project_root / f"{session_name}.session").parent
    session_path.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(str(project_root / session_name), api_id, api_hash)
    client.start()
    print(f"✅ Session yaratildi: {session_name}.session")
    client.disconnect()


if __name__ == "__main__":
    main()
