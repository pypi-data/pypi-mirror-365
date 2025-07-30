from collections.abc import Iterable, Sequence
from typing import Annotated, Optional, TypedDict

from fastapi import Depends, Header, Query, Request
from logiclayer import AuthToken, AuthTokenType
from pydantic import with_config

from tesseract_olap.query import (
    DataRequest,
    DataRequestParams,
    MembersRequest,
    MembersRequestParams,
)

DESCRIPTION_PAGINATION = """\
Specifies pagination on the results, so the query can be separated in multiple requests.

The shape of the parameter is composed by one integer, or two integers separated by a comma:
    `{value}` := `{limit}` | `{limit},{offset}`
Where:
    `{limit}` : `int`, defines the max amount of items in the response data
    `{offset}` : `int`, defines the index of the first item in the full list where the list in the response data will start.
"""

DESCRIPTION_SORTING = """\
Specifies the order of the results; available for properties and measures included in the request.

The shape for the value is:
    `{value}` := `{field}` | `{field}.{order}`
Where:
    `{field}` : `str`, defines the field to use: Measure or Property
    `{order}` : `Literal["asc", "desc"]`, defines the direction to sort the dataset

The field will be resolved to a Measure first, if not found then to a Property.
When `{order}` is not set, `"asc"` will be used by default.
"""


class DataSearchParamsRequired(TypedDict, total=True):
    cube: Annotated[str, Query(description="The name of the cube to work with.")]
    drilldowns: Annotated[
        Sequence[str],
        Query(description="A list of the level names to slice the bulk of the aggregated data."),
    ]
    measures: Annotated[
        Sequence[str],
        Query(description="A list of the measure names to retrieve from the aggregated data."),
    ]


@with_config(str_strip_whitespace=True)
class DataSearchParams(DataSearchParamsRequired, total=False):
    locale: Annotated[
        Optional[str],
        Query(description="The code of the language for the content in the response."),
    ]
    limit: Annotated[str, Query(description=DESCRIPTION_PAGINATION)]
    sort: Annotated[str, Query(description=DESCRIPTION_SORTING)]
    time: Annotated[str, Query(description="")]
    top: Annotated[str, Query(description="")]
    growth: Annotated[str, Query(description="")]
    aliases: Annotated[Sequence[str], Query(description="")]
    parents: Annotated[Sequence[str], Query(description="")]
    properties: Annotated[Sequence[str], Query(description="")]
    ranking: Annotated[Sequence[str], Query(description="")]
    exclude: Annotated[Sequence[str], Query(description="")]
    include: Annotated[Sequence[str], Query(description="")]
    filters: Annotated[Sequence[str], Query(description="")]


def auth_token(
    header_auth: Annotated[Optional[str], Header(alias="authorization")] = None,
    header_jwt: Annotated[Optional[str], Header(alias="x-tesseract-jwt")] = None,
    query_token: Annotated[Optional[str], Query(alias="token")] = None,
):
    if header_jwt:
        return AuthToken(AuthTokenType.JWTOKEN, header_jwt)
    if query_token:
        return AuthToken(AuthTokenType.SEARCHPARAM, query_token)
    if header_auth:
        if header_auth.startswith("Bearer "):
            return AuthToken(AuthTokenType.JWTOKEN, header_auth[7:])
        if header_auth.startswith("Basic "):
            return AuthToken(AuthTokenType.BASIC, header_auth[6:])
        if header_auth.startswith("Digest "):
            return AuthToken(AuthTokenType.DIGEST, header_auth[7:])

    return None


def query_cuts_include(
    request: Request,
    include: Annotated[
        str,
        Query(
            description="""\
Specifies which values should be considered for the aggregation.

The value is composed by multiple cut definitions separated by semicolons:
    `{value}` := `{cut_def};{cut_def...}`
Where a single cut definition is composed by the Level name, colon, and the list of keys separated by commas:
    `{cut_def}` := `{name}:{key},{key...}`
    `{name}` : `str`, the name of the Level to apply the cut
    `{key}` : `str | int`, the members' ID values

For compatibility, this parameter also accepts the definition of the {name} parameter directly in the URL search params; note the level name must start in caps for this to work. This means both `&include=Year:2009,2010` and `&Year=2009,2010` are equivalent.
""",
        ),
    ] = "",
):
    """FastAPI Dependency to parse including cut parameters.

    Parses all URL Search Params whose key is capitalized, as cut definitions.
    Values are members' IDs, separated by commas.
    """
    result = {
        key: value.split(",") for key, value in request.query_params.items() if key[0].isupper()
    }
    return {**result, **query_cuts_exclude(include)}


def query_cuts_exclude(
    exclude: Annotated[
        str,
        Query(
            description="""\
Specifies which values should be omitted from the aggregation.

The value is composed by multiple cut definitions separated by semicolons:
    `{value}` := `{cut_def};{cut_def...}`
Where a single cut definition is composed by the Level name, colon, and the list of keys separated by commas:
    `{cut_def}` := `{name}:{key},{key...}`
    `{name}` : `str`, the name of the Level to apply the cut
    `{key}` : `str | int`, the members' ID values
""",
        ),
    ] = "",
):
    """FastAPI Dependency to parse excluding cut parameters."""
    return {
        key: value.split(",")
        for key, value in (item.split(":")[:2] for item in exclude.split(";") if item != "")
    }


def query_filters(
    filters: Annotated[
        list[str],
        Query(
            description="""\
Specifies filters over the values of the calculated aggregations.

The value is a list of filter parameters, where each is composed by a measure name, and one or two conditions:
    `{value}` := `{filter},{filter...}`
    `{filter}` := `{name}.{condition}` | `{name}.{condition}.{joint}.{condition}`
    `{condition}` := `{comparison}.{number}`
Where
    `{name}` : `str`, the name of the Measure to apply the filter on;
    `{comparison}`: `Literal["gt", "gte", "eq", "neq", "lt", "lte"]`, the comparison operation to evaluate ('g' is 'greater', 'l' is 'lower', 'eq' is 'equal', 'neq' is 'not equal');
    `{number}` : `float`, the value to apply the comparison against the Measure (using decimal dot);
    `{joint}` : `Literal["and", "or"]`, the logic operation to apply between two conditions;
""",
        ),
    ] = [],
) -> list[str]:
    """FastAPI Dependency to parse filter parameters."""
    return [item for token in filters for item in token.split(",") if item != ""]


def dataquery_params(
    cube_name: Annotated[
        str,
        Query(alias="cube", description="The name of the cube to work with."),
    ],
    drilldowns: Annotated[
        str,
        Query(
            description="A list of the level names to slice the bulk of the aggregated data.",
        ),
    ],
    measures: Annotated[
        str,
        Query(
            description="A list of the measure names to retrieve from the aggregated data.",
        ),
    ],
    aliases: Optional[str] = None,
    cuts_exclude: dict[str, list[str]] = Depends(query_cuts_exclude),
    cuts_include: dict[str, list[str]] = Depends(query_cuts_include),
    filters: list[str] = Depends(query_filters),
    locale: Optional[str] = None,
    pagination: Annotated[
        str,
        Query(alias="limit", description=DESCRIPTION_PAGINATION),
    ] = "0",
    parents: Annotated[
        str,
        Query(
            description="""\
Specifies if the request should include the labels for the parent levels of the selected drilldowns.

The shape for the value is:
    `{value}` := `{truthy}` | `{falsey}` | `{name},{name...}`
Where:
    `{truthy}` : A string that can be interpreted as a truthy value; retrieves parents for all drilldowns in the request;
    `{falsey}` : A string that can be interpreted as a falsey value; deactivates parents for all drilldowns in the request (default);
    `{name}` : `str`, the name of the specific drilldown(s) to get parents for.
""",
        ),
    ] = "",
    properties: Optional[str] = None,
    ranking: Annotated[
        str,
        Query(
            description="""\
Adds a Ranking column to the specified measures.

If unset, or set to a value that can be interpreted as falsey, no rankings are added.
If set to a value that can be interpreted as truthy, a ranking for every measure is added.
Any other string is interpreted as a comma-separated list of the measure names that are expected to be added a ranking.

The value is always an unsigned integer. If many rows have an equal value, all are assigned the same ranking value, and the next value skips the places for the repeated rows.
The direction of the ranking can be specified by (not) prefixing the measure name with a minus character (`-`): the ranking will be calculated in descending order if the minus is present, ascending otherwise.
""",
        ),
    ] = "",
    sorting: Annotated[str, Query(alias="sort", description=DESCRIPTION_SORTING)] = "",
    time: Optional[str] = None,
    top: Optional[str] = None,
    growth: Optional[str] = None,
):
    """FastAPI Dependency to parse parameters into a DataRequest object."""
    params: DataRequestParams = {
        "drilldowns": [item.strip() for item in drilldowns.split(",")],
        "measures": [item.strip() for item in measures.split(",")],
        "cuts_exclude": cuts_exclude,
        "cuts_include": cuts_include,
        "filters": filters,
        "pagination": pagination,
        "parents": parents,
        "ranking": ranking,
        "sorting": sorting,
    }

    if locale is not None:
        params["locale"] = locale

    if properties is not None:
        params["properties"] = properties.split(",")

    if time is not None:
        params["time"] = time

    if top is not None:
        params["top"] = top

    if growth is not None:
        params["growth"] = growth

    if aliases is not None:
        params["aliases"] = aliases

    return DataRequest.new(cube_name, params)


def membersquery_params(
    cube_name: Annotated[
        str,
        Query(alias="cube", description="The name of the cube to work with."),
    ],
    level: Annotated[str, Query(description="The name of the level to get the members from.")],
    locale: Annotated[
        Optional[str],
        Query(description="The locale to get the members labels in."),
    ] = None,
    pagination: Annotated[
        str,
        Query(alias="limit", description=DESCRIPTION_PAGINATION),
    ] = "0",
    parents: bool = False,
    properties: Annotated[
        list[str],
        Query(description="The Properties to get for each of the members in the selected level."),
    ] = [],
    search: str = "",
):
    """FastAPI Dependency to parse parameters into a MembersRequest object."""
    params: MembersRequestParams = {
        "level": level,
        "pagination": pagination,
        "parents": parents,
        "properties": {item for item in split_list(properties) if item},
    }

    if locale is not None:
        params["locale"] = locale

    if search != "":
        params["search"] = search

    return MembersRequest.new(cube_name, params)


def split_list(items: list[str], tokensep: str = ",") -> Iterable[str]:
    """Split the items in a list of strings, and filter empty strings."""
    return (token.strip() for item in items for token in item.split(tokensep))
