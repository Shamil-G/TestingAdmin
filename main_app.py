from __init__ import app
import config as cfg

#
# Ни в коем случае не удалять строки ниже, иначе APP не узнает свои контексты
from view import routes
from db_oracle import UserLogin

print("Приложение APP готовится к запуску")


if __name__ == "__main__":
    val = "The Main function !"
    print("Приложение APP запускается")
    app.run(host=cfg.host, port=cfg.port, debug=False)
