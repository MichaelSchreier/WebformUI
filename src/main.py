import os
import shutil
import sys
import webbrowser

from multiprocessing import Queue, Process, freeze_support

from class_ui_native import webformUI_gui
from class_ui_web import webform_ui_app


def startFlask(page, q_to_flask, q_to_gui, app_dir, script_directory):
	"""
	Sets up and starts the Flask/Werkzeug server that runs the web interface
	"""
	app = webform_ui_app(page, q_to_flask, q_to_gui, app_dir, script_directory)

	templates_dir = app_dir + "\\templates"
	app.app.template_folder = templates_dir

	app.run()


def main(argv):
	page = 'webform_ui_form.tmp.html'
	q_to_flask = Queue(1)
	q_to_gui = Queue(1)

	if getattr(sys, 'frozen', False):
		app_dir = os.path.dirname(os.path.abspath(sys.executable))
	else:
		app_dir = os.path.dirname(os.path.realpath(__file__))
	templates_dir = app_dir + "\\templates"
	tmp_page = templates_dir + "\\webform_ui_form.tmp.html"

	if len(argv) > 1:
		file_in = ' '.join(argv[1:])
	else:
		file_in = templates_dir + "\\webform_ui_builder_main.html"
	if os.path.isfile(file_in):
		shutil.copy(file_in, tmp_page)
		page = "webform_ui_form.tmp.html"

	webbrowser.open("http://127.0.0.1:5000", autoraise=True)

	flask_process = Process(
		target=startFlask,
		args=(
			page,
			q_to_flask,
			q_to_gui,
			app_dir,
			os.path.dirname(file_in)
		)
	)

	flask_process.start()
	webformUI_gui(page, q_to_gui, q_to_flask, app_dir)

	flask_process.terminate()
	flask_process.join()

	if os.path.isfile(tmp_page):
		os.remove(tmp_page)

	raise SystemExit


if __name__ == "__main__":
	freeze_support()  # required for multiprocessing module to work with pyinstaller
	main(sys.argv)
