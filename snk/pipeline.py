from pathlib import Path
import sys
from typing import Optional
from git import Repo, InvalidGitRepositoryError

from snk.cli.config.utils import get_version_from_config


class Pipeline:
    """
    Represents a pipeline.
    Attributes:
      path (Path): The path to the pipeline.
      repo (Repo): The git repository of the pipeline.
      name (str): The name of the pipeline.
    """

    def __init__(self, path: Path) -> None:
        """
        Initializes a Pipeline object.
        Args:
            path (Path): The path to the pipeline.
        Returns:
            None
        Notes:
            Initializes the `repo` and `name` attributes.
        """
        self.path = path
        if path.is_symlink():  # editable mode
            self.repo = None
        else:
            try:
                self.repo = Repo(path)
            except InvalidGitRepositoryError:
                self.repo = None
        self.name = self.path.name

    @property
    def tag(self):
        """
        Gets the tag of the pipeline.
        Returns:
            str: The tag of the pipeline, or None if no tag is found.
        """
        try:
            # TODO: default to commit
            tag = self.repo.git.describe(["--tags", "--exact-match"])
        except Exception:
            tag = None
        return tag
    
    @property
    def version(self):
        """
        Gets the version of the pipeline.
        Returns:
            str: The version of the pipeline, or None if no version is found.
        """
        if (self.path / "snk.yaml").exists():
            version = get_version_from_config(self.path / "snk.yaml")
        else:
            version = self.tag
        return version if version else "latest"

    @property
    def executable(self):
        """
        Gets the executable of the pipeline.
        Returns:
            Path: The path to the pipeline executable.
        """
        pipeline_bin_dir = self.path.parent.parent / "bin"
        name = self.name
        if sys.platform.startswith("win"):
            name += ".exe"
        return pipeline_bin_dir / name

    @property
    def editable(self):
        """Is the pipeline editable?"""
        return self.path.is_symlink()

    def _find_folder(self, name) -> Optional[Path]:
        """Search for folder"""
        if (self.path / name).exists():
            return self.path / name
        if (self.path / "workflow" / name).exists():
            return self.path / "workflow" / name
        return None

    @property
    def profiles(self):
        pipeline_profile_dir = self._find_folder("profiles")
        if pipeline_profile_dir:
            return [p for p in pipeline_profile_dir.glob("*") if p.is_dir()]
        return []

    @property
    def environments(self):
        pipeline_environments_dir = self._find_folder("envs")
        if pipeline_environments_dir:
            return [e for e in pipeline_environments_dir.glob("*.yaml")] + [
                e for e in pipeline_environments_dir.glob("*.yml")
            ]
        return []

    @property
    def scripts(self):
        pipeline_environments_dir = self._find_folder("scripts")
        if pipeline_environments_dir:
            return [s for s in pipeline_environments_dir.iterdir() if s.is_file()]
        return []
