from apexdevkit.server import UvicornServer

from Core.runner import setup

if __name__ == "__main__":
    UvicornServer.from_env().run(setup())
