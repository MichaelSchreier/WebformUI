import os

from flask import Flask
from flask.views import View
from flask import request, render_template

import build_command
import read_form
from append_form import addMetaInformation, finalizeForm


class RenderView(View):
	"""
	custom implementation of Flask-View-class handling all requests
	"""
	def __init__(self, path, template_name, queue_in, queue_out, app_dir=None, script_directory=None):
		self.path = path
		self.template_name = template_name
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.app_dir = app_dir
		self.script_directory = script_directory

		if path == '/save':
			self.save_dialog()
		if path == '/start':
			self.start_script()

	def dispatch_request(self):
		return render_template(self.template_name)

	def save_dialog(self):
		form = request.form.get("render", "")
		script_type = request.form.get("script_type_select", "")
		path = request.form.get("path_to_script_button", "")

		form = addMetaInformation(form, script_type, path)
		form = finalizeForm(form)

		if self.queue_out.full():
			self.template_name = "webform_ui_builder_error.html"
			return

		self.queue_out.put(form)

		while self.queue_in.empty():
			pass

		tmp = self.queue_in.get()
		if not tmp[1] or tmp[0] != 'save':
			self.template_name = "webform_ui_builder_error.html"
		else:
			self.template_name = "webform_ui_builder_saved.html"

	def start_script(self):
		path = os.path.join(
			self.app_dir,
			"templates",
			"webform_ui_form.tmp.html"  # self.page
		)

		# read meta information (type and name of script to execute) and create a dict with
		# mappings for select, radio and checkbox type inputs
		meta = read_form.readMetaInformation(path)
		input_mapping = read_form.interpretForm(path)

		arguments = []
		tmp = None

		# parse all form fields for user input
		for group in read_form.readFormGroups(path)[:-1]:
			group_label = group.find('label')['for']
			input_elements = read_form.readInputElements(group)[0]

			if group.find(id=input_elements)['type'] in ["select", "radio"]:
				if input_mapping[group_label]:
					tmp = input_mapping[group_label][request.form[group_label]]
				else:
					tmp = request.form[group_label]

			if group.find(id=input_elements)['type'] in ["text", "password"]:
				tmp = request.form[group_label]
				if not tmp:
					tmp = read_form.readPlaceholder(group)

			if group.find(id=input_elements)['type'] == "prependedtext":
				prepend = read_form.readInputAddon(group)

				raw_input = request.form[group_label]
				if not raw_input:
					raw_input = read_form.readPlaceholder(group)

				tmp = prepend + raw_input

			if group.find(id=input_elements)['type'] == "appendedtext":
				append = read_form.readInputAddon(group)

				raw_input = request.form[group_label]
				if not raw_input:
					raw_input = read_form.readPlaceholder(group)

				tmp = raw_input + append

			# files need to be copied because html does not allow to pass full file paths via a file selector
			if group.find(id=input_elements)['type'] == "file":
				file = request.files[group_label]
				if file.filename:
					file_path = os.path.join(
						self.app_dir,
						"temporary_files",
						file.filename + ".tmp"
					)
					file.save(file_path)
					tmp = file_path
				else:
					tmp = ''

			if group.find(id=input_elements)['type'] in ["checkbox", "selectmultiple"]:
				if input_mapping[group_label]:
					tmp = [input_mapping[group_label][x] for x in request.form.getlist(group_label)]
				else:
					tmp = request.form.getlist(group_label)

			arguments.append([group_label, tmp])

		# build and execute command from form inputs
		command = build_command.buildCommand(meta['type'], os.path.join(self.script_directory, meta['path']), arguments)
		build_command.runCommand(command)

		# set confirmation page
		self.template_name = "webform_ui_launched.html"


class webform_ui_app:
	"""
	wrapper for all Flask functionality
	"""
	def __init__(self, page, queue_in, queue_out, app_dir, script_directory):
		self.app = Flask("webformUI", static_folder="assets")
		self.page = page
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.app_dir = app_dir
		self.script_directory = script_directory

		self.app.add_url_rule('/', view_func=RenderView.as_view(
			'home',
			path='/',
			template_name=page,
			queue_in=queue_in,
			queue_out=queue_out,
			app_dir=app_dir
		))

		self.app.add_url_rule('/save', view_func=RenderView.as_view(
			'save',
			path='/save',
			template_name='',
			queue_in=queue_in,
			queue_out=queue_out
		), methods=['POST'])

		self.app.add_url_rule('/start', view_func=RenderView.as_view(
			'start',
			path='/start',
			template_name='',
			queue_in=queue_in,
			queue_out=queue_out,
			app_dir=app_dir,
			script_directory=script_directory
		), methods=['POST'])

	def run(self):
		self.app.run(use_reloader=False, threaded=True)
