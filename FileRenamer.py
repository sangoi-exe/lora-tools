import logging
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Set, Tuple


# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class FileRenamer:
    def __init__(self, base_name: str):
        self.base_name = base_name
        self.counter = 1

    def select_directory(self) -> Path:
        """Opens a window to select a directory and returns the selected path."""
        root = Tk()
        root.withdraw()  # Hides the main Tk window
        root.attributes("-topmost", True)  # Keeps the selection window on top
        try:
            directory = filedialog.askdirectory(title="Select the directory for renaming")
            if directory:
                return Path(directory)
            else:
                logging.warning("No directory selected.")
                raise ValueError("No directory selected.")
        finally:
            root.destroy()  # Ensures the Tk window is destroyed

    def rename_files(self, directory: Path) -> None:
        """Renames files in the specified directory and its subdirectories."""
        logging.info(f"Starting renaming in directory: {directory}")

        files = [item for item in directory.iterdir() if item.is_file()]
        subdirectories = [item for item in directory.iterdir() if item.is_dir()]

        # Categorize files by extension
        files_by_extension: dict[str, Set[Path]] = {}
        for file in files:
            files_by_extension.setdefault(file.suffix.lower(), set()).add(file)

        png_files = files_by_extension.get(".png", set())
        txt_files = files_by_extension.get(".txt", set())
        json_files = files_by_extension.get(".json", set())
        npz_files = files_by_extension.get(".npz", set())

        # Find pairs of PNG and TXT files with the same base name
        pairs = self.find_pairs(png_files, txt_files)

        # Sort the pairs by PNG file names
        sorted_pairs = sorted(pairs, key=lambda x: x[0].name)

        # Rename the paired files
        for png_file, txt_file, json_file, npz_file in sorted_pairs:
            new_base_name = f"{self.base_name}_{str(self.counter).zfill(3)}"
            try:
                self.rename_file(png_file, directory / f"{new_base_name}.png")
                self.rename_file(txt_file, directory / f"{new_base_name}.txt")

                if json_file and json_file in json_files:
                    self.rename_file(json_file, directory / f"{new_base_name}.json")

                if npz_file and npz_file in npz_files:
                    self.rename_file(npz_file, directory / f"{new_base_name}.npz")

                self.counter += 1
            except Exception as e:
                logging.error(f"Error renaming files: {e}")

        # Recursively process subdirectories
        for subdir in subdirectories:
            self.rename_files(subdir)

    def find_pairs(self, png_files: Set[Path], txt_files: Set[Path]) -> Set[Tuple[Path, Path, Path, Path]]:
        """Finds pairs of PNG and TXT files with the same base name."""
        pairs = set()
        txt_names = {file.stem: file for file in txt_files}

        for png_file in png_files:
            base_name = png_file.stem
            txt_file = txt_names.get(base_name)
            if txt_file:
                json_file = png_file.with_suffix(".json")
                npz_file = png_file.with_suffix(".npz")
                pairs.add((png_file, txt_file, json_file, npz_file))
        return pairs

    def rename_file(self, original: Path, new: Path) -> None:
        """Renames a file from original to new."""
        if new.exists():
            logging.warning(f"The file {new} already exists and will be overwritten.")
        original.rename(new)
        logging.info(f"Renamed: {original.name} to {new.name}")


def main():
    base_name = "Aracy01102024"
    renamer = FileRenamer(base_name)

    try:
        directory = renamer.select_directory()
        renamer.rename_files(directory)
        logging.info("Renaming completed successfully.")
    except Exception as e:
        logging.error(f"Renaming process failed: {e}")


if __name__ == "__main__":
    main()
