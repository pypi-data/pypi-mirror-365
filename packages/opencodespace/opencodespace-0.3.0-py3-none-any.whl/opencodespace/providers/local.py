"""Local Docker provider implementation."""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List
import tempfile
try:
    from importlib.resources import files, as_file
except ImportError:
    # Python 3.8 compatibility
    from importlib_resources import files, as_file

from .base import Provider

# Set up logger for local provider
logger = logging.getLogger('opencodespace')


class LocalProvider(Provider):
    """
    Provider for local Docker deployments.
    
    This provider runs development environments locally using Docker
    containers with code-server for VS Code in the browser.
    """
    
    DEFAULT_PORT = 8080
    
    @property
    def name(self) -> str:
        return "local"
    
    @property
    def description(self) -> str:
        return "Run development environment locally with Docker"
    
    def check_requirements(self) -> None:
        """Check if Docker is installed and running."""
        if subprocess.call(["which", "docker"], stdout=subprocess.DEVNULL) != 0:
            raise RuntimeError("Docker is not installed or not in PATH.")
        
        # Check if Docker daemon is running
        try:
            subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError:
            raise RuntimeError(
                "Docker daemon is not running. Please start Docker Desktop."
            )
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate local provider configuration."""
        # Optional: validate port configuration if provided
        if "port" in config:
            port = config["port"]
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise ValueError("Port must be a valid number between 1 and 65535")
    
    def _get_container_name(self, config: Dict[str, Any]) -> str:
        """Get the Docker container name."""
        name = config.get('name') or 'local'
        return f"opencodespace-{name}"
    
    def _build_docker_image(self, path: Path) -> str:
        """Build the Docker image from our Dockerfile."""
        # Create .opencodespace directory in project if it doesn't exist
        target_dir = path / ".opencodespace"
        target_dir.mkdir(exist_ok=True)
        
        # Copy required files from package resources
        files_to_copy = ["Dockerfile", "entrypoint.sh"]
        
        logger.info(f"📁 Setting up .opencodespace directory...")
        for filename in files_to_copy:
            try:
                # Load resource data using importlib.resources
                resource_path = files('opencodespace') / '.opencodespace' / filename
                with as_file(resource_path) as resource_file:
                    content = resource_file.read_bytes()
                target_file = target_dir / filename
                
                # Only copy if file doesn't exist or user confirms overwrite
                if target_file.exists():
                    logger.info(f"ℹ️  {filename} already exists in .opencodespace/")
                else:
                    target_file.write_bytes(content)
                    if filename == "entrypoint.sh":
                        target_file.chmod(0o755)
                    logger.info(f"📄 Created .opencodespace/{filename}")
            except Exception as e:
                raise RuntimeError(f"Failed to copy {filename}: {e}")
        
        logger.info(f"🔨 Building Docker image...")
        dockerfile_path = target_dir / "Dockerfile"
        
        try:
            # Build from the project root directory
            subprocess.run(
                ["docker", "build", "-t", "opencodespace:latest", "-f", str(dockerfile_path), str(path)],
                check=True
            )
            return "opencodespace:latest"
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to build Docker image: {e}")
    
    def _build_docker_command(
        self, 
        path: Path, 
        config: Dict[str, Any]
    ) -> List[str]:
        """Build the Docker run command."""
        port = config.get("port", self.DEFAULT_PORT)
        container_name = self._get_container_name(config)
        
        # Build the image
        image = self._build_docker_image(path)
        
        cmd = [
            "docker", "run",
            "--rm",  # Remove container on exit
            "-d",    # Run in background
            "-p", f"{port}:{port}",
            "--name", container_name
        ]
        
        # Get all environment variables using base class method
        env_vars = self.build_environment_vars(config)
        
        # Add environment variables to Docker command
        for key, val in env_vars.items():
            cmd.extend(["-e", f"{key}={val}"])
        
        # Mount the project directory
        if config.get("upload_folder", True):
            cmd.extend(["-v", f"{str(path)}:/home/coder/workspace"])
        
        # Add the image
        cmd.append(image)
        
        return cmd
    
    def deploy(self, path: Path, config: Dict[str, Any]) -> None:
        """Run development environment locally using Docker."""
        self.check_requirements()
        
        # Generate container name if not set
        if not config.get("name"):
            config["name"] = "local"
            
        self.validate_config(config)
        
        port = config.get("port", self.DEFAULT_PORT)
        container_name = self._get_container_name(config)
        
        # Check if container already exists
        existing = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", f"name={container_name}"],
            capture_output=True,
            text=True
        )
        
        if existing.stdout.strip():
            logger.info(f"⚠️  Container '{container_name}' already exists. Removing it...")
            subprocess.run(["docker", "rm", "-f", container_name], check=True)
        
        try:
            logger.info(f"🐳 Starting local development environment...")
            
            # Build and run the Docker command
            cmd = self._build_docker_command(path, config)
            subprocess.run(cmd, check=True)
            
            # Wait a moment for the server to start
            import time
            time.sleep(2)
            
            logger.info(f"✅ Container started successfully!")
            logger.info(f"📡 Server available at: http://localhost:{port}")
            logger.info(f"📦 Container name: {container_name}")
            logger.info(f"\nTo view logs: docker logs -f {container_name}")
            logger.info(f"To stop: opencodespace stop")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker container failed to start: {e}")
    
    def stop(self, config: Dict[str, Any]) -> None:
        """Stop the Docker container."""
        self.check_requirements()
        
        # Ensure we have a container name
        if not config.get("name"):
            config["name"] = "local"
            
        container_name = self._get_container_name(config)
        
        try:
            # Check if container exists
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={container_name}"],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                logger.info(f"ℹ️  Container '{container_name}' is not running")
                return
            
            logger.info(f"🛑 Stopping container: {container_name}")
            subprocess.run(["docker", "stop", container_name], check=True)
            logger.info(f"✅ Container stopped successfully")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to stop container: {e}")
    
    def remove(self, config: Dict[str, Any]) -> None:
        """Remove the Docker container."""
        self.check_requirements()
        
        # Ensure we have a container name
        if not config.get("name"):
            config["name"] = "local"
            
        container_name = self._get_container_name(config)
        
        try:
            # Check if container exists (running or stopped)
            result = subprocess.run(
                ["docker", "ps", "-a", "-q", "-f", f"name={container_name}"],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                logger.info(f"ℹ️  Container '{container_name}' does not exist")
                return
            
            logger.info(f"🗑️  Removing container: {container_name}")
            subprocess.run(["docker", "rm", "-f", container_name], check=True)
            logger.info(f"✅ Container removed successfully")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to remove container: {e}")