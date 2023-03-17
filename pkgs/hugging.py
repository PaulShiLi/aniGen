import os
import pathlib
from pathlib import Path
import sys

# insert root path
sys.path.insert(1, os.path.join(Path(__file__).resolve().parent.parent))

import asyncio
import aiohttp
from diffusers import StableDiffusionPipeline, StableDiffusionInpaintPipelineLegacy, DiffusionPipeline
import json
import torch
from tensorflow.python.platform import build_info
import textwrap

from utils.info import SETTINGS
from pkgs import display, exceptions

parent_dir = Path(__file__).resolve().parent.parent

def formattedQuery(q): return " ".join([s.strip() for s in q.splitlines()])


class hug:
    async def getRepo(repoId: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://huggingface.co/api/models/{repoId}?blobs=true"
            ) as response:
                return await response.json()

    def getRepoSize(repoId: str) -> int:
        repoInfo = asyncio.run(hug.getRepo(repoId))
        totalBytes = 0
        [totalBytes := totalBytes + file["size"] for file in repoInfo["siblings"]]
        return totalBytes

    def checkModels():
        for repoId in SETTINGS["repos"].keys():
            repo = SETTINGS["repos"][repoId]
            repo["installed"] = os.path.exists(
                os.path.join(
                    parent_dir, "models", f'models--{"--".join(repoId.split("/"))}'
                )
            )
        with open(os.path.join(parent_dir, "res", "settings.json"), "w") as f:
            json.dump(SETTINGS, f, indent=4)

    def dlModels():
        modelIndices = display.get.massSelectionInput(
            "Select model(s) to download",
            [
                {
                    "title": f"{repoId} ~ <= {round(hug.getRepoSize(repoId) / 1000000000, 2)} GB{' | Installed' if SETTINGS['repos'][repoId]['installed'] == True else ''}",
                }
                for repoId in SETTINGS["repos"].keys()
            ],
        )
        # Download model
        keys = [key for key in SETTINGS["repos"].keys()]
        for indice in modelIndices:
            print("Downloading model " + keys[indice] + "...")
            if "revision" in SETTINGS["repos"][keys[indice]].keys():
                revision = SETTINGS["repos"][keys[indice]]["revision"]
            else:
                revision = None
            if revision != None:
                StableDiffusionPipeline.from_pretrained(
                    keys[indice],
                    cache_dir=os.path.join(parent_dir, "models"),
                    torch_dtype=torch.float16,
                    revision=revision
                )
            else:
                StableDiffusionPipeline.from_pretrained(
                    keys[indice],
                    cache_dir=os.path.join(parent_dir, "models"),
                    torch_dtype=torch.float16
                )
            with open(os.path.join(parent_dir, "res", "settings.json"), "w") as f:
                SETTINGS["repos"][keys[indice]]["installed"] = True
                json.dump(SETTINGS, f, indent=4)
            print("Downloaded model " + keys[indice] + "!")

class load:

    def model(modelId: str, revision: str):
        if revision != None:
            return StableDiffusionPipeline.from_pretrained(modelId, torch_dtype=torch.float16, cache_dir=os.path.join(parent_dir, "models"), revision=revision)
        else:
            return StableDiffusionPipeline.from_pretrained(modelId, torch_dtype=torch.float16, cache_dir=os.path.join(parent_dir, "models"))
    
    def promptParse(prompt: str):
        if (os.sep in prompt and prompt != ""):
            splicedPrompt = prompt.split(os.sep)
            if os.path.exists(prompt) and ".txt" in prompt:
                with open(prompt, "r") as f:
                    prompt = "".join(f.readlines()).replace("\n", " ")
            elif os.path.exists(prompt) and ".txt" not in prompt:
                error = textwrap.dedent(f"""
                                        Invalid txt file path given:
                                        {prompt}
                                        """)
                raise exceptions.InvalidPrompt(error)
            else:
                for i in range(len(splicedPrompt)-1, 0, -1):
                    if os.path.exists(os.path.join(*splicedPrompt[:i+1])):
                        error = textwrap.dedent(f"""
                                                Invalid txt file path given:
                                                {prompt}
                                                """)
                        raise exceptions.InvalidPrompt(error)
        elif prompt == "":
            prompt = input("What is your prompt?:\n>> ")
        return prompt
    
    def generate(modelId: str, prompt: str, dlDir: str, size: int = 1, guidance_scale: float = 7.5, revision: str = "fp16") -> list:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        try:
            torch.cuda.empty_cache()
            pipeline = load.model(modelId, revision)
            pipeline = pipeline.to(device)
            with torch.autocast(device):
                images = pipeline([prompt] * size, guidance_scale=guidance_scale)
        except Exception as e:
            print("CUDA out of memory, switching to CPU...")
            torch.cuda.empty_cache()
            device = "cpu"
            pipeline = load.model(modelId)
            pipeline = pipeline.to(device) 
            
            with torch.autocast(device):
                images = pipeline([prompt] * size, guidance_scale=guidance_scale)
        remove_punctuation_map = dict((ord(char), None) for char in '\/*?:"<>|')
        imgPaths = []
        for i in range(len(images)):
            if type(images[i][0]) != bool:
                # Remove forbidden chars
                name = f"{prompt.translate(remove_punctuation_map).replace(' ', '-').replace(',', '_')}{f' - {i}' if i != 0 else ''}.png"
                n = 0
                while (os.path.exists(os.path.join(dlDir, name))):
                    name = f"{prompt.translate(remove_punctuation_map).replace(' ', '-').replace(',', '_')}{f' - {n}' if n != 0 else ''}.png"
                    n += 1
                images[i][0].save(os.path.join(dlDir, name))
                imgPaths.append(os.path.join(dlDir, name))
        return imgPaths



