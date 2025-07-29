# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import shutil
import sys
from os.path import join, isdir
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from polaris import Polaris
from polaris.demand.checker.demand_checker import DemandChecker
from polaris.network.checker.supply_checker import SupplyChecker
from polaris.project.project_restorer import restore_project_from_csv
from polaris.utils.global_checker import GlobalChecker


def critical_network_tests(city: str, model_text_folder: str, model_dir=None, scenario_name=None):
    model_dir = model_dir or join(gettempdir(), uuid4().hex)

    restore_project_from_csv(model_dir, model_text_folder, city, overwrite=True, scenario_name=scenario_name)
    shutil.copytree(Path(model_text_folder) / "supply", Path(model_dir) / "supply", dirs_exist_ok=True)

    if isdir(Path(model_text_folder) / "demand"):
        shutil.copytree(Path(model_text_folder) / "demand", Path(model_dir) / "demand", dirs_exist_ok=True)

    model_dir = Path(model_dir)
    pol = Polaris.from_dir(model_dir)

    SupplyChecker(pol.supply_file).has_critical_errors(True)
    DemandChecker(pol.demand_file).has_critical_errors(True)
    GlobalChecker(pol).has_critical_errors(True)


def build_and_check_all_scenarios(city: str, model_text_folder: str, model_dir: str):
    out_pth = Path(model_dir)
    out_pth.mkdir(parents=True, exist_ok=True)

    # Build the base model
    critical_network_tests(city, model_text_folder, model_dir=out_pth / "base")

    scenario_file = Path(model_text_folder) / "scenario_files" / "model_scenarios.json"
    if not scenario_file.exists():
        print(f"NO MULTIPLE scenarios for {city}. Built base only")
        return

    with scenario_file.open() as file_:
        configs = json.load(file_)
    for scenario_name in configs.keys():
        critical_network_tests(city, model_text_folder, model_dir=out_pth / scenario_name, scenario_name=scenario_name)


if __name__ == "__main__":
    critical_network_tests(sys.argv[1], sys.argv[2])
