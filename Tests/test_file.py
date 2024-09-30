import unittest

from src.file import File


class TestFileClass(unittest.TestCase):

    def test_single_level_directory(self):
        # Тестирование файла в одном уровне каталога
        file = File("folder/file.txt", 1024)
        self.assertEqual(file.directory, "folder")
        self.assertEqual(file.name, "file.txt")
        self.assertEqual(file.length, 1024)

    def test_multi_level_directory(self):
        # Тестирование файла в многослойном каталоге
        file = File("folder/subfolder/file.txt", 2048)
        self.assertEqual(file.directory, "folder/subfolder")
        self.assertEqual(file.name, "file.txt")
        self.assertEqual(file.length, 2048)

    def test_root_level_file(self):
        # Тестирование файла на корневом уровне
        file = File("file.txt", 4096)
        self.assertEqual(file.directory, "")
        self.assertEqual(file.name, "file.txt")
        self.assertEqual(file.length, 4096)

    def test_empty_directory(self):
        # Тестирование файла с пустым путем (не должно возникнуть в реальной ситуации, но для покрытия тестов)
        file = File("", 512)
        self.assertEqual(file.directory, "")
        self.assertEqual(file.name, "")
        self.assertEqual(file.length, 512)

    def test_directory_with_trailing_slash(self):
        # Тестирование пути с завершающим слешем
        file = File("folder/subfolder/", 1024)
        self.assertEqual(file.directory, "folder/subfolder")
        self.assertEqual(file.name, "")
        self.assertEqual(file.length, 1024)

    def test_long_nested_directory(self):
        # Тестирование длинного пути с многослойными каталогами
        long_path = "/".join(["folder"] * 10) + "/file.txt"
        file = File(long_path, 8192)
        expected_directory = "/".join(["folder"] * 10)
        self.assertEqual(file.directory, expected_directory)
        self.assertEqual(file.name, "file.txt")
        self.assertEqual(file.length, 8192)
