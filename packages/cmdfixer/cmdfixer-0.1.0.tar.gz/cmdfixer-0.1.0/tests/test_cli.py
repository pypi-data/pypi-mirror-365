import unittest
import subprocess

class TestCLI(unittest.TestCase):
    def test_cli_typo(self):
        result = subprocess.run([
            'python', '-m', 'fix_cmd.cli', 'git sttaus'
        ], capture_output=True, text=True)
        self.assertIn('Suggested command: git status', result.stdout)

    def test_cli_no_suggestion(self):
        result = subprocess.run([
            'python', '-m', 'fix_cmd.cli', 'notarealcommand'
        ], capture_output=True, text=True)
        self.assertIn('Suggested command: <no suggestion>', result.stdout)

if __name__ == '__main__':
    unittest.main()
