import numpy as np
import pandas as pd
from typing import Dict, Any

def mock_option_chain(spot: float, base_iv: float) -> pd.DataFrame:
    """Generates a synthetic option chain (implied volatility smile)."""
    strikes = np.linspace(spot * 0.7, spot * 1.3, 31)
    # Simple skew/smile model: IV = base_iv - 0.00005 * (strike - spot) + 0.0000001 * (strike - spot)^2
    ivs = base_iv - 0.00005 * (strikes - spot) + 0.0000001 * (strikes - spot)**2
    
    return pd.DataFrame({
        'strike': strikes,
        'iv': ivs * 100 # convert to percentage
    })

def decompose_vix_change(
    underlying: str, 
    date_from: str, 
    date_to: str, 
    methodology: str = "cboe_like"
) -> Dict[str, Any]:
    """
    Computes VIX decomposition between two dates.
    In a real implementation, this would load historical tick/EOD data.
    Here we simulate market movements deterministically based on dates.
    """
    # Use dates to seed random number generator for stable outputs
    seed = sum(ord(c) for c in date_from + date_to + underlying)
    np.random.seed(seed)
    
    # Simulate market data
    spot_from = 5000 + np.random.normal(0, 100)
    spot_move_pct = np.random.normal(0.001, 0.015) # random daily return
    spot_to = spot_from * (1 + spot_move_pct)
    
    base_iv_from = 0.15 + np.random.normal(0, 0.03)
    iv_move_abs = np.random.normal(0.005, 0.01) # random daily IV shift
    base_iv_to = base_iv_from + iv_move_abs
    
    chain_from = mock_option_chain(spot_from, base_iv_from)
    chain_to = mock_option_chain(spot_to, base_iv_to)
    
    # Simulated VIX calculation
    vix_from = base_iv_from * 100 + 3.0
    vix_to = base_iv_to * 100 + 3.0
    abs_change = vix_to - vix_from
    
    # Factor breakdown
    # 1. Parallel shift: mostly driven by base_iv change
    parallel_shift = iv_move_abs * 100
    
    # 2. Sticky strike (Delta effect): how much VIX moved due to spot moving along the skew
    # If spot drops, IV usually goes up due to negative skew
    sticky_strike = -spot_move_pct * 100 * 0.5 
    
    # 3. Skew & Convexity: the remainder allocated arbitrarily for this simulation
    remainder = abs_change - (parallel_shift + sticky_strike)
    put_skew = remainder * 0.6
    convexity = remainder * 0.4
    
    return {
        "underlying": underlying,
        "from_date": date_from,
        "to_date": date_to,
        "spot": {
            "from": round(spot_from, 2),
            "to": round(spot_to, 2),
            "pct_change": round(spot_move_pct * 100, 2)
        },
        "vix": {
            "from": round(vix_from, 2),
            "to": round(vix_to, 2),
            "abs_change": round(abs_change, 2),
            "pct_change": round((abs_change / vix_from) * 100, 2)
        },
        "factors": {
            "sticky_strike": round(sticky_strike, 2),
            "parallel_shift": round(parallel_shift, 2),
            "put_skew": round(put_skew, 2),
            "call_skew": 0.0, # Simplified
            "downside_convexity": round(convexity, 2),
            "upside_convexity": 0.0
        },
        "curves": {
            "from": chain_from.round(2).to_dict('records')[::3], # sample every 3rd strike
            "to": chain_to.round(2).to_dict('records')[::3]
        },
        "commentary": [
            f"VIX changed by {round(abs_change, 2)} pts ({(spot_move_pct*100):.1f}% spot move).",
            f"Parallel shift accounted for {round(parallel_shift, 2)} pts.",
            f"Sticky strike (spot delta) accounted for {round(sticky_strike, 2)} pts."
        ],
        "metadata": {
            "method_used": methodology,
            "expiries_used": ["30-day constant maturity"],
            "quote_time_from": "16:15:00 ET",
            "quote_time_to": "16:15:00 ET"
        }
    }