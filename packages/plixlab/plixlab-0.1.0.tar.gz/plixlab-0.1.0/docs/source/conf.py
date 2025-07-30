# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import shutil
import glob
sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'plix'
copyright = '2024, Giuseppe Romano'
author = 'Giuseppe Romano'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
#extensions = ['import_example',
#              'sphinx_copybutton'
#               ]

extensions = [
              'sphinx_copybutton',\
              'import_example',
               ]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'

html_theme = 'sphinx_book_theme'
html_favicon = '_static/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


html_css_files = [
    'custom.css',
]


def copy_web_and_reference_files(app, exception):
    # --- Copy entire web/ folder to _static/web ---
    web_src_dir = os.path.abspath(os.path.join(app.confdir, '..', '..', 'web'))
    web_dst_dir = os.path.join(app.outdir, '_static', 'web')
    

    # Remove old destination if it exists, then copy entire directory
    if os.path.exists(web_dst_dir):
        shutil.rmtree(web_dst_dir)
    shutil.copytree(web_src_dir, web_dst_dir)

    # --- Copy *.plx from ../../tests/reference to _static/reference ---
    ref_src_dir = os.path.abspath(os.path.join(app.confdir, '..', '..', 'tests', 'reference'))
    ref_dst_dir = os.path.join(app.outdir, '_static', 'reference')
    
    os.makedirs(ref_dst_dir, exist_ok=True)

    for plx_path in glob.glob(os.path.join(ref_src_dir, '*.plx')):
        dst_path = os.path.join(ref_dst_dir, os.path.basename(plx_path))
        shutil.copy2(plx_path, dst_path)


def setup(app):
    app.connect('build-finished', copy_web_and_reference_files)

