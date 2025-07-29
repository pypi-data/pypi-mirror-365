# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import shutil
import subprocess
from datetime import datetime, timezone
from os.path import exists
from pathlib import Path

from polaris.network.create.triggers import delete_triggers, create_triggers
from polaris.network.utils.srid import get_srid
from polaris.scenario_management.assemble_model_files import assemble_scenario_files
from polaris.utils.database.database_loader import load_database_from_csvs, GeoInfo
from polaris.utils.database.db_utils import commit_and_close, write_about_model_value
from polaris.utils.database.migration_manager import MigrationManager
from polaris.utils.database.spatialite_utils import get_spatialite_version
from polaris.utils.database.standard_database import StandardDatabase, DatabaseType
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.signals import SIGNAL


def restore_project_from_csv(target_dir, git_dir, project_name, overwrite, scenario_name=None):
    target_dir, git_dir = Path(target_dir), Path(git_dir)
    mkdir_p(target_dir)

    if target_dir != git_dir:
        if overwrite:
            shutil.rmtree(target_dir)
        shutil.copytree(git_dir, target_dir, ignore=_ignore_files, dirs_exist_ok=True)

    if scenario_name:
        assemble_scenario_files(Path(target_dir), scenario_name, full_warnings=True)

    signal = SIGNAL(object)

    network_file_name = target_dir / f"{project_name}-Supply.sqlite"
    demand_file_name = target_dir / f"{project_name}-Demand.sqlite"
    freight_file_name = target_dir / f"{project_name}-Freight.sqlite"

    create_db_from_csv(network_file_name, git_dir / "supply", DatabaseType.Supply, signal, overwrite)
    geo_i = GeoInfo.from_fixed(get_srid(network_file_name))
    create_db_from_csv(demand_file_name, git_dir / "demand", DatabaseType.Demand, signal, overwrite)
    create_db_from_csv(freight_file_name, git_dir / "freight", DatabaseType.Freight, signal, overwrite, geo_info=geo_i)

    if scenario_name:
        from polaris.scenario_management.building_procedures import run_required_rebuilds

        scenario_file = git_dir / "scenario_files" / "model_scenarios.json"
        with scenario_file.open() as file_:
            run_required_rebuilds(target_dir, network_file_name, json.load(file_)[scenario_name], scenario_name)


def _ignore_files(directory, contents):
    return contents if ".git" in directory else []


def create_db_from_csv(db_name, csv_dir, db_type, signal=None, overwrite=False, jumpstart=True, geo_info=None):
    if exists(db_name) and not overwrite:
        raise RuntimeError(f"DB [{db_name}] already exists and overwrite = False")

    geo_info = geo_info or GeoInfo.from_folder(csv_dir)
    db = StandardDatabase.for_type(db_type)
    db.create_db(db_name, geo_info, jumpstart=jumpstart)

    with commit_and_close(db_name, spatial=True) as conn:
        delete_triggers(db, conn)
        load_database_from_csvs(csv_dir, conn, db.default_values_directory, signal)

    MigrationManager.upgrade(db_name, db_type, redo_triggers=False)
    with commit_and_close(db_name, spatial=True) as conn:
        create_triggers(db, conn)

        write_about_model_value(conn, "Build time", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"))
        write_about_model_value(conn, "Files source", str(csv_dir))
        write_about_model_value(conn, "spatialite_version", get_spatialite_version(conn))
        try:
            git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(Path(csv_dir).parent))
        except Exception:
            git_sha = "not found"
        finally:
            write_about_model_value(conn, "Git SHA", git_sha)
