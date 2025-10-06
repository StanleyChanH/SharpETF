# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an enhanced ETF Sharpe ratio optimization system (增强版ETF投资组合优化系统) that provides comprehensive quantitative investment decision support. It uses Tushare API to fetch ETF data and implements multiple optimization strategies including Sharpe ratio maximization, risk parity, and multi-objective optimization. The system features ETF Chinese name support, complex growth prediction, and professional HTML report generation. Written in Python and targets Chinese-speaking quantitative finance community.

## Latest Enhancements (v2.3.0 - Code Refactoring)

### Major Refactoring
- **Unified Optimization Engine**: Merged CVXPY and SciPy portfolio optimizers into a single module with automatic backend selection
- **Unified Quantitative Signals**: Integrated simple and advanced quantitative signal modules with mode switching support
- **Code Optimization**: Reduced from 21 files to 19 files (-9.5%) and 10,047 lines to 9,564 lines (-4.8%)
- **Eliminated Redundancy**: Removed duplicate modules, backup files, and streamlined imports
- **Architecture Enhancement**: Improved error handling, backward compatibility, and maintainability

### Technical Improvements
- **Smart Backend Selection**: Automatic detection and fallback between CVXPY and SciPy optimizers
- **Mode-based Signal Processing**: Support for simple/advanced/auto modes in quantitative signal generation
- **Enhanced Error Handling**: Robust fallback mechanisms and comprehensive exception handling
- **Streamlined Dependencies**: Simplified import structure and reduced module interdependencies
- **Code Quality**: Enhanced readability, maintainability, and architectural consistency

### Verified Functionality
- **Full Testing**: Successfully tested in conda environment with all core features working
- **Backward Compatibility**: All original functionality preserved with consistent APIs
- **Performance**: Intelligent backend selection improves computational efficiency
- **Robustness**: Enhanced error handling ensures system stability

## Previous Enhancements (v2.2.0)

### New Features
- **Quantitative Signal Analysis System**: Multi-dimensional quantitative indicators calculation and composite signal synthesis
- **Enhanced Portfolio Optimization**: Intelligent optimization engine based on quantitative signals
- **Chinese Font Configuration Optimization**: Centralized font management and better Chinese display support
- **Simplified Module Support**: Added simplified versions of quantitative signals and optimizer modules as fallback
- **Professional HTML Reports Enhancement**: New quantitative signal analysis and enhanced optimization comparison modules
- **Methodology Detailed Introduction**: Complete methodology documentation for quantitative investment and enhanced optimization

### Technical Improvements
- **Font Management**: Centralized font configuration module (`font_config.py`) for consistent Chinese character display
- **Signal Processing**: Advanced quantitative indicators including momentum, volatility, trend, and quality signals
- **Enhanced Optimization**: Traditional optimization enhanced with quantitative signal integration
- **Robust Architecture**: Simplified modules as fallback for enhanced functionality
- **Visualization Improvements**: Better Chinese font support in all charts and visualizations

## Previous Enhancements (v2.1.0)

### New Features
- **ETF Chinese Name Support**: Automatically fetches and displays ETF Chinese names in all outputs
- **Complex Growth Prediction**: Monte Carlo-based growth forecasting with probability distributions, scenario analysis, and multi-year projections
- **Professional HTML Reports**: Comprehensive HTML reports with interactive charts and detailed analysis
- **Correlation Analysis**: Portfolio correlation risk assessment and diversification scoring
- **Enhanced Visualization**: All charts and reports support ETF Chinese name display

## Key Architecture

### Main Components

- **main.py**: Entry point containing the `EnhancedETFSharpeOptimizer` class that orchestrates the entire workflow
- **src/**: Modular source code directory with clear separation of concerns:

#### Core Modules
- `config.py`: Configuration management (handles config.json and environment variables)
- `data_fetcher.py`: Tushare API integration for fetching ETF daily price data with Chinese name support
- `data_processor.py`: Data processing and returns calculation
- `portfolio_optimizer.py`: **🔧 Unified portfolio optimization engine** (supports both CVXPY and SciPy with automatic backend selection)
- `evaluator.py`: Portfolio performance evaluation with 8+ key financial metrics
- `visualizer.py`: Chart generation (4+ visualization types) with Chinese name support
- `utils.py`: Utility functions for logging, timing, and result saving

#### Enhanced Modules (v2.0+)
- `multi_objective_optimizer.py`: Multi-objective optimization engine with 4 strategies
- `risk_manager.py`: Advanced risk management (VaR/CVaR, stress testing, concentration analysis)
- `rebalancing_engine.py`: Dynamic rebalancing strategies with transaction cost optimization
- `investment_tools.py`: Practical investment tools (complex growth projection, DCA calculator, attribution)
- `correlation_analyzer.py`: ETF correlation analysis and clustering
- `html_report_generator.py`: Professional HTML report generation with interactive features

#### Refactored Modules (v2.3.0+)
- `font_config.py`: Centralized Chinese font configuration for consistent display
- `quant_signals.py`: **🔧 Unified quantitative signals module** (integrates simple and advanced modes)
- `enhanced_portfolio_optimizer.py`: Enhanced optimization engine with unified signal integration
- `enhanced_visualizer.py`: Enhanced visualization with quantitative signal support
- `simple_enhanced_optimizer.py`: Simplified enhanced optimizer (fallback module)

### Enhanced Optimization Flow (v2.3.0 - Refactored)

1. **Configuration**: Load from `config.json` or environment variables
2. **Font Setup**: Initialize Chinese font configuration for consistent display
3. **Data Fetching**: Use Tushare `fund_daily` API to get ETF price data with Chinese name fetching
4. **Data Processing**: Calculate returns and prepare data for optimization
5. **Multi-Objective Optimization**: Run 4 optimization strategies (Sharpe, Risk Parity, Stability, Hierarchical RP)
6. **Advanced Risk Analysis**: VaR/CVaR calculation, stress testing, concentration metrics
7. **Rebalancing Analysis**: Generate rebalancing recommendations with cost optimization
8. **Quantitative Signal Analysis**: Calculate multi-dimensional quantitative signals using unified module with mode selection
9. **Enhanced Portfolio Optimization**: Run signal-enhanced optimization using unified optimization engine
10. **Correlation Analysis**: Portfolio correlation risk assessment and diversification scoring
11. **Complex Growth Projection**: Monte Carlo simulation with probability distributions, scenario analysis, and multi-year forecasting (for both traditional and enhanced strategies)
12. **Comprehensive Evaluation**: Calculate 15+ performance and risk metrics
13. **Enhanced HTML Report Generation**: Create professional HTML reports with quantitative signal analysis and enhanced optimization comparison
14. **Visualization & Reporting**: Generate charts with Chinese names, save results, and create reports

### 🔧 Unified Optimizer Support (v2.3.0+)

The system uses a unified optimization engine (`portfolio_optimizer.py`) that automatically handles multiple backends:
- **Smart Backend Selection**: Automatically detects available libraries (SciPy/CVXPY)
- **Priority Order**: Prefers SciPy for performance, falls back to CVXPY when needed
- **Graceful Degradation**: Uses alternative methods if both backends fail
- **Backend Logging**: Reports which backend is being used for transparency

**Example Usage**:
```python
# Auto backend selection (recommended)
optimizer = get_portfolio_optimizer()

# Force specific backend
optimizer = get_portfolio_optimizer(backend='scipy')  # or 'cvxpy'
```

## Running the Application

### Basic Execution

```bash
python main.py
```

### Dependencies Installation

```bash
pip install -r requirements.txt
```

### Environment Setup (Recommended)

```bash
# Create conda environment
conda create -n sharpetf python=3.9 -y
conda activate sharpetf

# Install dependencies
pip install -r requirements.txt
```

### Configuration Setup

1. Copy `config.json.example` to `config.json`
2. Set your Tushare token in config or as environment variable:
   ```bash
   export TUSHARE_TOKEN=your_token_here
   ```

**Critical Requirement**: Requires Tushare Pro account with 2000+ points to access `fund_daily` API.

## Key Configuration Parameters

- `etf_codes`: List of ETF symbols in format (e.g., "159632.SZ", "510210.SH")
- `start_date`/`end_date`: Analysis period in YYYYMMDD format
- `risk_free_rate`: Risk-free rate for Sharpe ratio calculation (default 2%)
- `trading_days`: Annual trading days (default 252)
- `output_dir`: Directory for results and visualizations (default "outputs")
- `fields`: Data fields to fetch from Tushare (default "trade_date,close")

## Multi-Objective Optimization Strategies

| Strategy | Objective | Best For | Characteristics |
|----------|-----------|----------|-----------------|
| **Maximum Sharpe Ratio** | Risk-adjusted return maximization | Growth investors | Classic Markowitz optimization |
| **Risk Parity** | Equal risk contribution | Conservative investors | Diversified risk profile |
| **Stability Optimization** | Return stability | Risk-averse investors | 30% stability + 70% Sharpe weight |
| **Hierarchical Risk Parity** | Correlation-based clustering | Complex portfolios | Intelligent asset grouping |

## Output Files

### Visualizations (with Chinese Name Support)
- `outputs/cumulative_returns.png`: Cumulative returns comparison across strategies
- `outputs/efficient_frontier.png`: Efficient frontier with optimal portfolio marked
- `outputs/portfolio_weights.png`: Portfolio allocation pie charts with ETF Chinese names
- `outputs/returns_distribution.png`: Returns distribution histogram with normal fit

### Data & Reports
- `outputs/optimization_results.json`: Comprehensive results with all metrics and analyses
- `outputs/etf_optimization_report.html`: **NEW** Professional HTML report with:
  - Interactive charts and responsive design
  - Complete growth prediction analysis (probability distributions, scenarios, multi-year)
  - Advanced risk assessment and correlation analysis
  - Investment recommendations with ETF Chinese names
- `etf_optimizer.log`: Detailed application log file

### Enhanced Features in Outputs
- **ETF Chinese Names**: All displays show both ETF codes and Chinese names
- **Growth Prediction**: Monte Carlo-based forecasting with detailed probability analysis
- **Scenario Analysis**: Bull market, bear market, high volatility, low volatility scenarios
- **Multi-year Projections**: Year-by-year performance predictions
- **Correlation Analysis**: Risk assessment and diversification scoring

## Development Architecture

### Design Patterns
- **Factory Pattern**: All modules use `get_*()` factory functions for initialization
- **Class-based Architecture**: Main orchestrator `EnhancedETFSharpeOptimizer` in main.py
- **Modular Design**: Clear separation between core and enhanced functionality
- **Functional Utilities**: Helper functions in utils.py for common operations

### Key Classes
- `EnhancedETFSharpeOptimizer`: Main orchestrator class with complete workflow and Chinese name support
- `Config`: Configuration management with validation
- `DataFetcher`: ETF data fetching with Chinese name caching functionality
- `MultiObjectiveOptimizer`: Handles 4 different optimization strategies
- `AdvancedRiskManager`: Comprehensive risk analysis (VaR, CVaR, stress testing)
- `RebalancingEngine`: Smart rebalancing with transaction cost optimization
- `InvestmentCalculator`: Complex growth projection with Monte Carlo simulation and scenario analysis
- `HTMLReportGenerator`: Professional HTML report generation with interactive features
- `CorrelationAnalyzer`: Portfolio correlation analysis and diversification assessment

### Logging & Monitoring
- Centralized logging through `utils.setup_logging()`
- Performance timing with `Timer` context manager
- Comprehensive error handling and fallback mechanisms
- Detailed logging of optimizer type selection and performance metrics

## API Dependencies

### Required
- **Tushare Pro** (>=1.2.89): Primary data source requiring paid account (2000+ points)
- **Pandas** (>=1.5.0): Data processing and analysis
- **NumPy** (>=1.21.0): Numerical computations
- **SciPy** (>=1.7.0): Primary optimization engine
- **Matplotlib** (>=3.5.0): Visualization engine

### Optional
- **CVXPY** (>=1.3.0): Alternative optimization engine (fallback if SciPy unavailable)

## Testing & Development

- **No test framework**: Currently no automated tests implemented
- **Chinese Documentation**: All comments and documentation targeted at Chinese market
- **Error Handling**: Comprehensive try-catch blocks with fallback mechanisms
- **Performance Optimized**: Parallel data fetching and efficient numerical computations

## Common Development Tasks

### Adding New ETF Codes
Edit `config.json`:
```json
{
    "etf_codes": ["159632.SZ", "159670.SZ", "159770.SZ", "159995.SZ", "159871.SZ", "510210.SH"]
}
```
Chinese names will be automatically fetched and displayed.

### Extending Optimization Strategies
1. Add new method to `MultiObjectiveOptimizer` class
2. Update strategy comparison in `main.py`
3. Add visualization support in `visualizer.py` (supports Chinese names)
4. Update HTML report template if needed

### Adding New Risk Metrics
1. Extend `AdvancedRiskManager` class with new calculation methods
2. Update risk report generation in main workflow
3. Add HTML report section in `html_report_generator.py`

### Modifying Growth Prediction
1. Update `project_portfolio_growth()` method in `investment_tools.py`
2. Adjust Monte Carlo simulation parameters for more realistic predictions
3. Update scenario analysis methods for different market conditions
4. Modify HTML report sections for new prediction features

### Enhancing HTML Reports
1. Update templates in `html_report_generator.py`
2. Add new CSS styles for better visualization
3. Extend JavaScript functionality for interactivity
4. Add new sections for enhanced analysis features

### Debugging Common Issues
- **Array Dimension Errors**: Check Monte Carlo simulation in `investment_tools.py`
- **Numerical Overflow**: Adjust volatility parameters and return limits
- **Chinese Name Display**: Verify Tushare API access and ETF code format
- **HTML Report Issues**: Check data formatting and template syntax

## Recent Technical Improvements (v2.1.0)

### Numerical Stability Fixes
- **Monte Carlo Simulation**: Fixed array dimension inconsistencies in growth prediction
- **Probability Distribution**: Corrected percentile data access in HTML reports
- **Scenario Analysis**: Implemented differentiated scenario parameters for realistic results
- **Memory Optimization**: Enhanced array handling for large-scale simulations

### Enhanced Algorithm Features
- **Realistic Growth Modeling**: Added market shocks, stop-loss mechanisms, and volatility adjustments
- **Multi-year Analysis**: Extended projection capabilities with proper data padding
- **Risk-adjusted Predictions**: Implemented dynamic volatility based on return levels
- **Correlation Analysis**: Added portfolio diversification scoring and risk assessment

### User Experience Improvements
- **Chinese Name Integration**: All outputs display ETF Chinese names alongside codes
- **Interactive HTML Reports**: Professional reports with responsive design and detailed analysis
- **Enhanced Error Handling**: Better validation and user-friendly error messages
- **Performance Monitoring**: Detailed timing and logging for optimization steps