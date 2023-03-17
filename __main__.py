# Create arguments
import argparse
import os
from pathlib import Path
import subprocess
import time

from utils.info import PATH, SETTINGS, vs
from pkgs.hugging import load
from pkgs.exceptions import InvalidPath

# python .\aniGen\ run -p "Remilia Scarlet, blue hair, masterpiece, best quality, blue hair, looking at viewer" -cfg -1

class funcs:
    def run(args: argparse.Namespace):
        # Set median range of 15 if user chooses guidance scale value thats >= 30 and <= 0
        if args.guidanceScale <= 0 and args.guidanceScale >= 30:
            args.guidanceScale = 15.0
        if not os.path.exists(args.outdir):
            InvalidPath(f"Download path of {args.oudir} doesn't exist!")
        if args.quantity <= 0:
            args.quantity = 1
        
        print("Starting program...")
        
        print("Parsing prompt...")
        prompt = load.promptParse(args.prompt)
        print("Prompt parsed...")
        
        print(f"Generating image...")
        
        imgPaths = load.generate(args.model, prompt, args.outdir, args.quantity, guidance_scale=args.guidanceScale, revision=(SETTINGS["repos"][args.model]["revision"] if "revision" in SETTINGS["repos"][args.model].keys() else None))
        print(f"Images generated @ paths:\n{ '||__NEW__LINE__||'.join([f'{i+1}) {imgPaths[i]}' for i in range(len(imgPaths))])}".replace("||__NEW__LINE__||", "\n"))

    def build(args: argparse.Namespace):
        print("Starting build process...")
        # Check of hugEnv directory exists
        if not os.path.exists(os.path.join(PATH.root, "hugEnv")):
            print("Creating hugEnv virtual environment...")
            os.system(f"python -m venv {os.path.join(PATH.root, 'hugEnv')}")
            print("hugEnv virtual environment created!")
        # Activate virtual environment
        subprocess.run(
            [
                f"{os.path.join(PATH.root, 'hugEnv', 'Scripts', 'python.exe')}",
                f"{os.path.join(PATH.root, 'src', 'build.py')}",
            ],
            shell=True,
        )


def main():
    defaultModel = [repoId
            for repoId in SETTINGS["repos"].keys()
            if SETTINGS["repos"][repoId]["installed"] == True]
    if len(defaultModel) == 0:
        defaultModel = "None"
    else:
        defaultModel = defaultModel[0]
    
    parser = argparse.ArgumentParser(
        prog=f"python .{os.sep}{Path(__file__).resolve().parent.name}",
        usage="%(prog)s [options]",
        description=f"AniArt Generator v{vs} | An AI-powered image generator.",
        # add_help=True,
    )

    subparsers = parser.add_subparsers(
        help="Valid Subcommands", description="List of subcommands", required=True
    )

    # Create the parser for the "run" command
    runParser = subparsers.add_parser(
        "run",
        help="Runs the program.",
        description="Starts the AniArt Generator",
        usage="%(prog)s [options]",
    )
    runParser.add_argument(
        "-m",
        "--model",
        help="""
        Selects a model to use.
        (default: %(default)s)
        """,
        required=False,
        default=defaultModel,
        action="store",
        type=str,
        choices=[
            repoId
            for repoId in SETTINGS["repos"].keys()
            if SETTINGS["repos"][repoId]["installed"] == True
        ],
    )
    runParser.add_argument(
        "-o",
        "--outdir",
        help="""
        Output directory for the generated image.
        (default: %(default)s)
        """,
        required=False,
        default=PATH.download,
        action="store",
        nargs="?",
        type=str,
    )
    runParser.add_argument(
        "-p",
        "--prompt",
        help="""
        Prompt for the AI
        (Optional) [Can be a path to a .txt file or inputted as "PROMPT_HERE"]
        """,
        required=False,
        default="",
        action="store",
        nargs="?",
        type=str,
    )
    runParser.add_argument(
        "-q",
        "--quantity",
        help="""
        Quantity of imgs to generate.
        (default: %(default)s)
        """,
        required=False,
        default=1,
        action="store",
        nargs="?",
        type=int,
    )
    runParser.add_argument(
        "-cfg",
        "--guidanceScale",
        help="""
        Temperature of how closely generation follows prompt.
        Has to be a float in the range of 0 <= cfg <= 30
        (default: %(default)s)
        """,
        required=False,
        default=7.5,
        action="store",
        nargs="?",
        type=float,
    )
    runParser.set_defaults(func=funcs.run)

    # Create the parser for the "build" command
    buildParser = subparsers.add_parser(
        "build",
        help="Fetches and builds necessary files for the program to run.",
        description="Builds necessary files & models from huggingface",
        usage="%(prog)s [options]",
    )
    buildParser.set_defaults(func=funcs.build)

    args = parser.parse_args()
    if args.func.__name__ == "build":
        funcs.build(args)
    elif args.func.__name__ == "run":
        funcs.run(args)


if __name__ == "__main__":
    main()
