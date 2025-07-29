import sys 
import uvicorn
import argparse 
from pathlib import Path
from zyro.engine.fastapi_engine import create_app 
from zyro.core.parser import get_environment_config
from zyro.deployers.docker.dockerizer import dockerize

def main():
    parser = argparse.ArgumentParser(
        prog = "zyro",
        description = "Deploy APIs from YAML configs. Instantly.") 
    
    subparser = parser.add_subparsers(dest = "command", help = "Available commands")

    run_parser = subparser.add_parser("run", help = "Run the zyro server") 
    run_parser.add_argument(
        "--config",
        type = str, 
        default = "config.yaml" ,
        help = "Path to YAML file" 
    )

    docker_parser = subparser.add_parser("dockerize", help = "Dockerize the application")
    docker_parser.add_argument(
        "--config",
        type = str,
        help = "Path to YAML file"
    )

    args = parser.parse_args() 

    if args.command == "run":
        app = create_app(Path(args.config)) 
    elif args.command == "dockerize":
        if not args.config:
            print("Please provide a path to the YAML config file using --config")
            sys.exit(1) 
        dockerize(Path(args.config))  

if __name__ == "__main__":
    main()