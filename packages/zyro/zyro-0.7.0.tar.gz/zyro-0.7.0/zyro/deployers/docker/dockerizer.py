import os 
import subprocess 
from pathlib import Path
import sys 
import socket
from zyro.core.parser import load_yaml_file

def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0 

def validate_dockerfile(dockerfile_path: Path):
    if not dockerfile_path.exists():
        print(f"Dockerfile not found at {dockerfile_path}")
        sys.exit(1) 

def build_image(dockerfile_path: Path, image_tag: str):
    try:
        subprocess.run(
            ["docker", "build", "-t", image_tag, "-f", str(dockerfile_path), "."],
            check=True
        )
        print(f"Image {image_tag} built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image: {e}")
        sys.exit(1)

def run_container(image_tag: str, config_path: str, host_port: int):
    try:
        subprocess.run([
            "docker", "run", "-d",
            "-p", f"{host_port}:8000",  # 8000 is container's FastAPI port (constant)
            image_tag,
            "zyro", "run", f"--config={config_path}"
        ], check=True)
        print(f"Container running at http://localhost:{host_port}")
    except subprocess.CalledProcessError as e:
        print(f"Error running Docker container: {e}")
        sys.exit(1)

def dockerize(config_path: str):
    config = load_yaml_file(config_path)
    docker_config = config.get('docker', {})
    dockerfile_path = Path(docker_config.get('dockerfile', 'Dockerfile'))
    
    ports = docker_config.get('ports', {})
    host_port = ports.get('host', 8001)
    container_port = ports.get('container', 8000)

    # === Port Rules ===
    if container_port != 8000:
        print("You cannot override the container port. FastAPI runs on port 8000 inside the container.")
        sys.exit(1)

    if host_port == 8000:
        print("Host port 8000 is not allowed. Please choose a different port to avoid conflicts.")
        sys.exit(1)

    if not is_port_available(host_port):
        print(f"Host port {host_port} is already in use. Please use a free port.")
        sys.exit(1)

    validate_dockerfile(dockerfile_path)

    image_tag = f"zyro_app:{os.path.basename(config_path).replace('.yaml', '')}"
    build_image(dockerfile_path, image_tag) 
    run_container(image_tag, config_path, host_port)