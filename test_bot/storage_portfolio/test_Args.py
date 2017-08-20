import unittest

from bot.storage_portfolio.Args import Args


class TestArgsStoragePortfolio(unittest.TestCase):
    def test_list(self):
        args = Args("pf list")
        self.assertTrue(args.parse().is_list())

    def test_select(self):
        args = Args("pf select my_first_portfolio")
        self.assertTrue(args.parse().is_select())

    def test_current(self):
        args = Args("pf current")
        self.assertTrue(args.parse().is_current())

    def test_save(self):
        args = Args("pf save bfds3r2fe2efdslfakj2f2 my_first_portfolio")
        self.assertTrue(args.parse().is_save())

    def test_add(self):
        args = Args("pf add AFLT 2 34.2")
        self.assertTrue(args.parse().is_add())

    def test_rm(self):
        args = Args("pf rm AFLT 2")
        self.assertTrue(args.parse().is_rm())

    def test_delete(self):
        args = Args("pf delete my_first_portfolio")
        self.assertTrue(args.parse().is_delete())

    def test_stat(self):
        args = Args("pf stat")
        self.assertTrue(args.parse().is_stat())

    def test_compare(self):
        args = Args("pf compare my_second_portfolio")
        self.assertTrue(args.parse().is_compare())

