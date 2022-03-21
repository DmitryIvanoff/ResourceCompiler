import unittest
from pathlib import Path
from ApcWorkObj import ApcCompiler, Path
import os
import shutil
from stat import S_IWRITE

ApcCompiler.services["Google"].set_token(str(Path(__file__).parent.joinpath("API/GoogleAPI_cred.json")))
ApcCompiler.set_abbreviations()
ApcCompiler.set_log_level("DEBUG")


class TestWorkObj(unittest.TestCase):
    def test_validation(self):
        wd = Path("./test/ResClMain").resolve()
        xml_file = "ApcRegResources.xml"
        compiler = ApcCompiler(xml_file, wd=wd)
        langs = ["AZE"]
        compiler.update_json(langs)
        compiler.save()

    def test_spec_validation(self):
        wd = Path("./test/test_spec/ResClMain").resolve()
        xml_file = "ApcRegResources.xml"
        compiler = ApcCompiler(xml_file, wd=wd)
        langs = ["AZE"]
        compiler.update_json(langs)
        compiler.save()

    def test_compilation(self):
        wd = Path("./test/ResClMain")
        xml_file = "ApcRegResources.xml"
        json_file = "Resources.json"
        compiler = ApcCompiler(xml_file, json_file, wd)
        compiler.save()

    def test_all(self):
        src = Path("C:/Ivanov/p4/main/current/Apacs30/Modules/ApcClientExtensions/ApcClExtMap/ResClMain")
        wd = Path("./test/ResClMain")
        self._refresh_wd(src, wd)
        # xml_file = "ApcRegResources.xml"
        # json_file = "Resources.json"
        # compiler = ApcCompiler(xml_file, json_file, wd)
        # langs = ["AZ"]
        # compiler.validate_json(langs)
        # compiler.compile_json()

    def test_repair_format(self):
        rus = '%2%. Считыватель "%1%", "ГД" 5%. <Не задано> %n%s%d __redirect(ApcSoftwarePackage, COMMON, SoftwarePackage) %1% "%2%" пользователь: %strHolderName% (Системный адрес: %4%), температура: %5% °C %n'
        wd = Path("./test/ResClMain")
        compiler = ApcCompiler(wd=wd)
        enu = compiler.translate(rus, "ENU", service="Google")
        compiler.logger.info(enu)
        self.assertEqual(
            r'%2%. Reader "%1%", "SG" 5%. <Not set> %n%s%d __redirect(ApcSoftwarePackage, COMMON, SoftwarePackage) %1% "%2%" user: %strHolderName% (System address: %4%), temperature: %5% °C %n',
            enu)

    def test_some_symbols(self):
        rus = '%%Всем, привет. <Не задано>%n__redirect(ApcSoftwarePackage, COMMON, SoftwarePackage) <А что происходит> 1<2 Не задано %isOffLineEvent% план %? %  %5% 5 мг/л.  '
        wd = Path("./test/ResClMain")
        compiler = ApcCompiler(wd=wd)
        enu = compiler.translate(rus, "UKR", service="Google")
        self.assertEqual('%%Всім привіт. <Не задано>%n__redirect(ApcSoftwarePackage, COMMON, SoftwarePackage) <А що відбувається> 1<2 Не налаштовано %isOffLineEvent% план %? %  %5% 5 мг/л.  ', enu)

    def test_some_symbols2(self):
        rus = 'Ключ "%1%" не выдан %2%, уровень алкоголя — %5% мг/л'
        wd = Path("./test/ResClMain")
        compiler = ApcCompiler(wd=wd)
        enu = compiler.translate(rus, "UKR", service="Google")
        self.assertEqual('Ключ "%1%" не видано %2%, рівень алкоголю - %5% мг/л', enu)

    def test_some_symbols3(self):
        rus = 'Ключ "%1%" не выдан %2%,%nуровень алкоголя — %5% мг/л'
        wd = Path("./test/ResClMain")
        compiler = ApcCompiler(wd=wd)
        enu = compiler.translate(rus, "UKR", service="Google")
        self.assertEqual('Ключ "%1%" не видано %2%,%nрівень алкоголю - %5% мг/л', enu)

    def test_some_symbols4(self):  # слишком сложный формат все равно портится((
        rus = 'Ключ "%1%" не выдан %2%%n-%n-%n%sуровень алкоголя — %5% мг/л  90%'
        wd = Path("./test/ResClMain")
        compiler = ApcCompiler(wd=wd)
        enu = compiler.translate(rus, "UKR", service="Google")
        self.assertEqual('Ключ "%1%" не видано %2%%n-%n-%n%sрівень алкоголю - %5% мг/л  90%', enu)

    @staticmethod
    def _refresh_wd(src, wd):
        def onerror(st, path, info):
            p = Path(path)
            p.chmod(S_IWRITE)
            os.remove(p)

        if wd.exists():
            os.chmod(wd, mode=S_IWRITE)
            shutil.rmtree(wd, onerror=onerror)
        shutil.copytree(src, wd)


if __name__ == '__main__':
    unittest.main()
