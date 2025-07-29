import os
from os.path import sep
import shutil


class DirectoryPaths(object):
    def __init__(self,
                 file_path: str = '',
                 delete_all: bool = False,
                 delete_figures: bool = False,
                 figures_folder: str | None = None,
                 figures_subset_folder=''):
        file_path = os.path.expanduser(file_path)
        self._file_path = file_path
        self._file_directory = os.path.dirname(os.path.abspath(file_path))
        self.file_basename_path = os.path.abspath(os.path.splitext(file_path)[0])
        self.delete_all = delete_all
        self.delete_figures = delete_figures
        self._figures_folder = figures_folder
        if self._figures_folder is None:
            self._figures_folder = os.path.join(self._file_directory, 'figures')
        if (self.delete_all or self.delete_figures) and os.path.exists(self._figures_folder):
            try:
                shutil.rmtree(self._figures_folder)
            except OSError:
                print((OSError.message))
        # data_directory = os.path.join(self._file_directory, '.data')
        # if self.delete_all and os.path.exists(data_directory):
        #     try:
        #         shutil.rmtree(data_directory)
        #     except OSError:
        #         print((OSError.message))
        # if not os.path.exists(data_directory):
        #     os.makedirs(data_directory)
        self.data_dir = None
        self.figures_subset_folder = figures_subset_folder

    def set_file_path(self, value):
        self._file_path = value

    def get_file_path(self):
        if not os.path.exists(self._file_path):
            os.makedirs(self._file_path)
        return self._file_path

    file_path = property(get_file_path, set_file_path)

    def set_file_directory(self, value):
        self._file_directory = value

    def get_file_directory(self):
        if not os.path.exists(self._file_directory):
            os.makedirs(self._file_directory)
        return self._file_directory

    file_directory = property(get_file_directory, set_file_directory)

    def get_figures_folder(self):
        if not os.path.exists(self._figures_folder):
            os.makedirs(self._figures_folder)
        return self._figures_folder

    def set_figures_folder(self, value):
        self._figures_folder = value

    figures_folder = property(get_figures_folder, set_figures_folder)

    def get_figure_basename_path(self):
        return os.path.join(self.figure_subset_path, os.path.basename(self.file_path).split('.')[0])

    figure_basename_path = property(get_figure_basename_path)

    def get_data_basename_path(self):
        return os.path.join(self.data_subset_path, os.path.basename(self.file_path).split('.')[0])

    data_basename_path = property(get_data_basename_path)

    def get_figure_subset_path(self):
        _path = os.path.join(self._figures_folder, self.figures_subset_folder) + sep
        if not os.path.exists(_path):
            os.makedirs(_path)
        return _path

    figure_subset_path = property(get_figure_subset_path)

    def get_data_subset_path(self):
        _path = os.path.join(self.data_dir, self.figures_subset_folder)
        if not os.path.exists(_path):
            os.makedirs(_path)
        return _path

    data_path = property(get_data_subset_path)
    figures_current_dir = property(get_figure_subset_path)
