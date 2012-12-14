import sublime, sublime_plugin, subprocess, thread, os, functools, glob, fnmatch

class SbtTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command("test-only", self)

class SbtRunCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command("run-main", self)

class SbtCompile(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command("compile", self)

class SbtClean(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command("clean", self)

class SbtUpdate(sublime_plugin.TextCommand):
	def run(self, edit):
		CommandRunner().run_command("update", self)

class CommandRunner():
	def load_config(self):
		s = sublime.load_settings("SBTRunner.sublime-settings")
		global SBT; SBT = s.get("sbt_path")

	def run_command(self, sbt_command, commander):
		#print(sbt_command)
		self.view = commander.view
		self.load_config()
		current_file = self.view.file_name()
		print(current_file)
		self.base_dir = current_file.partition("/test/scala/")[0]
		self.project_dir = self.base_dir.replace("/src", "")
		package_name = current_file.replace(self.base_dir + "/test/scala/", "").replace("/", ".").replace(".scala", "")
		if sbt_command == "run-main":
			if "/test/scala" in current_file: 
				sbt_command = "\"test:run-main "+ package_name +"\""
			else:
				sbt_command = "\"run-main "+ package_name +"\""
		elif sbt_command == "test-only":
			sbt_command = sbt_command +" "+ package_name

		self.show_tests_panel()
		command = wrap_in_cd(self.project_dir, SBT + " " + sbt_command)
		self.proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		thread.start_new_thread(self.read_stdout, ())
		thread.start_new_thread(self.read_stderr, ())

	def read_stdout(self):
		self.copy_stream_to_output_view(self.proc.stdout)

	def read_stderr(self):
		self.copy_stream_to_output_view(self.proc.stderr)

	def copy_stream_to_output_view(self, stream):
		while True:
			data = os.read(stream.fileno(), 2**15)

			if data != "":
				sublime.set_timeout(functools.partial(self.append_data, self.proc, data), 0)
			else:
				stream.close()
				break		

	def window(self):
		return self.view.window()

	def append_data(self, proc, data):
		self.output_view.set_read_only(False)
		#self.output_view.settings().set("syntax", "Packages/SublimeSBTRunner/TestConsole.tmLanguage")
		#self.output_view.settings().set("color_scheme", "Packages/SublimeSBTRunner/TestConsole.hidden-tmTheme")
		edit = self.output_view.begin_edit()
		self.output_view.insert(edit, self.output_view.size(), data)
		self.output_view.end_edit(edit)
		self.output_view.set_read_only(True)

	def show_tests_panel(self):
		if not hasattr(self, 'output_view'):
			self.output_view = self.window().get_output_panel("tests")
		self.clear_test_view()
		self.window().run_command("show_panel", {"panel": "output.tests"})

	def clear_test_view(self):
		self.output_view.set_read_only(False)
		edit = self.output_view.begin_edit()
		self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
		self.output_view.end_edit(edit)
		self.output_view.set_read_only(True)

def wrap_in_cd(path, command):
	return 'cd ' + path.replace("\\", "/") + ' && ' + command
