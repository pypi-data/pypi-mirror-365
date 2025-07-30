from __future__ import annotations

import atexit
import os
import subprocess
import sysconfig
import tempfile
from typing import TYPE_CHECKING
from typing import Any

import runtool
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

if TYPE_CHECKING:
    from hatchling.bridge.app import SafeApplication
    from hatchling.builders.config import BuilderConfig
    from hatchling.builders.wheel import WheelBuilderConfig
    from hatchling.metadata.core import ProjectMetadata
    from typing_extensions import NotRequired
    from typing_extensions import TypedDict

    class BuildData(TypedDict):
        """A dictionary containing build data."""

        infer_tag: bool
        pure_python: bool
        dependencies: list[str]
        force_include_editable: dict[str, str]
        extra_metadata: dict[str, str]
        shared_data: dict[str, str]
        shared_scripts: dict[str, str]
        artifacts: list[str]
        force_include: dict[str, str]
        tag: NotRequired[str]


class CustomBuildHook(BuildHookInterface):
    def __init__(  # noqa: PLR0913
        self,
        root: str,
        config: dict[str, Any],
        build_config: WheelBuilderConfig | BuilderConfig,
        metadata: ProjectMetadata,
        directory: str,
        target_name: str,
        app: SafeApplication | None = None,
    ) -> None:
        super().__init__(root, config, build_config, metadata, directory, target_name, app)  # pyright:ignore[reportArgumentType]
        version = self.metadata.core_raw_metadata["version"]
        self.tool = runtool.GithubReleaseLinks(
            url=f"https://github.com/grafana/k6/releases/tag/{version}", binary="k6"
        )
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir.__enter__()
        atexit.register(self.temp_dir.__exit__, None, None, None)
        os.environ["TOOL_INSTALLER_OPT_DIR"] = self.temp_dir.name
        os.environ.pop("TOOL_INSTALLER_BIN_DIR", None)
        os.environ.pop("TOOL_INSTALLER_PACKAGE_DIR", None)
        os.environ.pop("TOOL_INSTALLER_GIT_PROJECT_DIR", None)
        os.environ.pop("TOOL_INSTALLER_PIPX_HOME", None)
        runtool.TOOL_INSTALLER_CONFIG = runtool.ToolInstallerConfig()

    def initialize(self, version: str, build_data: BuildData) -> None:  # pyright: ignore[reportIncompatibleMethodOverride] # noqa: ARG002
        if self.target_name != "wheel":
            return
        executable = self.tool.get_executable()

        # Check that the executable is available
        subprocess.run((executable, "--help"), check=True, capture_output=True)  # noqa: S603

        build_data["shared_scripts"].update(
            {
                executable: "k6",
            }
        )

        build_data["pure_python"] = False
        build_data["infer_tag"] = False
        build_data["tag"] = (
            f"py3-none-{sysconfig.get_platform().replace('-', '_').replace('.', '_')}"
        )


runtool.selection = lambda x: x[0]
