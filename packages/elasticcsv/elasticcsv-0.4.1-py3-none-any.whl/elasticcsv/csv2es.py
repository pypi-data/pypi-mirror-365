import logging
import os
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import typer
import yaml
from box import Box
from typer import Option
from typing_extensions import Annotated

from elasticcsv import elastic_csv
from elasticcsv.elastic_csv import FileMode

logger = logging.getLogger(__name__)
config: Optional[Box] = None

app = typer.Typer(help="Elastic CSV utility")


def _load_config() -> None:
    global config
    logger.info("Loading connection.yaml file")
    if not os.path.exists("./connection.yaml"):
        logger.critical("Can't load csv into elastic without 'connection.yaml' config file")
        logger.critical("See https://gitlab.com/juguerre/elasticcsv")
        exit(1)
    with open("./connection.yaml") as conn_file:
        conn_d = yaml.safe_load(conn_file)
        config = Box(conn_d, box_dots=True)


@app.command()
def load_csv(
    csv: Annotated[Path, Option(exists=True, help="CSV File")],
    index: Annotated[str, Option(help="Elastic Index")],
    logic_date: Annotated[Optional[datetime], Option(help="Date reference for interfaces")] = None,
    csv_date_format: Annotated[
        str, Option(help="date format for *_date columns as for ex: '%Y-%m-%d'")
    ] = "%Y-%m-%d",
    sep: Annotated[str, Option(help="CSV field sepator")] = ";",
    csv_offset: Annotated[int, Option(help="CSV file offset")] = 0,
    delete_if_exists: Annotated[
        bool, Option("--delete-if-exists", "-d", help="Flag for deleting index before running load")
    ] = False,
    dict_columns: Annotated[
        str, Option(help="Comma separated list of colums of type dict to load as dicts")
    ] = None,
) -> None:
    """Loads csv to elastic index"""
    _load_config()
    logger.info(f"Loading file: {csv}")
    logger.info(f"CSV Date Format: {csv_date_format}")

    logic_date = logic_date.date() if logic_date else date.today()
    if delete_if_exists and not elastic_csv.delete_index(config, index=index):
        logger.warning(f"Index {index} not exists and will not be deleted. Continuing anyway")
    dict_columns = dict_columns.strip().split(",") if dict_columns else None
    elastic_csv.load_csv(
        config=config,
        csv_file_name=csv.as_posix(),
        index=index,
        delimiter=sep,
        csv_date_format=csv_date_format,
        logic_date=logic_date,
        csv_offset=csv_offset,
        dict_columns=dict_columns,
    )


@app.command()
def download_index(
    csv: Annotated[Path, Option(exists=False, help="Output CSV File")],
    index: Annotated[str, Option(help="Elastic Index")],
    sep: Annotated[str, Option(help="CSV field sepator")],
    delete_if_exists: Annotated[
        bool, Option("--delete_if_exists", "-d", help="Flag for deleting index before running load")
    ] = False,
) -> None:
    """Download index to csv file"""
    _load_config()
    logger.info(f"Downloading index: {index}")
    file_mode = FileMode.w if delete_if_exists else FileMode.a

    elastic_csv.download_csv(
        config=config, index=index, csv_file_name=csv.as_posix(), delimiter=sep, file_mode=file_mode
    )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s", level="WARNING"
    )
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.getLogger("elasticcsv").setLevel(logging.DEBUG)
    logging.getLogger("elasticsearch").setLevel(logging.INFO)
    app()
