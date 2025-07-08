import os

from configparser import ConfigParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR.parent / "config.ini"

parser = ConfigParser()
read_files = parser.read(CONFIG_FILE)

env = os.getenv("APP_ENV", "default")
section_name = "testdb" if env == "test" else "db"
print(f"used section: [{section_name}]")

if section_name not in parser:
    raise RuntimeError(f"Section [{section_name}] not found in config.ini")

section = parser[section_name]

class Settings:
    def __init__(self, section, env):
        self.env = env
        self.db_host = section["db_host"]
        self.db_name = section["db_name"]
        self.db_user = section["db_user"]
        self.db_password = section["db_password"]

        self.database_url = self.get_db_url()

        jwt_section = parser["jwt"]
        self.jwt_secret = jwt_section["jwt_secret"]
        self.jwt_algorithm = jwt_section["jwt_algorithm"]
        self.jwt_expire_minutes = int(jwt_section["jwt_expire_minutes"])

        server_section = parser["server"]
        self.host = server_section["host"]
        self.port_backend = server_section["port_backend"]
        self.port_frontend = server_section["port_frontend"]
        self.log_level = server_section["log_level"]
        self.public_ip = server_section["public_ip"]

        application_section = parser["application"]
        self.poweredby = application_section["poweredby"]
        self.root_mount = application_section.get("root_mount", None)

        contact_section = parser["contact"]
        self.contact_name = contact_section["name"]
        self.contact_email = contact_section["email"]
        self.contact_url = contact_section["url"]
        self.contact_tos = contact_section["tos"]
        self.contact_privpol = contact_section["privpol"]

        smtp_section = parser["SMTP"]
        self.sender_email  = smtp_section["sender_email"]
        self.smtp_password  = smtp_section["smtp_password"]
        self.smtp_server  = smtp_section["smtp_server"]
        self.smtp_port  = int(smtp_section["smtp_port"])

    def get_db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"


def get_settings(env: str = None) -> Settings:
    if env is None:
        env = os.getenv("APP_ENV", "default")

    if env == "test":
        section = parser["testdb"]
    else:
        section = parser["db"]

    return Settings(section, env)

settings = get_settings()
