import sublime, sublime_plugin, subprocess, thread, os, functools, glob, fnmatch, re

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
		s = sublime.load_settings("SBT.sublime-settings")
		#print(s.has("sbt_path"))
		self.SBT = s.get("sbt_path")
		self.PLAY = s.get("play_path")
		#print("SBT PATH: "+ SBT)

	def test_if_playapp(self):
		self.play_base_dir = self.current_file.partition("/test/")[0]
		print("Checking if: "+ self.play_base_dir + "/conf/routes")
		if os.path.exists(self.play_base_dir + "/conf/routes"):
			return True
		else:
			return False

	def run_command(self, sbt_command, commander):
		#print(sbt_command)
		self.view = commander.view
		self.load_config()
		self.current_file = self.view.file_name()
		#print(self.current_file)
		self.base_dir = self.current_file.partition("/test/scala/")[0]
		self.project_dir = self.base_dir.replace("/src", "")
		self.package_name = self.current_file.replace(self.base_dir + "/test/scala/", "").replace("/", ".").replace(".scala", "")

		if sbt_command == "run-main":
			if "/test/scala" in self.current_file: 
				sbt_command = "\"test:run-main "+ self.package_name +"\""
			else:
				sbt_command = "\"run-main "+ self.package_name +"\""
		elif sbt_command == "test-only":
			sbt_command = sbt_command +" "+ self.package_name

		if self.test_if_playapp():
			self.package_name = self.current_file.replace(self.play_base_dir+ "/test/", "").replace("/", ".").replace(".scala", "")
			self.project_dir = self.play_base_dir
			self.SBT = self.PLAY
			sbt_command = "test-only" + " " + self.package_name


		self.show_tests_panel()
		command = wrap_in_cd(self.project_dir, self.SBT + " " + sbt_command)
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
		(cur_row, _) = self.output_view.rowcol(self.output_view.size())
		self.output_view.show(self.output_view.text_point(cur_row, 0))

		self.output_view.set_read_only(False)
		self.output_view.settings().set("syntax", "Packages/SBTRunner/TestConsole.tmLanguage")
		self.output_view.settings().set("color_scheme", "Packages/SBTRunner/TestConsole.hidden-tmTheme")
		data = re.sub(r'\033\[\d*(;\d*)?\w', '', data)
		data = re.sub(r'.\x08', '', data)

		
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
