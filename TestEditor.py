import unittest
import ApcEditor
import os
from ApcResEditor import ResXMLEditor
from pathlib import Path


class TestEditorMethods(unittest.TestCase):

    def test_editor_exist(self):
        editor = ApcEditor.Editor("./test/lol.txt")
        editor.open()
        self.assertEqual(editor.text, "hello")
        editor.edit("World")
        editor.save()
        old = editor.text
        editor.open()
        self.assertEqual(editor.text, old)
        editor.edit("hello")
        editor.save()

    def test_editor_notexist(self):
        editor = ApcEditor.Editor("./test/lol1.txt")
        editor.open()
        editor.edit("World")
        editor.save()
        old = editor.text
        editor.open()
        self.assertEqual(editor.text, old)
        os.remove("lol1.txt")

    def test_INIEditor(self):
        editor = ApcEditor.IniEditor("./test/lol.ini")
        editor.open()
        self.assertEqual(editor.ini_file["LoL"]["hello"], "World")
        print(editor)
        editor.save()
        editor.open()
        self.assertEqual(editor.ini_file["LoL"]["hello"], "World")
        editor.add_sections({"LoL": {'new': 'option'}})
        editor.save()
        editor.open()
        print(editor)
        self.assertEqual(editor.ini_file["LoL"]['new'], 'option')
        editor.remove_options({"LoL": {'new': 'option'}})
        editor.save()

    def test_XmlEditor_sections(self):
        editor = ApcEditor.XMLEditor("./test/ApcRegResources_2.xml")
        sections = editor.open()
        editor.add_sections({"TApcMetadataView": {"kk": "lol.ini"}})
        print(editor)
        editor.save()

    def test_XmlEditor_edit(self):
        editor = ApcEditor.XMLEditor("./test/lol.xml")
        sections = editor.open()
        editor.edit("<Key>Lool</Key>")
        print(editor)
        editor.save()

    def test_MetaInfoEditor(self):
        editor = ApcEditor.MetainfoEditor()
        sections = editor.open()
        print(super(ApcEditor.MetainfoEditor))
        print(sections)
        editor.update_sections({"ResLangs": ["Rus", "ENU"], 2: "ляля"})
        print(editor)
        editor.save()

    def test_ResEditor(self):
        ResXMLEditor.logger.setLevel("DEBUG")
        editor = ResXMLEditor(Path("./test/ResClMain/ApcRegResources.xml"))
        editor.open()
        editor.parse_sections()
        print(editor)


if __name__ == '__main__':
    unittest.main()
