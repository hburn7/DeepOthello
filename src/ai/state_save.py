import json
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


class StateSaveDecoder:
    def __init__(self):
        super().__init__()
        self.data = json.loads('data.json')

    def find_best_move(self, bits_black, bits_white, current_player) -> None | SavedMoveData:
        for d in self.data:
            if np.uint64(d['bits_black']) == bits_black and np.uint64(d['bits_white']) == bits_white \
                    and int(d['current_player']) == current_player:
                best_res = d['results'][0]
                # todo...come back



        return None
