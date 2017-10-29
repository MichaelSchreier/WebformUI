import os
import tkinter as tk
import webbrowser

from tkinter import filedialog


class webformUI_gui:
	"""
	Main GUI class to control webformUI server
	"""
	def __init__(self, tmp_page, queue_in, queue_out, app_dir=None):
		self.tmp_page = tmp_page
		self.queue_in = queue_in
		self.queue_out = queue_out
		self.app_dir = app_dir
		self.root = tk.Tk()
		self.root.title("")
		self.root.iconbitmap(os.path.join(app_dir, 'assets/img/logo.ico'))
		self.root.geometry("200x100")
		self.root.resizable(0, 0)

		title_label = tk.Label(self.root, text="Webform UI", bg="royal blue", fg="White", font="SegoeUI 10 bold")
		exit_button = tk.Button(self.root, text="Exit", command=self.quitGUI)
		delete_button = tk.Button(self.root, text="Delete temporary files", command=self.deleteTempFiles)
		website_button = tk.Button(self.root, text="Open in browser", command=self.openPage)

		title_label.pack(fill=tk.X)
		exit_button.pack(fill=tk.X)
		delete_button.pack(fill=tk.X)
		website_button.pack(fill=tk.X)

		self.root.lift()
		self.root.after(100, self.pollQueue)
		tk.mainloop()

	def quitGUI(self):
		self.root.destroy()

	def deleteTempFiles(self):
		tmp_folder = os.path.join(self.app_dir, "temporary_files")
		for file in os.listdir(tmp_folder):
			if os.path.isfile(os.path.join(tmp_folder, file)):
				os.remove(os.path.join(tmp_folder, file))

	@staticmethod
	def openPage():
		webbrowser.open("http://127.0.0.1:5000", autoraise=True)

	def pollQueue(self):
		if not self.queue_in.empty():
			self.queue_out.put(['save', self.savefiledialog(self.queue_in.get())])

		self.root.after(100, self.pollQueue)

	def savefiledialog(self, form):
		self.root.lift()
		file_path = filedialog.asksaveasfilename(filetypes=(("WebForm UIs", "*.wui"), ("all files", "*.*")))

		base, ext = os.path.splitext(file_path)
		if not ext and base:
			ext = ".wui"
		path = base + ext
		try:
			with open(path, 'w') as f:
				f.write(form)
			return True
		except Exception:
			return False
