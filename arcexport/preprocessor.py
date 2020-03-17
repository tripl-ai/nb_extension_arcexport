"""A preprocessor that converts inline sql into json format.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import sys
import os
import json
import shlex

from nbconvert.preprocessors import Preprocessor

class ArcExporterPreprocessor(Preprocessor):

    def preprocess_cell(self, cell, resources, cell_index):

        print(cell)

        return cell, resources