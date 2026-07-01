import warnings

warnings.warn(
    "The 'app.forecasting' module is deprecated and will be removed in M53b. "
    "Please use the canonical 'app.forecast' module instead.",
    DeprecationWarning,
    stacklevel=2,
)
