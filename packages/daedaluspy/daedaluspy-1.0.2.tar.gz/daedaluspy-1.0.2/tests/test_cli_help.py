import subprocess

def test_daedaluspy_cli_help():
    result = subprocess.run(['python', '-m', 'daedaluspy', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'DaedalusPy' in result.stdout or 'usage' in result.stdout.lower()
