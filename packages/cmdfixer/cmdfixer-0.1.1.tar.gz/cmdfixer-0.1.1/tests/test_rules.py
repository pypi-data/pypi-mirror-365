import unittest
from fix_cmd.rules import suggest_correction

class TestSuggestCorrection(unittest.TestCase):
    def test_git_status_typo(self):
        self.assertEqual(suggest_correction('git sttaus'), 'git status')
    def test_git_commit_typo(self):
        self.assertEqual(suggest_correction('git cmomit'), 'git commit')
    def test_ls_typo(self):
        self.assertEqual(suggest_correction('lsit'), 'ls')
    def test_kubectl_typo(self):
        self.assertEqual(suggest_correction('kubctl'), 'kubectl')
    def test_no_suggestion(self):
        self.assertEqual(suggest_correction('randomcmd'), '<no suggestion>')

if __name__ == '__main__':
    unittest.main()
