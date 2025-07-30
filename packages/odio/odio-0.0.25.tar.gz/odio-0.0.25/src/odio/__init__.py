import xml.dom.minidom
import zipfile


class OdioException(Exception):
    pass


def create_spreadsheet(version="1.3"):
    if version == "1.1":
        raise OdioException(
            f"Version '{version}' isn't supported for creating spreadsheets. Use "
            f"versions 1.3 or 1.2 instead."
        )
    elif version == "1.2":
        import odio.v1_2

        return odio.v1_2.create_spreadsheet()
    elif version == "1.3":
        import odio.v1_3

        return odio.v1_3.create_spreadsheet()
    else:
        raise Exception(
            f"The version '{version}' isn't recognized. The valid version strings "
            f"are '1.1', '1.2' and '1.3'."
        )


def parse_document(f):
    with zipfile.ZipFile(f, "r") as z:
        dom = xml.dom.minidom.parseString(z.read("META-INF/manifest.xml"))
        version = dom.documentElement.getAttribute("manifest:version")

        if version == "1.1":
            import odio.v1_1

            return odio.v1_1.parser.parse_node(dom)
        elif version == "1.2":
            import odio.v1_2

            return odio.v1_2.parse_document(z)
        elif version == "1.3":
            import odio.v1_3

            return odio.v1_3.parse_document(z)
        else:
            raise Exception(
                f"The version '{version}' isn't recognized. The valid version strings "
                f"are '1.1', '1.2' and '1.3'."
            )


def parse_text(f):
    with zipfile.ZipFile(f, "r") as z:
        content = z.read("content.xml")
    f.close()
    dom = xml.dom.minidom.parseString(content)
    version = dom.documentElement.getAttribute("office:version")
    text_elem = dom.getElementsByTagName("office:text")[0]

    if version == "1.1":
        import odio.v1_1

        return odio.v1_1.TextReader(text_elem)
    elif version == "1.2":
        import odio.v1_2

        return odio.v1_2.TextReader(text_elem)
    elif version == "1.3":
        import odio.v1_3

        return odio.v1_3.TextReader(text_elem)
    else:
        raise Exception(
            f"The version '{version}' isn't recognized. The valid version strings "
            f"are '1.1', '1.2' and '1.3'."
        )
