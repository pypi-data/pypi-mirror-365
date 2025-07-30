
import os
from pathlib import Path
import pwd
import subprocess
import psutil

from liminal import config
from liminal.logging import LOGGER


class Shell:


	def __init__(self, exec_path: Path | None = None):
		if not exec_path:
			self.exec_path = self.get_default_shell_path()
		else:
			self.exec_path = exec_path
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
			'default': self.get_default_shell_path().as_posix(),
			'current': self.this_process_shell_path().as_posix(),
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


def determine_shell_user_promptable() -> Shell:
	"""get the shell obj for a user. prompts them to specifiy shell if there is an unexpected difference"""

	default_shell = Shell()
	current_shell_path = default_shell.this_process_shell_path()
	default_shell_path = default_shell.get_default_shell_path()

	if current_shell_path == default_shell_path:
		return default_shell
	
	LOGGER.debug(f'Shell paths differ: {default_shell_path=} {current_shell_path=}')
	
	if path := config.Config.LIMINAL_INSTALLER_SHELL_PATH:
		return Shell(exec_path=Path(path))

	from rich.prompt import IntPrompt
	from rich.console import Console

	console = Console()
	console.print(f'Your default shell is [italic]{default_shell_path}[/], but your current shell is [italic]{current_shell_path}[/]')
	console.print("[bold]Which would you like to use?")
	
	shell_choices=[default_shell_path.as_posix(), current_shell_path.as_posix(),]

	for i, choice in enumerate(shell_choices):
		msg = f'  [cyan]{i+1}[/cyan]. {choice}'
		if i == 0:
			msg += f'   [italic](default)'
		console.print(msg)

	console.print("[italic](If you're not sure, choose default (1))[/]")
	selection_idx = IntPrompt.ask(
		'Enter the number of your choice',
		choices=[str(i+1) for i in range(len(shell_choices))],
		# default=default_index+1, # no default so user has to type instead of just press enter (ive done too hasty of an enter many times)
		show_choices=False, # i think =True is more confusing to casual users
	)
	selected_shell_path = shell_choices[selection_idx - 1]
	LOGGER.debug(f'user {selected_shell_path=}')
	return Shell(exec_path=Path(selected_shell_path))


if __name__ == '__main__':
	s = determine_shell_user_promptable()
