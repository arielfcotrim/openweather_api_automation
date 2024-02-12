import os


class PathManager:
    @staticmethod   # static method is used to access the method without creating an object of the class
    def get_project_root_directory():
        # __file__ is the path of the current file
        # internal: os.path.dirname() returns the directory name of the file
        # external: os.path.dirname() returns the parent directory of the file's directory (move up 2 levels)
        return os.path.dirname(os.path.dirname(__file__))

    @staticmethod
    def get_relative_path(*args):
        root_path = PathManager.get_project_root_directory()

        # os.path.join() is used to join the root path with the arguments provided
        # resulting in a full path to the file
        # *args is being used to accept any number of arguments to form the path as needed
        # join() will take care of the correct path separator (e.g. \ or / or // or \\ etc.)
        return os.path.join(root_path, *args)
