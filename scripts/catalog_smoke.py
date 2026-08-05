"""Run a controlled real-network catalog search smoke check."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from anicompass.catalog import (  # noqa: E402
    CatalogProviderError,
    CatalogService,
    CatalogSource,
    JikanCatalogProvider,
)


async def run_smoke(query: str, limit: int) -> int:
    provider = JikanCatalogProvider()
    service = CatalogService({CatalogSource.JIKAN: provider})
    try:
        result = await service.search(query, limit=limit)
    except CatalogProviderError as exc:
        print(
            "catalog_smoke=failed "
            f"code={exc.error.code.value} message={exc.error.message}"
        )
        return 1
    finally:
        await provider.aclose()

    print(
        f"catalog_smoke=passed source={result.source.value} "
        f"count={len(result.items)}"
    )
    if result.items:
        first = result.items[0]
        print(
            "first="
            f"{first.catalog_id.provider_id}|{first.title}|{first.year or ''}|"
            f"{first.attribution}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke-test real Jikan search.")
    parser.add_argument("--query", default="cowboy bebop")
    parser.add_argument("--limit", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return asyncio.run(run_smoke(args.query, args.limit))


if __name__ == "__main__":
    raise SystemExit(main())