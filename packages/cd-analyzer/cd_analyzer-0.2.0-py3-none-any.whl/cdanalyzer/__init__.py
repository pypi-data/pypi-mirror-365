# src/cdanalyzer/__init__.py

# 这样用户就可以通过 from cdanalyzer import tm_calc_cd 来使用
# 而不是 from cdanalyzer.analysis import tm_calc_cd
from .analysis import parse_dsx,help_read_multifile,plot_dtemp_cd,analyze_and_fit_curves,plot_fitted_curves,extrapolate_and_plot_dg

print("CD Analyzer package loaded.") # 可以加一句加载信息，也可以不加