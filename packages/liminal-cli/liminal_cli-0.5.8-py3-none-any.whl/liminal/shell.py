
import os
from pathlib import Path
import pwd
import subprocess
import psutil


class Shell:


	def __init__(self):
		self.exec_path = self.get_default_shell_path()
		self.name = self.exec_path.name
		self.config_file = Path.home() / '.bashrc' if self.is_bash() else Path.home() / '.zshrc'
		self.history_file = Path.home() / '.bash_history' if self.is_bash() else Path.home() / '.zsh_history'

		# {
		# 	'bash': ['.bashrc', '.bash_profile', '.bash_login', '.profile'],
		# 	'zsh': ['.zshrc', '.zshenv', '.zprofile', '.zlogin']
		# }

	def _envvar(self, name: str) -> str | None:
		return os.environ.get(name)
	
	def _envvar_dict(self, names: list[str]) -> dict[str, str | None]:
		result = {}
		for name in names:
			result[name] = self._envvar(name)
		return result

	def dict(self):
		return {
			'name': self.exec_path.name,
			'exec_path': self.exec_path.as_posix(),
			'version': subprocess.run([self.exec_path, '--version'], check=False, capture_output=True, text=True, timeout=1).stdout,
			'envvar': self._envvar_dict([
				'SHLVL', 'TERM', 'HOME',
				'PS1',
				'PROMPT_COMMAND', 'RPROMPT', 'PROMPT_SUBST',
	 		]),			
		}

	def is_supported(self):
		return self.exec_path.name in ['bash', 'zsh']
	
	def is_bash(self):
		return self.exec_path.name == 'bash'

	def get_default_shell_path(self) -> Path:
		"""Gets the default shell for the current user."""
		# NOTE: we also have shellingham installed (dependency of typer)
		user_id = os.getuid()
		user_info = pwd.getpwuid(user_id)
		return Path(user_info.pw_shell)
		
	def this_process_shell_path(self) -> Path:
		parent_pid = os.getppid()
		parent_process = psutil.Process(parent_pid)
		# .exe() gives the full path, .name() just the command name (e.g., 'bash')
		# We prefer .exe() for uniqueness
		shell_exe = parent_process.exe()
		return Path(shell_exe)
	

	def try_parse_login_command(self):
		from liminal.command_runner import run_test_login_command, PS1ParseException
		import uuid
		key = str(uuid.uuid4())
		try:
			output = run_test_login_command(self.exec_path.as_posix(), key)
		except PS1ParseException as e:
			raise e
		# TODO: search syslog
		# assert output and key in output, f'Did not find {key=} in {output=}'


def path_replace_home_with_var(path: Path) -> str:
	_path = path.expanduser()
	
	if _path.is_relative_to(Path.home()):
		_path = '$HOME' / _path.relative_to(Path.home())

	return _path.as_posix()
