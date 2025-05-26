# Portfolio Optimization - Usage Examples

## Description
Portfolio optimization helps find the optimal distribution of investments across different assets to achieve the best risk-return ratio.

## Example Prompts for LLM

### Example 1: Basic Portfolio Optimization
```
Help me optimize my investment portfolio using MCP Optimizer.

I have $100,000 to invest in the following assets:

Assets:
- Apple Stock: expected return 12%, risk (standard deviation) 18%
- Government Bonds: expected return 6%, risk 3%
- Tesla Stock: expected return 15%, risk 25%
- Gold: expected return 8%, risk 12%

Requirements:
- Maximum acceptable portfolio risk: 15%
- Minimum expected return: 10%

Find the optimal allocation to minimize risk.
```

### Example 2: Diversified Portfolio
```
Use MCP Optimizer to create a diversified portfolio.

Budget: $50,000

Available assets:
- US Stocks: return 14%, risk 20%
- International Stocks: return 11%, risk 16%
- Corporate Bonds: return 8%, risk 5%
- Government Bonds: return 5%, risk 2%
- Real Estate (REITs): return 9%, risk 10%
- Commodities: return 7%, risk 15%

Constraints:
- No more than 30% in any single asset
- Minimum 10% in government bonds
- Maximum 40% in stocks (US + International)
- Risk tolerance: 12%

Maximize expected return while meeting constraints.
```

### Example 3: Retirement Portfolio
```
Help create a conservative retirement portfolio with MCP Optimizer.

Investment amount: $200,000
Investment horizon: 15 years until retirement

Investment options:
- Large Cap Stocks: return 10%, risk 15%
- Treasury Bonds: return 6%, risk 3%
- Corporate Bonds: return 8%, risk 6%
- Bank CDs: return 4%, risk 1%
- Index Funds: return 9%, risk 12%

Requirements:
- Maximum portfolio risk: 8%
- Minimum 20% in risk-free assets (CDs + Treasury)
- Maximum 40% in stocks
- Target return: at least 7%

Find optimal allocation to meet goals.
```

### Example 4: Aggressive Growth Portfolio
```
Create an aggressive growth portfolio using MCP Optimizer.

Capital: $30,000
Goal: maximum growth over 5 years

Investment opportunities:
- Tech Stocks: return 20%, risk 30%
- Emerging Market Stocks: return 18%, risk 28%
- Cryptocurrency: return 25%, risk 40%
- Venture Capital Funds: return 22%, risk 35%
- High-Yield Bonds: return 12%, risk 15%
- Commodity Futures: return 15%, risk 25%

Constraints:
- Maximum portfolio risk: 25%
- Maximum 20% in cryptocurrency
- Minimum 10% in bonds for stability
- No more than 25% in any single asset

Maximize expected return.
```

## Request Structure for MCP Optimizer

```python
# Example function call
result = optimize_portfolio(
    assets=[
        {"name": "Asset1", "expected_return": 0.12, "risk": 0.18},
        {"name": "Asset2", "expected_return": 0.08, "risk": 0.10},
        {"name": "Asset3", "expected_return": 0.15, "risk": 0.25}
    ],
    objective="minimize_risk",  # or "maximize_return"
    budget=100000,
    risk_tolerance=0.15,
    min_return=0.10,
    constraints={
        "max_weight_per_asset": 0.30,
        "min_bonds": 0.20,
        "max_stocks": 0.60
    }
)
```

## Typical Activation Phrases

- "Optimize my investment portfolio"
- "Find optimal asset allocation"
- "Minimize risk for given return"
- "Maximize return with limited risk"
- "Create a diversified portfolio"
- "Help with investment distribution"

## Optimization Strategies

1. **Risk Minimization** - for a given target return
2. **Return Maximization** - with limited risk level
3. **Sharpe Ratio Maximization** - best risk-return ratio
4. **Balanced Portfolio** - equilibrium across all assets

## Applications

Portfolio optimization is used for:
- Personal investments
- Retirement savings
- Fund asset management
- Corporate investments
- Insurance reserves 