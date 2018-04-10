from itertools import cycle


class Player:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class Match:
    def __init__(self, holes_count, players):
        self._holes = holes_count
        self._players = players
        self._results = [[None] * len(self._players)] * (self._holes + 1)
        self._results[0] = (tuple(player.name for player in self._players))
        order_list = [i for i in range(len(self._players))]
        self._players_order = {}
        self._players_scores = {}
        self._players_results = {}
        for i in range(self._holes):
            self._players_order[i] = cycle(tuple(order_list))
            self._players_scores[i] = [0] * len(players)
            self._players_results[i] = [None] * len(players)
            switch_player = order_list.pop(0)
            order_list.append(switch_player)

    @property
    def players(self):
        return self._players

    @property
    def holes(self):
        return self._holes

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError("Match is complete")
        else:
            _current_hole = self._get_current_hole()
            _next_player = self._get_hitting_player(_current_hole)
            self._write_result(success, _current_hole, _next_player)

    @property
    def finished(self):
        for table_string in self._players_results.values():
            if not all(table_string):
                return False
        return True

    def get_winners(self):
        if not self.finished:
            raise RuntimeError("Match is not complete yet")
        else:
            if isinstance(self, HolesMatch):
                is_reversed = True
            else:
                is_reversed = False
            winners = []
            players_match_scores = {i: 0 for i in range(len(self.players))}
            for players_scores in self._players_scores.values():
                for player_index in range(len(players_scores)):
                    players_match_scores[player_index] += players_scores[player_index]
            high_score = sorted(set(players_match_scores.values()), reverse=is_reversed)[0]
            for player, player_score in players_match_scores.items():
                if player_score == high_score:
                    winners.append(self._players[player])
            return winners

    def get_table(self):
        for i in range(1, self._holes + 1):
            hole_result = [None] * len(self._players)
            for k in range(len(hole_result)):
                if self._players_results[i - 1][k]:
                    hole_result[k] = self._players_scores[i - 1][k]
                else:
                    hole_result[k] = None
            self._results[i] = tuple(hole_result)
        return self._results

    def _get_current_hole(self):
        for hole in self._players_results.keys():
            if not all(self._players_results[hole]):
                return hole

    def _get_hitting_player(self, current_hole):
        if current_hole is None:
            return
        players_cycle = self._players_order[current_hole]
        player_index = next(players_cycle)
        while self._players_results[current_hole][player_index]:
            player_index = next(players_cycle)
        return player_index

    def _write_result(self, success, current_hole, hitting_player):
        if current_hole is None or hitting_player is None:
            return
        self._players_scores[current_hole][hitting_player] += 1
        self._players_results[current_hole][hitting_player] = success


class HitsMatch(Match):

    def _write_result(self, success, current_hole, hitting_player):
        if current_hole is None or hitting_player is None:
            return
        self._players_scores[current_hole][hitting_player] += 1
        self._players_results[current_hole][hitting_player] = success
        if self._players_scores[current_hole][hitting_player] == 9:
            self._players_scores[current_hole][hitting_player] += 1
            self._players_results[current_hole][hitting_player] = True


class HolesMatch(Match):

    def _write_result(self, success, current_hole, hitting_player):
        if current_hole is None or hitting_player is None:
            return
        self._players_scores[current_hole][hitting_player] += 1
        self._players_results[current_hole][hitting_player] = success
        if any(self._players_results[current_hole]):
            self._players_scores[current_hole] = [0] * len(self._players_scores[current_hole])
            for i in range(len(self._players_results[current_hole])):
                if self._players_results[current_hole][i]:
                    self._players_scores[current_hole][i] = 1
        elif self._players_scores[current_hole] == [10] * len(self._players_scores[current_hole]):
            self._players_scores[current_hole] = [0] * len(self._players_scores[current_hole])
            self._players_results[current_hole] = [True] * len(self._players_results[current_hole])
            return
        if None not in self._players_results[current_hole] and any(self._players_results[current_hole]):
            self._players_results[current_hole] = [True] * len(self._players_results[current_hole])
        elif None not in self._players_results[current_hole] and not any(self._players_results[current_hole]):
            self._players_results[current_hole] = [None] * len(self._players_results[current_hole])
