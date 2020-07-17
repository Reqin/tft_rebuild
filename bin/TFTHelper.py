import os
import sys

os.chdir("../")
path = os.getcwd()
sys.path.append(path)

if __name__ == "__main__":
    from core import app

    app.start()
