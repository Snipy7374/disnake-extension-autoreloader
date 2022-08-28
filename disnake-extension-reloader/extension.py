from __future__ import annotations
import os

from typing import List, Optional, Tuple, Union, Set, TYPE_CHECKING

from watchfiles import awatch

if TYPE_CHECKING:
    from disnake.ext.commands import Bot


class ExtensionLoader:
    def __init__(
        self,
        *,
        paths: Union[str, List[str]],
        project_path: str,
        ignore_paths: Optional[Union[str, List[str]]] = None,
        extension_loader_debug: Optional[bool] = False,
        bot: Bot,
    ) -> None:

        self.paths = paths
        self.files: Set[str] = set()
        self.project_path = project_path
        self.ignore_paths = ignore_paths
        self.ignored_files: Set[str] = set()

        self.awatch_generator = awatch(self.project_path)
        self.extension_loader_debug = extension_loader_debug
        self.bot = bot

        self._populate_files()
        self._populate_ignored_files()

    def __repr__(self) -> str:
        return f"<ExtensionLoader paths={self.paths}\
 project_path='{self.project_path}'\
 ignore_paths={self.ignore_paths}\
 files={self.files} awatch_generator_at='{self.awatch_generator}'\
 bot='{self.bot}'>"

    @staticmethod
    def _is_all_dir(paths: List[str]) -> bool:
        for i in paths:
            if os.path.isdir(i):
                continue

            else:
                return False
        return True

    @staticmethod
    def _is_all_files(*files: Tuple[str]) -> bool:
        for i in files:
            if os.path.isfile(i):
                continue

            else:
                return False
        return True

    def __get_files_from_dirs(self, paths: List[str]) -> List[str]:
        return [
            os.path.abspath("/".join((i, file)))
            for i in paths
            if os.path.isdir(os.path.abspath(i))
            for file in os.listdir(i)
            if file.endswith(".py")
        ]

    def __get_files(self, *files: Tuple[str]) -> List[str]:
        return [
            os.path.abspath(file)
            for file in files
            if os.path.isfile(os.path.abspath(file))
        ]

    def __get_files_and_dirs(self, paths: List[str]) -> List[str]:
        files = self.__get_files(*self.paths)
        files_from_dirs = self.__get_files_from_dirs(self.paths)
        return files + files_from_dirs

    def _populate_ignored_files(self) -> None:
        # Populate self.ignored_files with the files given as
        # directory or as file

        if self.ignore_paths is None:
            return

        if isinstance(self.ignore_paths, list):
            if self._is_all_dir(self.ignore_paths):
                self.ignored_files.update(self.__get_files_from_dirs(self.ignore_paths))

            elif self._is_all_files(*self.ignore_paths):
                self.ignored_files.update(self.__get_files(*self.ignore_paths))

            else:
                self.ignored_files.update(self.__get_files_and_dirs(self.ignore_paths))

        elif isinstance(self.ignore_paths, str):
            if os.path.isdir(self.ignore_paths):
                self.ignored_files.update(
                    self.__get_files_from_dirs([self.ignore_paths])
                )

            elif os.path.isfile(os.path.abspath(self.ignore_paths)):
                self.ignored_files.add(os.path.abspath(self.ignore_paths))

        self.files = self.files - self.ignored_files

    def _populate_files(self) -> None:
        # Populate self.files with all the files given as
        # directory or as file
        # if a file or directory is not found the corresponding file/dir
        # will not be added to self.files

        if isinstance(self.paths, list):
            if self._is_all_dir(self.paths):
                self.files.update(self.__get_files_from_dirs(self.paths))

            elif self._is_all_files(*self.paths):
                self.files.update(self.__get_files(*self.paths))

            else:
                self.files.update(self.__get_files_and_dirs(self.paths))

        elif isinstance(self.paths, str):
            if os.path.isdir(self.paths):
                self.files.update(self.__get_files_from_dirs([self.paths]))

            elif os.path.isfile(self.paths):
                self.files.add(os.path.abspath(self.paths))

    @classmethod
    def default_dir(cls, *, bot: Bot) -> ExtensionLoader:
        return cls(paths="./", project_path="./", bot=bot)

    @staticmethod
    def __find_path_difference(path1: str, path2: str) -> List[str]:
        ls_path1 = [path1[i] for i in range(len(path1))]
        ls_path2 = [path2[i] for i in range(len(path2))]

        for char in ls_path1:
            ls_path2.remove(char)

        return ls_path2

    async def watch_for_changes(self) -> None:
        async for changes in self.awatch_generator:
            x = next(iter(changes))
            count = 0

            for i in self.files:
                if "__pycache__" in os.path.dirname(os.path.normpath(x[1])):
                    continue
                
                print(f'\n\n{self.files}\n\n')
                if os.path.samefile(os.path.normpath(i), os.path.normpath(x[1])):

                    ext = self.__find_path_difference(
                        os.path.normpath(os.path.abspath(self.project_path)),
                        os.path.normpath(x[1]),
                    )
                    _module_path = "".join(ext)

                    x = os.path.normpath(_module_path).replace("\\", ".")[:-3]
                    _cog_path = f"{x[1:]}"
                    try:
                        if _cog_path not in self.bot.extensions:
                            self.bot.load_extension(_cog_path)
                            
                            if self.extension_loader_debug and count==0:
                                print(f"[WARNING] '{_cog_path}' was not already loaded, i'm loading it for the first time!\nIt's suggested to use this module only to reload changed file extension.\nFor an example head over https://guide.disnake.dev/getting-started/using-cogs (this message cannot be silenced, however it's shown only for the first loaded extension)")
                        
                        
                        elif _cog_path in self.bot.extensions:
                            self.bot.reload_extension(_cog_path)
                            print("Extension reloaded")
                        count += 1

                    except Exception as error:
                        print(error)


# x = ExtensionLoader(
#       paths=['./'],
#       project_path='./',
#       ignore_paths=['./main_example.py', './__init__.py'],
#       bot='sus'
#     )
# print(x)
