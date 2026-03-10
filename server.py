import json
from typing import Literal
from mcp.server.fastmcp import FastMCP
from quant import decompose_vix_change

# Initialize FastMCP server
mcp = FastMCP("VixDecompositionServer")

@mcp.tool()
def compute_vix_decomposition(
    from_date: str,
    to_date: str,
    underlying: str = "SPX",
    method: Literal["cboe_like", "house"] = "cboe_like"
) -> str:
    """
    Decomposes the change in VIX or implied volatility between two dates into
    constituent factors (sticky strike, parallel shift, skew, convexity).

    Args:
        from_date: The starting date (YYYY-MM-DD).
        to_date: The ending date (YYYY-MM-DD).
        underlying: The underlying ticker (default: "SPX").
        method: Decomposition methodology to use (default: "cboe_like").
    """
    result = decompose_vix_change(
        underlying=underlying,
        date_from=from_date,
        date_to=to_date,
        methodology=method
    )

    # Returning a JSON string is a safe, clean contract for LLMs.
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()