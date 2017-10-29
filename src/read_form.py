from bs4 import BeautifulSoup


def readFormGroups(form):
	"""
	:param form: form as html or BeautifulSoup
	:return: list of form inputs
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')
		
	return form.find_all('div', class_='form-group')
	
	
def readInputElements(form):
	"""
	:param form: form as html or BeautifulSoup
	:return: list of names of form inputs
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')
		
	form_elements = form.find_all(['input', 'select', 'textarea'])
	form_element_names = [i['id'] for i in form_elements]
	
	return form_element_names
	
	
def readMetaInformation(form):
	"""
	:param form: form as html or BeautifulSoup
	:return: list of information stored in <meta> tag(s)
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')
	
	return form.head.meta.attrs
	

def readInputAddon(form):
	"""
	:param form: form as html or BeautifulSoup
	:return: text of 'prepend' and 'append' field(s)
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')
	
	return form.find('div', class_='input-group-addon').string
	
	
def readPlaceholder(form):
	"""
	:param form: form as html or BeautifulSoup
	:return: FIRST placeholder text
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')
	
	for i in form.find_all('input'):
		if i.has_attr('placeholder'):
			return i['placeholder']
	
	return None

	
def interpretForm(form):
	"""
	Determines the mappings for e.g. select fields where the input selected by the user is different from what argument
	is to be submitted to the script.

	:param form: form as html or BeautifulSoup
	:return: key:value pairs for all form inputs
	"""
	if type(form) is str:
		with open(form, 'r') as h:
			form = BeautifulSoup(h, 'lxml')

	form_mapping = {}
	
	for group in readFormGroups(form)[:-1]:
		label = group.find('label')['for']
		argument_container = group.find(
			lambda tag: 
				(tag.name == 'div' or tag.name == 'select') and 
				tag.has_attr('arguments')
		)
		
		if argument_container:
			arguments = argument_container['arguments']
			arguments = arguments.split(',')
			
			keys = argument_container.find_all(['input', 'option'])
			keys = [key.string.strip() if key.string else key['value'] for key in keys]
			
			form_mapping[label] = {}
			for key, argument in zip(keys, arguments):
				form_mapping[label][key] = argument
		else:
			form_mapping[label] = None
	
	return form_mapping
