import json
from pathlib import Path

import numpy as np

from dataclasses import dataclass


@dataclass()
class SavedMoveData:
    pos: int
    pos_str: str
    wins: int
    visits: int
    ratio: float

class StateSave:
    def __init__(self, bits_black: np.uint64, bits_white: np.uint64, current_player: int, results: list[SavedMoveData]):
        self.bits_black = bits_black
        self.bits_white = bits_white
        self.current_player = current_player
        self.results = results

    def to_json(self):
        data = {
            'bits_black': str(self.bits_black),
            'bits_white': str(self.bits_white),
            'current_player': self.current_player,
            'results': [
                {
                    r.pos:
                        {
                            'move_str': r.pos_str,
                            'wins': r.wins,
                            'visits': r.visits,
                            'ratio': r.wins / r.visits
                        }
                } for r in self.results]
        }

        return json.dumps(data, indent=4)

    def find_best_move(self):
        return self.results[0]


class StateSaveDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__()

        if Path('data.json').exists():
            with open('data.json', 'r') as f:
                self.data = json.load(f)

                # convert str to dict
                self.data = [self._as_dict(d) for d in self.data]

        else:
            self.data = None

    def find_best_move(self, bits_black: np.uint64, bits_white: np.uint64, current_player: int) -> None | SavedMoveData:
        if self.data is None:
            return None

        for d in self.data:
            d = self._as_dict(d)
            if np.uint64(d['bits_black']) == bits_black and np.uint64(d['bits_white']) == bits_white \
                    and int(d['current_player']) == current_player:
                # Data is stored sorted by best ratio first
                best_key = next(iter(d['results'][0]))  # Move pos as str
                best_val = d['results'][0][best_key]  # All other properties

                return SavedMoveData(int(best_key), best_val['move_str'], best_val['wins'], best_val['visits'], best_val['ratio'])

        return None
    def _as_dict(self, d: str):
        """Loads a formatted JSON string into a dictionary"""
        return json.loads(d)
