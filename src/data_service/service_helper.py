import glob
import os
import os.path


class ServiceHelper:
    @staticmethod
    def remove_tmp_folder(path):
        print(f"Removing temp folder: {path}")
        if os.path.isdir(path):
            try:
                filelist = glob.glob(os.path.join(path, "*.*"))
                for f in filelist:
                    os.remove(f)
            except OSError as exception:
                print(
                    f"Removing temp folder error: {exception.filename} - {exception.strerror}.")
        elif os.path.isfile(path):
            print(
                f"Removing a file: {path}")
            os.remove(path)
            print(
                f"Removing a file succeed: {path}")
        else:
            raise RuntimeError("Path is not a file or directory.")
