# TODO
def before_start(func):
    return func
def app_exit():
    return 

@before_start
def start(app_main_func):
    app_main_func()
    return app_exit()

def init():
    return True