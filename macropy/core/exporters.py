"""Functions that are nice to have but really should be in the python library"""

class NullExporter(object):
    def __init__(self, root):
        pass

    def export_transformed(self, tree, module_name):
        print module_name
        pass