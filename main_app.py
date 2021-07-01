from __init__ import app
import config as cfg

#
# Don't remove next lines 
from view import routes
from db_oracle import UserLogin

print("APP TestingAdmin ready for start")


if __name__ == "__main__":
    val = "The Main function !"
    print("APP TestingAdmin starting")
    app.run(host=cfg.host, port=cfg.port, debug=False)
