# file __init__.py
import os
import os.path

from traitlets import default
from traitlets.config import Config

from nbconvert.exporters.templateexporter import TemplateExporter


class ArcExporter(TemplateExporter):
    """
    Arc Exporter
    """

    # If this custom exporter should add an entry to the
    # "File -> Download as" menu in the notebook, give it a name here in the
    # `export_from_notebook` class member
    export_from_notebook = "Arc"

    # first process the notebook
    preprocessors = ['arcexport.ArcExporterPreprocessor']

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
