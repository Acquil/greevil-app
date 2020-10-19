from xml.dom.minidom import Document


class XmlTransformer(object):
    """
    Builds an XML from a python dictionary
    """
    doc = None

    def __init__(self, data: dict):

        self.doc = Document()

        if len(data) == 1:
            # only one root element
            root_name = str(list(data)[0])
        else:
            # set "response" as default root element
            root_name = "response"

        self.root = self.doc.createElement(root_name)
        self.doc.appendChild(self.root)
        # Build XML
        self.build(self.root, data[root_name])

    def build(self, parent, structure):
        """
        Recursively build XML
        :param parent: same as structure, initially root tag
        :param structure: dictionary, list or number/string
        :return: None
        """
        if type(structure) == dict:
            for item in structure:
                tag = self.doc.createElement(item)
                parent.appendChild(tag)
                self.build(tag, structure[item])

        elif type(structure) == list:

            grand_parent = parent.parentNode
            tag_name = parent.tagName
            grand_parent.removeChild(parent)

            for list_item in structure:
                tag = self.doc.createElement(tag_name)
                self.build(tag, list_item)
                grand_parent.appendChild(tag)

        # Take int/float/double/string as string
        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            parent.appendChild(tag)

    def unlink(self):
        """
        Unlink all children
        :return: None
        """
        self.doc.unlink()
        return None

    def __repr__(self):
        """
        For repr()
        :return: string
        """
        return self.doc.toprettyxml("")

    def __str__(self):
        """
        For print()
        :return: string
        """
        return self.doc.toprettyxml(indent="\t")
