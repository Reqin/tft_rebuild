import os
import sys

os.chdir("../")

if __name__ == "__main__":
    from core import app

    app.start()
