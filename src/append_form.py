import os
from bs4 import BeautifulSoup, Tag


def addMetaInformation(html, type=None, path=None):
    """
    read and return the information stored in the <meta> tag(s)
    """
    # parse form
    if os.path.isfile(html):
        with open(html) as h:
            form = BeautifulSoup(h, 'lxml')
    else:
        form = BeautifulSoup(html, 'lxml')

    if not form.head:
        new_tag = Tag(builder=form.builder, name="head")
        form.find().insert(0, new_tag)

    # prepend meta information tag
    new_tag = Tag(builder=form.builder, name="meta", attrs={"type": type, "path": path})
    form.head.insert(0, new_tag)

    return str(form)


def finalizeForm(html):
    """
    take html from the form builder and add meta-information, html-wrappings etc.
    """
    # parse form
    if os.path.isfile(html):
        with open(html) as h:
            form = BeautifulSoup(h, 'lxml')
    else:
        form = BeautifulSoup(html, 'lxml')

    # add <head>-tags
    if not form.head:
        new_tag = Tag(builder=form.builder, name="head")
        form.find().insert(0, new_tag)

    # add title
    new_tag = Tag(builder=form.builder, name="title")
    new_tag.string = "Webform Script Launcher"
    form.head.insert(0, new_tag)

    # add link to css files
    new_tag = Tag(builder=form.builder, name="link",
                  attrs={"href": "assets/css/lib/bootstrap.min.css", "rel": "stylesheet"})
    form.head.insert(1, new_tag)

    new_tag = Tag(builder=form.builder, name="link", attrs={"href": "assets/css/custom.css", "rel": "stylesheet"})
    form.head.insert(2, new_tag)

    # add action to form
    form.form['action'] = '/start'
    form.form['method'] = 'POST'

    # format form into column
    new_tag = Tag(builder=form.builder, name="div", attrs={"class": "col-md-6"})
    form.form.wrap(new_tag)

    # add submit button
    new_tag = Tag(builder=form.builder, name="div", attrs={"class": "form-group"})
    form.fieldset.append(new_tag)

    new_tag = Tag(builder=form.builder, name="button",
                  attrs={"id": "savebutton", "type": "submit", "class": "btn btn-primary", "name": "savebutton"})
    new_tag.string = "Submit"
    form.find_all('div')[-1].append(new_tag)

    return str(form.prettify())
