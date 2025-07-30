from __future__ import annotations

import logging
import os
import pprint
import tempfile as tmp
from collections.abc import Generator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from datetime import datetime

import orjson
import polars as pl
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response, StreamingResponse
from starlette.background import BackgroundTask
from strenum import StrEnum

from tesseract_olap.backend import Result
from tesseract_olap.common import AnyDict
from tesseract_olap.query import DataQuery, DataRequest, MembersQuery, MembersRequest
from tesseract_olap.schema import Annotations, DataType, TesseractProperty

logger = logging.getLogger(__name__)


class ResponseFormat(StrEnum):
    """Define the extensions available to the user and how to response to them."""

    csv = "csv"
    csvbom = "csvbom"
    excel = "xlsx"
    jsonarrays = "jsonarrays"
    jsonrecords = "jsonrecords"
    parquet = "parquet"
    tsv = "tsv"
    tsvbom = "tsvbom"

    def get_mimetype(self) -> str:
        """Return the matching mimetype for the current enum value."""
        return MIMETYPES[self]


MIMETYPES = {
    ResponseFormat.csv: "text/csv",
    ResponseFormat.csvbom: "text/csv",
    ResponseFormat.excel: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ResponseFormat.jsonarrays: "application/json",
    ResponseFormat.jsonrecords: "application/json",
    ResponseFormat.parquet: "application/vnd.apache.parquet",
    ResponseFormat.tsv: "text/tab-separated-values",
    ResponseFormat.tsvbom: "text/tab-separated-values",
}


@dataclass(eq=False, order=False)
class MembersResModel:
    name: str
    caption: str
    depth: int
    annotations: Annotations
    properties: list[TesseractProperty]
    dtypes: Mapping[str, DataType]
    members: list[AnyDict]


def data_response(
    result: Result[pl.DataFrame],
    extension: ResponseFormat,
    *,
    annotations: Annotations | AnyDict,
    tempdir: str | Path,
    cube=None,
) -> Response:
    df = result.data
    columns = tuple(df.columns)

    headers = {
        "X-Tesseract-Cache": result.cache.get("status", "MISS"),
        "X-Tesseract-Columns": ",".join(columns),
        "X-Tesseract-QueryRows": str(df.height),
        "X-Tesseract-TotalRows": str(result.page["total"]),
    }
    kwargs: AnyDict = {"headers": headers, "media_type": extension.get_mimetype()}

    if extension in (ResponseFormat.csv, ResponseFormat.csvbom):
        with_bom = extension is ResponseFormat.csvbom
        content = df.write_csv(separator=",", include_bom=with_bom, include_header=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["headers"]["Content-Disposition"] = f'attachment; filename="data_{cube} {timestamp}.{extension}"'
        return PlainTextResponse(content, **kwargs)

    if extension in (ResponseFormat.tsv, ResponseFormat.tsvbom):
        with_bom = extension is ResponseFormat.tsvbom
        content = df.write_csv(separator="\t", include_bom=with_bom, include_header=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["headers"]["Content-Disposition"] = f'attachment; filename="data_{cube} {timestamp}.{extension}"'
        return PlainTextResponse(content, **kwargs)

    if extension is ResponseFormat.jsonarrays:
        streamer = _stream_jsonarrays(result, annotations=dict(annotations))
        return StreamingResponse(streamer, **kwargs)

    if extension is ResponseFormat.jsonrecords:
        streamer = _stream_jsonrecords(result, annotations=dict(annotations))
        return StreamingResponse(streamer, **kwargs)

    if extension is ResponseFormat.excel:
        with tmp.NamedTemporaryFile(
            delete=False,
            dir=tempdir,
            suffix=f".{extension}",
        ) as tmp_file:
            df.write_excel(tmp_file.name)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["filename"] = f"data_{cube} {timestamp}.{extension}"
        kwargs["background"] = BackgroundTask(os.unlink, tmp_file.name)
        return FileResponse(tmp_file.name, **kwargs)

    if extension is ResponseFormat.parquet:
        with tmp.NamedTemporaryFile(
            delete=False,
            dir=tempdir,
            suffix=f".{extension}",
        ) as tmp_file:
            df.write_parquet(tmp_file.name)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kwargs["filename"] = f"data_{cube} {timestamp}.{extension}"
        kwargs["background"] = BackgroundTask(os.unlink, tmp_file.name)
        return FileResponse(tmp_file.name, **kwargs)

    raise HTTPException(406, f"Requested format is not supported: {extension}")


def members_response(
    params: MembersRequest,
    query: MembersQuery,
    result: Result[list[AnyDict]],
):
    locale = query.locale
    level = query.hiefield.deepest_level.level

    return MembersResModel(
        name=level.name,
        caption=level.get_caption(locale),
        depth=level.depth,
        annotations=dict(level.annotations),
        properties=[TesseractProperty.from_entity(item, locale) for item in level.properties],
        dtypes=result.columns,
        members=[nest_dict(row) for row in result.data]
        if params.parents or params.properties
        else result.data,
    )


def nest_dict(flat_dict: dict[str, Any]) -> dict[str, Any]:
    """Convert a flat dictionary with dot-notation keys into a nested dictionary or list structure.

    This function transforms keys with dot-separated components into nested objects.
    Numeric indices create lists, while string keys create nested dictionaries.

    Args:
        input_dict (dict): A dictionary with potentially nested keys using dot notation

    Returns:
        dict: A nested dictionary with hierarchical structure based on input keys

    Example:
        >>> flatten_nested_dict({"key": 101, "ancestor.0.key": 1})
        {"key": 101, "ancestor": [{"key": 1}]}

    """
    nested_dict = {}

    for key, value in flat_dict.items():
        key_parts = key.split(".")  # Split the key by periods

        # Traverse or create the nested structure
        current = nested_dict
        for part in key_parts[:-1]:
            # Check if the part is a number (array index)
            if part.isdigit():
                # Ensure the parent is a list
                if not isinstance(current, list):
                    current = nested_dict[key_parts[0]] = []

                index = int(part)
                while len(current) <= index:
                    current.append({})  # Extend list if needed

                # Move to the specific list item
                current = current[index]

            else:
                if part not in current:
                    current[part] = {}  # Create nested dict if not exists
                current = current[part]

        # Set the final value, assuming it never ends with digit
        current[key_parts[-1]] = value

    return nested_dict


def debug_response(
    accept: str,
    *,
    request: DataRequest,
    query: DataQuery,
    sql: AnyDict,
) -> Response:
    priority = [item.split(";")[0] for item in accept.split(",")]
    restype = sorted(
        ["text/plain", "application/json", "text/html"],
        key=lambda x: priority.index(x) if x in priority else 99,
    )

    def _dict_2_str(obj: dict, *, title: str = "{}", content: str = "{}"):
        return "\n".join(
            title.format(name) + "\n" + content.format(value)
            for name, value in obj.items()
            if value
        )

    if restype[0] == "text/plain":
        queries = {
            f"Fetch {name.capitalize()}": _dict_2_str(
                {
                    "SQL": value["query"],
                    "Params": pprint.saferepr(value["params"]) if value["params"] else None,
                    "Tables": _dict_2_str(
                        {
                            f"Table {table_name!r}": "\n".join(
                                "\t".join(str(cell) for cell in row) for row in table_body
                            )
                            for table_name, table_body in value["tables"].items()
                        },
                        title="### {}",
                    ),
                },
                title="## {}",
            )
            for name, value in sql.items()
        }
        sections = {
            "DataRequest": pprint.pformat(request, sort_dicts=True),
            "DataQuery": pprint.saferepr(query),
            **queries,
        }
        content = _dict_2_str(sections, title="\n# {}")
        return PlainTextResponse(content, media_type="text/plain")

    if restype[0] == "text/html":
        queries = {
            f"Fetch {name.capitalize()}": _dict_2_str(
                {
                    "SQL": f"<pre>{value['query']}</pre>",
                    "Params": f"<pre>{pprint.saferepr(value['params'])}</pre>",
                    "Tables": _dict_2_str(
                        {
                            f"Table {table_name!r}": "".join(
                                f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>"
                                for row in table_body
                            )
                            for table_name, table_body in value["tables"].items()
                        },
                        title="<h4>{}</h4>",
                        content="<table><tbody>{}</tbody></table>",
                    ),
                },
                title="<h3>{}</h3>",
            )
            for name, value in sql.items()
        }
        sections = {
            "DataRequest": f"<pre>{pprint.pformat(request, sort_dicts=True)}</pre>",
            "DataQuery": f"<pre>{pprint.saferepr(query)}</pre>",
            **queries,
        }
        content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /><style>pre{{white-space:normal}}</style></head>
<body>{_dict_2_str(sections, title="<h2>{}</h2>")}</body>
</html>
"""
        return PlainTextResponse(content, media_type="text/html")

    content = {
        "request": pprint.pformat(request, sort_dicts=True),
        "query": pprint.saferepr(query),
        **sql,
    }
    return PlainTextResponse(orjson.dumps(content), media_type="application/json")


def _stream_jsonarrays(
    result: Result[pl.DataFrame],
    *,
    annotations: AnyDict,
    chunk_size: int = 100000,
) -> Generator[bytes]:
    """Return a JSON Records representation of the data through a Generator."""
    data = result.data
    yield b'{"annotations":%b,"page":%b,"columns":%b,"data":[' % (
        orjson.dumps(annotations),
        orjson.dumps(result.page),
        orjson.dumps(data.columns),
    )
    for index in range(0, data.height + 1, chunk_size):
        data_chunk = data.slice(index, chunk_size).to_dict(as_series=False)
        # we have the indivitual columns, transform in individual rows
        trasposed = list(zip(*(data_chunk[key] for key in data.columns)))
        comma = b"," if index + chunk_size < data.height else b""
        # remove JSON array brackets and add comma if needed
        yield orjson.dumps(trasposed)[1:-1] + comma
    yield b"]}"


def _stream_jsonrecords(
    result: Result[pl.DataFrame],
    *,
    annotations: dict[str, Any],
    chunk_size: int = 100000,
) -> Generator[bytes]:
    """Return a JSON Records representation of the data through a Generator."""
    data = result.data
    yield b'{"annotations":%b,"page":%b,"columns":%b,"data":[' % (
        orjson.dumps(annotations),
        orjson.dumps(result.page),
        orjson.dumps(data.columns),
    )
    for index in range(0, data.height + 1, chunk_size):
        data_chunk = data.slice(index, chunk_size).to_dicts()
        # JSON is picky with trailing commas, use them only if not finished
        comma = b"," if index + chunk_size < data.height else b""
        # remove JSON array brackets and add comma
        yield orjson.dumps(data_chunk)[1:-1] + comma
    yield b"]}"
