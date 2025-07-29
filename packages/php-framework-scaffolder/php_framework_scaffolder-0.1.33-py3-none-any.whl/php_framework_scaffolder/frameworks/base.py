import os
import shutil
import string
import json
import uuid
import git
import tempfile
import secrets
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Union, List, Optional, Any
from packaging import version
from php_framework_detector.core.models import FrameworkType
from php_framework_scaffolder.utils.semver import select_php_version
from php_framework_scaffolder.utils.template import copy_and_replace_template
from php_framework_scaffolder.utils.logger import get_logger
from php_framework_scaffolder.utils.docker import run_docker_compose_command, run_docker_compose_command_realtime
from php_framework_scaffolder.utils.composer import read_composer_json

logger = get_logger(__name__)


class BaseFrameworkSetup(ABC):
    def __init__(self, framework_type: FrameworkType):
        self.framework_type = framework_type
        self.template_dir = Path(f"templates/{framework_type.value}")
        self.target_folder = Path(tempfile.mkdtemp(), "SpecPHP", str(uuid.uuid4()))

    def get_php_version(self, repository_path: Path) -> Optional[str]:
        try:
            composer_data = read_composer_json(os.path.join(repository_path, "composer.json"))
            php_requirement = composer_data.get("require", {}).get("php", "")
            logger.info(f"PHP requirement: {php_requirement}")
            php_version = select_php_version(php_requirement)
            logger.info(f"Selected PHP version: {php_version}")
            return php_version
        except Exception as e:
            logger.error(f"Error getting PHP version: {e}")
            return None

    def setup(self, repository_path: Path, apk_packages: List[str] = [], php_extensions: List[str] = [], pecl_extensions: List[str] = [], php_version: Optional[str] = None) -> None:
        if php_version is None:
            logger.warning("PHP version is not specified")
            php_version = self.get_php_version(repository_path)
        logger.info(f"Using PHP version: {php_version}")

        apk_packages = [
            "git",
            "npm",
            "bash",
            "linux-headers",
            "$PHPIZE_DEPS",
            "gmp-dev",
            "icu-dev",
            "libffi-dev",
            "libpng-dev",
            "librdkafka-dev",
            "libssh2-dev",
            "libssh2",
            "libxml2-dev",
            "libxslt-dev",
            "libzip-dev",
            "mariadb-client",
            "mysql-client",
            "oniguruma-dev",
            "openldap-dev",
            "postgresql-client",
            "postgresql-dev",
            "zlib-dev",
            "imagemagick-dev",
        ] + apk_packages
        logger.info(f"Using APK packages: {apk_packages}")
        
        php_extensions = [
            "bcmath",
            "calendar",
            "exif",
            "ffi",
            "ftp",
            "gd",
            "gmp",
            "intl",
            "ldap",
            "pcntl",
            "pdo_mysql",
            "pdo_pgsql",
            "pgsql",
            "soap",
            "sockets",
            "sodium",
            "xsl",
            "zip",
            "mbstring",
            "bz2",
            "opcache",
        ] + php_extensions
        logger.info(f"Using PHP extensions: {php_extensions}")

        pecl_extensions = [
            "rdkafka",
            "redis",
            "apcu",
            "imagick",
        ] + pecl_extensions
        logger.info(f"Using PECL extensions: {pecl_extensions}")

        context = {
            "php_version": php_version,
            "db_database": "app",
            "db_username": "user",
            "db_password": secrets.token_hex(8),
            "apk_packages": apk_packages,
            "php_extensions": php_extensions,
            "pecl_extensions": pecl_extensions,
        }
        template_path = Path(os.path.dirname(__file__)).parent / Path(f"templates/{self.framework_type.value}")
        logger.info(f"Template path: {template_path}")

        logger.info(f"Created target folder: {self.target_folder}")

        copy_and_replace_template(template_path, self.target_folder, context)
        logger.info(f"Copied template to {self.target_folder}")

        git.Repo.clone_from(repository_path, self.target_folder / "src")
        logger.info(f"Cloned repository to {self.target_folder / 'src'}")

        build_command = self.get_docker_build_command()
        logger.info(f"Executing build command: {build_command}")
        run_docker_compose_command_realtime(build_command, self.target_folder)

        up_command = self.get_docker_up_command()
        logger.info(f"Executing up command: {up_command}")
        run_docker_compose_command_realtime(up_command, self.target_folder)

        setup_commands = self.get_setup_commands()
        logger.info("Starting Docker containers setup", total_commands=len(setup_commands))

        for i, command in enumerate(setup_commands, 1):
            logger.info(f"Executing setup command {i} of {len(setup_commands)}", command=command)
            run_docker_compose_command_realtime(command, self.target_folder)

        
    def extract_openapi(self, openapi_json_path: Path) -> None:
        openapi_command = self.get_openapi_command()
        logger.info(f"Executing swagger command: {openapi_command}")
        run_docker_compose_command_realtime(openapi_command, self.target_folder)
        openapi_command = self.get_cat_openapi_command(openapi_json_path)
        logger.info(f"Executing cat openapi command: {openapi_command}")
        _, openapi_output, _ = run_docker_compose_command(openapi_command, self.target_folder)
        openapi_json = json.loads(openapi_output)
        os.makedirs(openapi_json_path.parent, exist_ok=True)
        with open(openapi_json_path, "w") as f:
            json.dump(openapi_json, f, indent=4, ensure_ascii=False)
        logger.info(f"OpenAPI JSON saved to {openapi_json_path}")
        

    def extract_routes(self, routes_json_path: Path) -> Dict[str, Any]:
        routes_command = self.get_routes_command()
        logger.info(f"Executing routes command: {routes_command}")
        _, routes_output, _ = run_docker_compose_command(routes_command, self.target_folder)
        routes = json.loads(routes_output)
        logger.info(f"{len(routes)} routes extracted")
        os.makedirs(routes_json_path.parent, exist_ok=True)
        with open(routes_json_path, "w") as f:
            json.dump(routes, f, indent=4, ensure_ascii=False)
        logger.info(f"Routes saved to {routes_json_path}")
        return routes


    def shutdown(self) -> None:
        cleanup_command = self.get_docker_down_command()
        logger.info(f"Executing cleanup command: {cleanup_command}")
        run_docker_compose_command_realtime(cleanup_command, self.target_folder)

        shutil.rmtree(self.target_folder)
        logger.info(f"Removed target folder: {self.target_folder}")


    def get_docker_build_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "build",
        ]
    
    def get_docker_up_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "up",
            "--detach"
        ]

    def get_docker_down_command(self) -> List[str]:
        return [
            "docker",
            "compose",
            "down",
            "-v"
        ]

    @abstractmethod
    def get_setup_commands(self) -> List[List[str]]:
        """
        Get the setup commands for this framework.
        
        Returns:
            List[List[str]]: A list of command arrays to execute for framework setup
        """
        pass

    @abstractmethod
    def get_routes_command(self) -> List[str]:
        """
        Get the command to list routes for this framework.
        
        Returns:
            List[str]: The command array to execute for listing routes
        """
        pass

    def get_openapi_command(self) -> List[str]:
        # ./vendor/bin/openapi --output openapi.yaml --version 3.1.0 --exclude vendor --exclude node_modules --exclude storage .
        return [
            "docker",
            "compose",
            "exec",
            "-w",
            "/app",
            "app",
            "php",
            "-d",
            "error_reporting=~E_DEPRECATED",
            "vendor/bin/openapi",
            "--output",
            "openapi.json",
            "--exclude",
            "vendor",
            "--exclude",
            "node_modules",
            "--exclude",
            "storage",
            "--exclude",
            "public",
            "."
        ]

    def get_cat_openapi_command(self, openapi_json_path: Path) -> List[str]:
        return [
            "docker",
            "compose",
            "exec",
            "-w",
            "/app",
            "app",
            "cat",
            str(openapi_json_path)
        ]