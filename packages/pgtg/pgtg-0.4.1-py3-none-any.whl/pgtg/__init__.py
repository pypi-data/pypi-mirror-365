from gymnasium.envs.registration import register

from pgtg.environment import PGTGEnv

__version__ = "0.4.0"

register(id="pgtg-v3", entry_point="pgtg.environment:PGTGEnv")
