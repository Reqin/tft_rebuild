from modules.config.config import defaultConfig as config

def setState(state):
    with open(config['engine.path_state'],'w') as f:
        f.write(str(state))

def getState():
    with open(config['engine.path_state'],'rb') as f:
        state = f.readline().decode()
        return int(state)