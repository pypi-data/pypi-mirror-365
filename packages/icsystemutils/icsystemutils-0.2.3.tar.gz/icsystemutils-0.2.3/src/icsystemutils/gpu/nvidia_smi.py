"""
This module obtains NVIDIA GPU information

See https://docs.nvidia.com/deploy/nvidia-smi/index.html for nvidia-smi manual
"""

import shutil
import subprocess
import csv

from iccore.system.gpu import GpuProcessor


def has_nvidia_smi() -> bool:
    if shutil.which("nvidia-smi") is None:
        return False
    return True


def _read_nvidia_smi() -> str:
    ret = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=name,serial,pci.bus_id,index,memory.free,memory.total",
            "--format=csv,nounits",
        ]
    )
    return ret.decode("utf-8").strip()


def _from_smi(p: dict) -> GpuProcessor:
    test = GpuProcessor(
        id=int(p["index"]),
        model=str(p["name"]),
        serial=int(p["serial"]),
        bus_id=str(p["pci.bus_id"]),
        max_memory=int(p["memory.total[MiB]"]),
        free_memory=int(p["memory.free[MiB]"]),
    )
    return test


def parse(content: str) -> list[GpuProcessor]:
    formatted_content = content.replace(" ", "").splitlines()
    nvidia_smi_output = csv.DictReader(formatted_content, delimiter=",")

    return [_from_smi(p) for p in list(nvidia_smi_output)]


def read() -> list[GpuProcessor]:
    return parse(_read_nvidia_smi())
