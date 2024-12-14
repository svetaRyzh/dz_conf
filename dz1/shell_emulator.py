import os
import zipfile
import toml
import datetime
import unittest

class ShellEmulator:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = toml.load(f)
            self.username = self.config.get('username')
            self.vfs_path = self.config.get('vfs_path')
            self.current_dir = '/'
            self.command_history = []

    def _get_file_content(self, path):
        """Возвращает содержимое файла из виртуальной файловой системы."""
        with zipfile.ZipFile(self.vfs_path, 'r') as zf:
            with zf.open(path.lstrip('/')) as f:
                return f.read().decode('utf-8')

    def _get_dir_content(self, path):
        """Возвращает список файлов и подкаталогов в виртуальном каталоге."""
        with zipfile.ZipFile(self.vfs_path, 'r') as zf:
            return [f.filename for f in zf.infolist() if f.filename.startswith(path.lstrip('/'))]

    def _get_full_path(self, path):
        """Возвращает полный путь к файлу/каталогу относительно корня VFS."""
        return os.path.join(self.current_dir, path)

    def ls(self, path=''):
        """Выводит список файлов и подкаталогов в текущем каталоге."""
        full_path = self._get_full_path(path)
        dir_content = self._get_dir_content(full_path)
        if dir_content:
            for file in dir_content:
                print(file)
            return dir_content
        else:
            print("No files found in the directory.")
            return "No files found in the directory."

    def cd(self, path):
        """Переходит в указанный каталог."""
        full_path = self._get_full_path(path)
        if full_path.startswith('/'):
            self.current_dir = full_path
        else:
            self.current_dir = os.path.join(self.current_dir, path)

    def exit(self):
        """Выход из эмулятора."""
        print("Exiting shell emulator.")
        exit()

    def date(self):
        """Выводит текущую дату и время."""
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def chown(self, path, user):
        """Изменяет владельца файла."""
        print(f"chown: {user} {path}")
        return f"chown: {user} {path}"

    def history(self):
        """Выводит историю выполненных команд."""
        if self.command_history:
            for i, command in enumerate(self.command_history):
                print(f"{i+1}: {command}")
            return self.command_history 
        else:
            print("No commands in history.")
            return "No commands in history."

    def run(self):
        """Запускает эмулятор."""
        while True:
            command = input(f"{self.username}@{self.current_dir}$ ")
            self.command_history.append(command)
            try:
                args = command.split()
                command_name = args[0]
                if hasattr(self, command_name):
                    getattr(self, command_name)(*args[1:])
                else:
                    print(f"Unknown command: {command_name}")
            except Exception as e:
                print(f"Error: {e}")

# Тесты
class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        self.emulator = ShellEmulator('config.toml')

    def test_ls_empty(self):
        self.emulator.cd('/empty_dir')
        self.emulator.ls()
        self.assertEqual(self.emulator.ls(), "No files found in the directory.")

    def test_ls_files(self):
        self.emulator.ls('/test_dir')
        self.assertIn("test_dir/file1.txt", self.emulator.ls())
        self.assertIn("test_dir/file2.txt", self.emulator.ls())

    def test_cd_root(self):
        self.emulator.cd('/')
        self.assertEqual(self.emulator.current_dir, '/')

    def test_cd_subdir(self):
        self.emulator.cd('test_dir')
        self.assertEqual(self.emulator.current_dir, '/test_dir')

    def test_date(self):
        self.emulator.date()
        self.assertIsInstance(self.emulator.date(), str)

    def test_chown(self):
        self.emulator.chown('test_dir/file1.txt', 'user1')
        self.assertEqual(self.emulator.chown('test_dir/file1.txt', 'user1'), "chown: user1 test_dir/file1.txt")

    def test_history_empty(self):
        self.assertEqual(self.emulator.history(), "No commands in history.")

    def test_history_filled(self):
        self.emulator.run()
        self.emulator.ls()
        self.emulator.cd('test_dir')
        history = self.emulator.history()
        self.assertIn("ls", history)
        self.assertIn("cd test_dir", history)

if __name__ == '__main__':
    emulator = ShellEmulator('config.toml')  
    emulator.run()
    '''unittest.main()'''
