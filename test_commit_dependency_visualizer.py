import unittest
from unittest.mock import patch, mock_open, MagicMock
import commit_dependency_visualizer as cdv

class TestCommitDependencyVisualizer(unittest.TestCase):

    def test_get_commits(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "a1b2c3d4\nb2c3d4e5 a1b2c3d4\n"
            mock_run.return_value.stderr = ""
            commits = cdv.get_commits('repo_path', '2024-01-01')
            expected = {
                'a1b2c3d4': [],
                'b2c3d4e5': ['a1b2c3d4']
            }
            self.assertEqual(commits, expected)

    def test_generate_mermaid_graph(self):
        commits = {
            'a1b2c3d4': [],
            'b2c3d4e5': ['a1b2c3d4']
        }
        mermaid_code = cdv.generate_mermaid_graph(commits)
        expected = (
            'graph TD;\n'
            '    a1b2c3d["a1b2c3d"];\n'
            '    b2c3d4e --> a1b2c3d;\n'
        )
        self.assertEqual(mermaid_code, expected)

    @patch("builtins.open", new_callable=mock_open)
    @patch("subprocess.run")
    def test_render_mermaid(self, mock_run, mock_open):
        cdv.render_mermaid('graph TD;', 'renderer_path', 'output.png')
        mock_open.assert_called_with('diagram.mmd', 'w')
        mock_open().write.assert_called_with('graph TD;')
        mock_run.assert_called_with('"renderer_path" -i diagram.mmd -o output.png', shell=True)

    @patch("os.startfile")
    def test_display_image_windows(self, mock_startfile):
        with patch('os.name', 'nt'):
            cdv.display_image('output.png')
            mock_startfile.assert_called_with('output.png')

    @patch("subprocess.run")
    def test_display_image_posix(self, mock_run):
        with patch('os.name', 'posix'):
            cdv.display_image('output.png')
            mock_run.assert_called_with(['open', 'output.png'], check=False)

if __name__ == '__main__':
    unittest.main()
