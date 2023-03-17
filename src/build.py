import os
from pathlib import Path
import sys
import subprocess

# insert root path
sys.path.insert(1, os.path.join(Path(__file__).resolve().parent.parent))

import textwrap
import requests
from bs4 import BeautifulSoup
import json
import torch

from utils.info import SETTINGS, PATH
from pkgs.hugging import hug

parent_dir = Path(__file__).resolve().parent.parent
 
class start:
    def __init__(self):
        # Install dependencies
        # start.dependencies()

        # Download models
        start.models()
        
        # Check if CUDA is installed
        start.checkCuda()

    def dependencies():
        # Install dependencies
        print(
            f"Installing dependencies from {os.path.join(parent_dir, 'requirements.txt')}..."
        )
        os.system(f"pip install -r {os.path.join(parent_dir, 'requirements.txt')}")
        print("Dependencies installed!")

    def models():
        # Download models
        print("Downloading models...")
        hug.dlModels()
        print("All selected models downloaded!")

    def checkCuda():
        # Scrape NVIDIA's 
        res = requests.get("https://developer.nvidia.com/cuda-gpus")
        supGPU = {}
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for gpu in soup.select("#accordion :is(tbody) > tr :is(a)"):
                if gpu.text != "*":
                    supGPU.update({
                        gpu.text: gpu["href"]
                    })
                # print(f"\n{'-'*30}\n{gpu['href']}\n{gpu.text}")
            with open(os.path.join(PATH.root, "res", "supportedGPUs.json"), "w") as f:
                json.dump(supGPU, f, indent=4)
        else:
            print(f"Failed to fetch CUDA supported GPUs from https://developer.nvidia.com/cuda-gpus returning a status code of {res.status_code}")
            print("Utilizing backup file list of supported GPUs")
            with open(os.path.join(PATH.root, "res", "supportedGPUs.json"), "r") as f:
                supGPU = json.load(f)
            print("Backup file loaded successfully!")
        n = str(subprocess.check_output(["nvidia-smi", "-L"])).count("UUID")
        info = {
            "name": None,
            "link": None,
        }
        if n != 0:
            # Sort gpu list first so TI could be validated first i.e. RTX 3090 Ti > RTX 3090
            for gpu in [key[::-1] for key in sorted([key[::-1] for key in supGPU.keys()])][::-1]:
                if gpu in str(subprocess.check_output("nvidia-smi", shell=True)):
                    info.update({"name": gpu})
                    info.update({"link": supGPU[gpu]})
                    break
            if info["name"] == None:
                print(
                    textwrap.dedent(
                        f"""
                        GPU not a CUDA supported GPU!
                        Switching to CPU for image generation!
                        """
                    )
                )
            else:
                logs = str(subprocess.check_output("nvidia-smi", shell=True)).split(r"\n")
                for log in logs:
                    if "Driver Version" in log:
                        parts = (
                            log.replace("|", "")
                            .replace("\\r", "")
                            .replace("Version: ", "")
                            .split(" ")
                        )
                        for i in range(len(parts)):
                            if (i + 1) != len(parts):
                                if parts[i] != "" and parts[i + 1] != "":
                                    info.update({parts[i]: parts[i + 1]})
        else:
            print(
                textwrap.dedent(
                    """
                    Nvidia GPU not found!
                    Switching to CPU for image generation!
                    """
                )
            )
        if info["name"] != None :
            print(
                textwrap.dedent(
                    f"""
                    Your GPU supports CUDA!
                    
                    GPU: {info['name']}
                    Driver Version: {info['Driver']}
                    {f"CUDA Version: {info['CUDA']}" if 'CUDA' in info.keys() else ""}
                    """
                )
                + (f"\nPlease visit https://developer.nvidia.com/cuda-downloads to download the latest CUDA version for your GPU!\n" if not torch.cuda.is_available() else "")
            )
            if not torch.cuda.is_available():
                print("Uninstalling existing nonCuda torch...")
                os.system("pip uninstall torch torchvision torchaudio -y")
                print("Installing cuda torch...")
                print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return info


if __name__ == "__main__":
    start()
