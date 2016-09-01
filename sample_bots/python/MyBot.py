from ants import Ants
from HunterBot import HunterBot
from FerrariBot import FerrariBot

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        Ants.run(FerrariBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
