import os
import sys


REQUIRED = (
    "QA_URL",
    "API_URL",
    "ADMIN_LOGIN_USR",
    "ADMIN_LOGIN_PSW",
    "ENFERMERIA_LOGIN_USR",
    "ENFERMERIA_LOGIN_PSW",
    "TURN_ROUTE",
    "STUDIES_ROUTE",
    "ANALYTICS_ROUTE",
)


def main() -> int:
    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        print("Configuración incompleta:")
        for name in missing:
            print(f"- {name}")
        return 1
    print("Configuración base del Sprint 11 completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
