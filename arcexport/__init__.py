# file __init__.py
import io
import os
import copy
import collections
import datetime

import json
import shlex

import nbformat

from traitlets.config.configurable import LoggingConfigurable
from traitlets.config import Config
from traitlets import default, HasTraits, Unicode, List, TraitError
from traitlets.utils.importstring import import_item
from ipython_genutils import text, py3compat

from nbconvert.exporters.templateexporter import TemplateExporter


class ArcExporter(TemplateExporter):
    """
    Arc Exporter
    """

    # If this custom exporter should add an entry to the
    # "File -> Download as" menu in the notebook, give it a name here in the
    # `export_from_notebook` class member
    export_from_notebook = "Arc"

    @default('file_extension')
    def _file_extension_default(self):
        """
        The new file extension is `.json`
        """
        return '.json'

    @property
    def template_path(self):
        """
        We want to inherit from HTML template, and have template under
        `./templates/` so append it to the search path. (see next section)
        """
        return super().template_path+[os.path.join(os.path.dirname(__file__), "templates")]

    @default('template_file')
    def _template_file_default(self):
        """
        We want to use the new template we ship with our library.
        """
        return 'arcexport'  # full

    output_mimetype = 'application/json'

    @default('raw_mimetypes')
    def _raw_mimetypes_default(self):
        return ['application/json', '']

    @property
    def default_config(self):
        c = Config({
            'ExtractOutputPreprocessor': {'enabled': True},
            'NbConvertBase': {
                'display_data_priority': ['text/plain']
            }
        })
        c.merge(super(ArcExporter, self).default_config)
        return c

    # override the default _preprocess function in nbconvert/exporters/exporter.py
    # this uses the default preprocessors then adds a custom one to convert inline sql into arc stages
    def _preprocess(self, nb, resources):
        """
        Preprocess the notebook before passing it into the Jinja engine.
        To preprocess the notebook is to successively apply all the
        enabled preprocessors. Output from each preprocessor is passed
        along to the next one.
        Parameters
        ----------
        nb : notebook node
            notebook that is being exported.
        resources : a dict of additional resources that
            can be accessed read/write by preprocessors
        """

        # Do a copy.deepcopy first,
        # we are never safe enough with what the preprocessors could do.
        nbc =  copy.deepcopy(nb)
        resc = copy.deepcopy(resources)

        # Run each preprocessor on the notebook.  Carry the output along
        # to each preprocessor
        for preprocessor in self._preprocessors:
            nbc, resc = preprocessor(nbc, resc)
            try:
                nbformat.validate(nbc, relax_add_props=True)
            except nbformat.ValidationError:
                self.log.error('Notebook is invalid after preprocessor %s',
                               preprocessor)
                raise


        # additional transformations
        def transform(cell):
            cell_copy = copy.deepcopy(cell)
            cell_copy.source = cell.source.lstrip()

            # transform %arc by removing first line
            if cell_copy.source.startswith('%arc'):
                cell_copy.source = '\n'.join(cell_copy.source.split('\n')[1::])
                return cell_copy

            # transform %sqlvalidate to JSON
            if cell_copy.source.startswith('%sqlvalidate'):
                params = dict(s.split('=', 1) for s in shlex.split(cell_copy.source.split('\n')[0])[1:])
                c = {}
                c['type'] = 'SQLValidate'
                c['name'] = params['name'] if 'name' in params else ''
                c['description'] = params['description'] if 'description' in params else ''
                c['environments'] = params['environments'].split(',') if 'environments' in params else []
                c['sql'] = (' ').join(map(lambda line: line.strip(), cell_copy.source.split('\n')[1::]))
                c['sqlParams'] = dict(kv.split('=') for kv in params['sqlParams'].split(',')) if 'sqlParams' in params else {}
                cell_copy.source = json.dumps(c, indent=2)
                return cell_copy

            # transform %sql to JSON
            if cell_copy.source.startswith('%sql'):
                params = dict(s.split('=', 1) for s in shlex.split(cell_copy.source.split('\n')[0])[1:])
                c = {}
                c['type'] = 'SQLTransform'
                c['name'] = params['name'] if 'name' in params else ''
                c['description'] = params['description'] if 'description' in params else ''
                c['environments'] = params['environments'].split(',') if 'environments' in params else []
                c['sql'] = (' ').join(map(lambda line: line.strip(), cell_copy.source.split('\n')[1::]))
                c['outputView'] = params['outputView'] if 'outputView' in params else ''
                c['persist'] = params['persist'] == 'true' if 'persist' in params else False
                c['sqlParams'] = dict(kv.split('=') for kv in params['sqlParams'].split(',')) if 'sqlParams' in params else {}
                cell_copy.source = json.dumps(c, indent=2)
                return cell_copy

            return cell_copy

        # Preprocess
        # filter only relevant cells
        nbc.cells = list(filter(lambda cell: cell.cell_type == 'code' and len(cell.source.strip()) != 0 and (not cell.source.lstrip().startswith('%') or cell.source.lstrip().startswith('%arc') or cell.source.lstrip().startswith('%sql')), nbc.cells))
        # transform relevant cells
        nbc.cells = list(map(transform, nbc.cells))

        return nbc, resc