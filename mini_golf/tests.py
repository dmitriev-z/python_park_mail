from ..minigolf.minigolf import Player, Match, HitsMatch, HolesMatch
from unittest import TestCase


class TestPlayer(TestCase):

    def test_player_name(self):
        expected_names = ['a', 'b', 'c']
        for name in expected_names:
            player = Player(name)
            self.assertEqual(name, player.name)


class TestMatch(TestCase):
    def setUp(self):
        self.match_generators = [(1, [Player('A')]), (1, [Player('A'), Player('B')]),
                                 (2, [Player('A'), Player('B')]), (2, [Player('A'), Player('B'), Player('C')]),
                                 (3, [Player('A'), Player('B'), Player('C')])]
        self.matches = [Match(1, [Player('A')]), Match(1, [Player('A'), Player('B')]),
                        Match(2, [Player('A'), Player('B')]), Match(2, [Player('A'), Player('B'), Player('C')]),
                        Match(3, [Player('A'), Player('B'), Player('C')])]

    def test_match_constructor(self):
        for match in self.match_generators:
            holes, players = match
            m = Match(holes, players)
            self.assertEqual(holes, m.holes)
            self.assertEqual(players, m.players)

    def test_hit(self):
        for match in self.matches:
            for i in range(match.holes):
                for player in match.players:
                    match.hit(success=True)
            with self.assertRaises(RuntimeError):
                match.hit()

    def test_match_is_finished(self):
        for match in self.matches:
            for i in range(match.holes):
                for player in match.players:
                    self.assertFalse(match.finished)
                    match.hit(success=True)
                if 0 < i < match.holes - 1:
                    self.assertFalse(match.finished)
            self.assertTrue(match.finished)

    def test_get_winners(self):
        for match in self.matches:
            for i in range(match.holes):
                for player in match.players:
                    with self.assertRaises(RuntimeError):
                        match.get_winners()
                    match.hit(success=True)
            self.assertEqual(match.get_winners(), match.players)

    def test_get_table(self):
        m = Match(2, [Player('A'), Player('B')])
        expected_table = [('A', 'B'),
                          (None, None),
                          (None, None)]
        self.assertEqual(expected_table, m.get_table())
        m.hit(success=True)
        expected_table = [('A', 'B'),
                          (1, None),
                          (None, None)]
        self.assertEqual(expected_table, m.get_table())
        m.hit()
        expected_table = [('A', 'B'),
                          (1, None),
                          (None, None)]
        self.assertEqual(expected_table, m.get_table())
        m.hit(success=True)
        expected_table = [('A', 'B'),
                          (1, 2),
                          (None, None)]
        self.assertEqual(expected_table, m.get_table())
        m.hit(success=True)
        expected_table = [('A', 'B'),
                          (1, 2),
                          (None, 1)]
        self.assertEqual(expected_table, m.get_table())
        m.hit()
        expected_table = [('A', 'B'),
                          (1, 2),
                          (None, 1)]
        self.assertEqual(expected_table, m.get_table())
        m.hit(success=True)
        expected_table = [('A', 'B'),
                          (1, 2),
                          (2, 1)]
        self.assertEqual(expected_table, m.get_table())


class TestHolesMatch(TestCase):

    def test(self):
        players = [Player('A'), Player('B'), Player('C')]
        m = HolesMatch(3, players)
        m.hit(True)  # 1
        m.hit()  # 2
        m.hit()  # 3

        for _ in range(10):
            for _ in range(3):
                m.hit() # 2, 3, 1

        for _ in range(9):
            for _ in range(3):
                m.hit() # 3, 1, 2
                print(m._players_scores[2])
                print(m.get_table())
        m.hit(True) # 3
        m.hit()  # 1
        m.hit(True)  # 2
