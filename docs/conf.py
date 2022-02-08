extensions = ['myst_parser']
templates_path = ['_templates']
master_doc = 'index'
project = u'Spack-Manager'
copyright = u'Phil Sakievich'
author = u'Phil Sakievich'
version = u'0.1'
release = u'0.1'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
numfig = True
numfig_format = {'figure': '%s', 'table': '%s', 'code-block': '%s'}
html_theme = 'sphinx_rtd_theme'
html_static_path = []
html_show_copyright = False
htmlhelp_basename = 'spack-manager-doc'
latex_elements = {
}
latex_documents = [
    (master_doc, 'spack-manager.tex', u'Spack-Manager Documentation',
     author, 'manual'),
]
man_pages = [
    (master_doc, 'spack-manager', u'Spack-Manager Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'spack-manager', u'Spack-Manager Documentation',
     author, 'Spack-Manager', 'One line description of project.',
     'Miscellaneous'),
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
