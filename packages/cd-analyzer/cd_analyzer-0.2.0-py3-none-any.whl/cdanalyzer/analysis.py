import pandas as pd
import numpy as np
import re
from pathlib import Path
import struct
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.optimize import curve_fit
from scipy.constants import R
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter
from typing import List, Tuple, Dict, Any, Optional

def parse_dsx(filepath, debug=False):

    with open(filepath, 'rb') as f:
        content = f.read()

    # --- 1. & 2. 解析元数据和列名 (此逻辑对所有文件通用) ---
    metadata = {}
    metadata_matches = re.findall(b'#([^:]+):\s*([^\x00]+)', content)
    for key_bytes, value_bytes in metadata_matches:
        try:
            metadata[key_bytes.decode('ascii').strip()] = value_bytes.decode('ascii').strip()
        except UnicodeDecodeError:
            continue
    
    start_anchor = b'Misc_AutoShutter:1\x00'
    end_anchor = b'\x00Wavelength -en'
    start_pos = content.find(start_anchor)
    if start_pos == -1: return None
    start_of_cols_pos = start_pos + len(start_anchor)
    end_of_cols_pos = content.find(end_anchor)
    if end_of_cols_pos == -1: return None
    
    column_blob = content[start_of_cols_pos:end_of_cols_pos]
    potential_names = column_blob.split(b'\x00')
    data_column_candidates = []
    for s_bytes in potential_names:
        if not s_bytes: continue
        try:
            s = s_bytes.decode('ascii').strip()
            if s and ':' not in s and s.isprintable() and len(s) > 1 and not s.isdigit():
                data_column_candidates.append(s)
        except (UnicodeDecodeError, TypeError): continue

    column_names = ['Wavelength_nm']
    if data_column_candidates:
        for col in data_column_candidates:
            column_names.append(col.split(' ')[0].strip())
    
    if debug:
        print(f"[DEBUG] 解析出的原始列名顺序: {column_names}")

    if len(column_names) <= 1: return None

    # --- 3. 解析核心参数并根据文件类型动态计算指针 ---
    try:
        range_marker = b'-range\x00'
        range_pos = content.find(range_marker, end_of_cols_pos)
        num_points_pos = range_pos + len(range_marker)
        num_points = struct.unpack('<i', content[num_points_pos : num_points_pos + 4])[0]
        wavelength_data_start_pos = num_points_pos + 4
        
        wavelength_bytes_size = num_points * 4
        wavelength_end_pos = wavelength_data_start_pos + wavelength_bytes_size

        num_repeats = 1
        data_columns_start_pos = 0
        
        repeat_marker = b'Repeat -iter\x00'
        repeat_pos = content.find(repeat_marker)

        if repeat_pos != -1:
            # --- 情况 A: 这是一个多Repeat文件，Padding与N相关 ---
            if debug: print("[DEBUG] 检测到 'Repeat -iter' 标记，按“多Repeat文件”模式解析。")
            
            num_repeats_pos = repeat_pos + len(repeat_marker)
            num_repeats = struct.unpack('<i', content[num_repeats_pos : num_repeats_pos + 4])[0]
            
            # 动态计算Padding: Padding = 4 * N + 4
            dynamic_padding_size = 4 * num_repeats + 4
            
            data_columns_start_pos = repeat_pos + len(repeat_marker) + 4 + dynamic_padding_size

            if debug:
                print(f"[DEBUG] N = {num_repeats}, 动态计算出的Padding为: {dynamic_padding_size} 字节。")
            
        else:
            # --- 情况 B: 这是一个单Repeat文件，Padding固定为4 ---
            if debug: print("[DEBUG] 未检测到 'Repeat -iter' 标记，按“单Repeat文件”模式解析。")
            
            num_repeats = 1
            # 单Repeat文件在Wavelength数据后有一个固定的4字节填充
            SINGLE_REPEAT_PADDING_SIZE = 4
            data_columns_start_pos = wavelength_end_pos + SINGLE_REPEAT_PADDING_SIZE

    except (struct.error, TypeError, IndexError) as e:
        print(f"错误: 解析核心参数失败: {e}")
        return None
    
    if debug:
        print(f"[DEBUG] 数据点数 (num_points): {num_points}")
        print(f"[DEBUG] 重复次数 (num_repeats): {num_repeats}")
        print(f"[DEBUG] 数据列将从 {data_columns_start_pos} 开始读取。")

    # --- 4. & 5. 读取数据 ---
    results_data = [{} for _ in range(num_repeats)]
    
    # 读取Wavelength数据
    try:
        wavelengths = struct.unpack(f'<{num_points}f', content[wavelength_data_start_pos : wavelength_end_pos])
        for i in range(num_repeats):
            results_data[i]['Wavelength_nm'] = wavelengths
    except (struct.error, IndexError): return None
    
    current_pos = data_columns_start_pos
    
    data_columns = column_names[1:]
    for col_name in data_columns:
        if debug: print(f"\n[DEBUG] 正在读取列 '{col_name}' 的所有 repeats...")
        for i in range(num_repeats):
            try:
                col_bytes_size = num_points * 4
                col_data_block = content[current_pos : current_pos + col_bytes_size]
                
                if len(col_data_block) < col_bytes_size:
                     print(f"错误: 文件提前结束。在读取列 '{col_name}' (Repeat #{i+1}) 时数据不足。")
                     return None

                col_data = struct.unpack(f'<{num_points}f', col_data_block)
                results_data[i][col_name] = col_data
                current_pos += col_bytes_size

            except (struct.error, ValueError, IndexError) as e:
                print(f"错误: 读取列 '{col_name}' (Repeat #{i+1}) 数据时失败: {e}")
                return None
    
    # --- 6. 整理并返回结果 ---
    final_results = []
    final_column_order = column_names 

    for i in range(num_repeats):
        df = pd.DataFrame(results_data[i])
        final_results.append((df[final_column_order], metadata))

    return final_results



# --- 1. Sigmoid 函数 ---
# 保持不变，但添加了详细的文档字符串和类型提示
def sigmoid(x: np.ndarray, a: float, Tm: float, b: float, c: float) -> np.ndarray:
    """
    Sigmoid函数（玻尔兹曼函数），用于拟合蛋白解链曲线。

    公式: f(x) = a / (1 + exp((x - Tm) / b)) + c

    Parameters
    ----------
    x : np.ndarray
        自变量，通常是温度 (°C)。
    a : float
        曲线的总振幅（y轴变化范围）。
    Tm : float
        熔解温度（中点），即曲线拐点处的x值。
    b : float
        斜率因子，描述了过渡的陡峭程度。
    c : float
        曲线的垂直偏移量（y轴基线）。

    Returns
    -------
    np.ndarray
        计算出的y值。
    """
    return a / (1 + np.exp((x - Tm) / b)) + c

# --- 2. 绘制变温CD光谱图 ---
def plot_dtemp_cd(ax: plt.Axes, 
                  data_arr: np.ndarray, 
                  factor: float = 1.0, 
                  add_colorbar: bool = True,
                  smooth: None | int = None) -> Tuple[plt.Axes, cm.ScalarMappable]:
    """
    在指定的坐标轴上绘制一系列变温CD光谱。

    Parameters
    ----------
    ax : plt.Axes
        用于绘图的matplotlib坐标轴对象。
    data : np.ndarray
        CD数据，第一列是波长，其余列是对应温度的CD信号。
        形状应为 (n_wavelengths, n_temperatures + 1)。
    temp_lst : List[float]
        与数据列对应的温度列表。
    factor : float, optional
        CD信号的缩放因子，默认为 1.0。
    add_colorbar : bool, optional
        是否在图旁添加表示温度的颜色条，默认为 True。

    Returns
    -------
    Tuple[plt.Axes, cm.ScalarMappable]
        返回原始的坐标轴对象和一个ScalarMappable对象（用于外部创建颜色条）。
    """
    temperature_arr = data_arr[:,:,2].mean(axis=1)
    min_temp, max_temp = temperature_arr.min(), temperature_arr.max()
    norm = plt.Normalize(vmin=min_temp, vmax=max_temp)
    # 使用 'coolwarm' 或 'viridis' 等色谱图
    scalar_mappable = cm.ScalarMappable(norm=norm, cmap=cm.coolwarm)

    for i, temp in enumerate(temperature_arr):
        x,y = data_arr[i][:,0], data_arr[i][:,1] * factor
        if smooth:
            y = gaussian_filter(y,smooth)
        ax.plot(x,y, 
                color=scalar_mappable.to_rgba(temp), lw=2)

    if add_colorbar:
        cbar = plt.colorbar(scalar_mappable, ax=ax, orientation='vertical')
        cbar.set_label('Temperature (°C)', fontsize=14)
        cbar.ax.tick_params(labelsize=12)

    ax.set_xlabel("Wavelength (nm)", fontsize=16)
    ax.set_ylabel("CD (mdeg)", fontsize=16)
    ax.tick_params(labelsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return ax, scalar_mappable

# --- 3. 绘制单波长解链曲线 ---
# 此函数在 tm_calc_cd 中已有类似功能，但作为一个独立的快速绘图工具也很有用。
def plot_single_wl_dtemp(ax: plt.Axes, 
                         data: np.ndarray, 
                         temp_lst: List[float], 
                         wl: float = 222.0, 
                         factor: float = 1.0, 
                         color: str = '#e57373'):
    """
    绘制指定单个波长的CD信号随温度的变化曲线。

    Parameters
    ----------
    ax : plt.Axes
        用于绘图的matplotlib坐标轴对象。
    data : np.ndarray
        CD数据，格式同 plot_dtemp_cd。
    temp_lst : List[float]
        温度列表。
    wl : float, optional
        要监测的波长，默认为 222.0 nm。
    factor : float, optional
        CD信号的缩放因子，默认为 1.0。
    color : str, optional
        曲线颜色，默认为 '#e57373' (红色系)。
    """
    # 找到最接近指定波长的索引
    index = np.argmin(np.abs(data[:, 0] - wl))
    actual_wl = data[index, 0]
    
    y = data[index, 1:] * factor
    x = np.array(temp_lst)
    
    ax.plot(x, y, color=color, lw=2.5, marker='o', markersize=5, linestyle='-')
    ax.set_title(f'Melting Curve at {actual_wl:.1f} nm', fontsize=16)
    ax.set_xlabel("Temperature (°C)", fontsize=16)
    ax.set_ylabel("CD (mdeg)", fontsize=16)
    ax.tick_params(labelsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)



def help_read_multifile(path):
    path = Path(path)
    f_lst = list(path.rglob("*.dsx"))
    data_dic = {}
    for fname in f_lst:
        data = parse_dsx(fname)[0][0]
        if 'buf' in fname.stem.lower():
            k = 'buffer'
        else:
            k = float(round(data['Temperature'].mean(),1))
        dic = {k:data[k] for k in ['Wavelength_nm','CircularDichroism','Temperature']}
        df_new = pd.DataFrame(dic)
        data_dic[k] = df_new
    new_dic = {}
    if 'buffer' in data_dic.keys():
        for k,v in data_dic.items():
            if k == 'buffer':
                continue
            v['CircularDichroism'] = v['CircularDichroism']-data_dic['buffer']['CircularDichroism']
            new_dic[k] = v
    k_lst = sorted(new_dic.keys())
    data_arr = np.stack([np.array(new_dic[k]) for k in k_lst])
    return data_arr

def vant_hoff_model(temp_c, tm, delta_h, mn, cn, md, cd):
    """
    用于非线性拟合的van't Hoff模型函数（包含线性基线）。
    Parameters:
    -----------
    temp_c : array, 温度(°C)
    tm : float, 熔解温度(°C)
    delta_h : float, 展开焓变(J/mol)
    mn, cn : float, 天然态基线参数 (slope, intercept)
    md, cd : float, 变性态基线参数 (slope, intercept)
    """
    temp_k = temp_c + 273.15
    tm_k = tm + 273.15
    y_native = mn * temp_c + cn
    y_denatured = md * temp_c + cd
    exponent = (delta_h / R) * ((1 / tm_k) - (1 / temp_k))
    exponent = np.clip(exponent, -500, 500)
    f_u = np.exp(exponent) / (1 + np.exp(exponent))
    return y_native * (1 - f_u) + y_denatured * f_u


def analyze_and_fit_curves(data_arr,wavelength='auto'):
    """
    对指定的曲线进行拟合，计算热力学参数。
    
    参数:
    - data_dict (dict): 包含所有数据的字典。
    - concentrations_to_fit (list): 需要进行拟合的浓度列表。
    
    返回:
    - thermo_results (dict): 包含拟合结果的字典。
    """
    if wavelength == 'auto':
        index = np.abs(data_arr[:,:,1]-data_arr[0,:,1]).sum(axis=0).argmax()
    else:
        index = np.abs(data_arr[0,:,0]-wavelength).argmin()
    data = data_arr[:,index,:]


    temps, signals = data[:, 2], data[:, 1]
    fit_wavelength = data[:, 0][0]
    # 智能设置初始猜测值 (p0)，这是拟合成功的关键
    p0 = [
        temps[len(temps)//2],  # Tm: 猜测在温度范围中间
        350e3,               # delta_h (J/mol): 典型值
        (signals[5]-signals[0])/(temps[5]-temps[0]), # mn: 初始段斜率
        signals[0],          # cn: 初始段截距
        (signals[-1]-signals[-5])/(temps[-1]-temps[-5]), # md: 末端斜率
        signals[-1]          # cd: 末端截距
    ]
    

    params, _ = curve_fit(vant_hoff_model, temps, signals, p0=p0, maxfev=10000)
    
    tm_fit, delta_h_fit, _, _, _, _ = params
    
    # 在参考温度 25°C (298.15 K) 下计算 ΔG
    T_ref_k = 25.0 + 273.15
    tm_fit_k = tm_fit + 273.15
    delta_g_ref = delta_h_fit * (1 - T_ref_k / tm_fit_k)
    
    thermo_results = {
        'Tm (°C)': tm_fit,
        'ΔH (kJ/mol)': delta_h_fit / 1000, 
        'ΔG_25C (kJ/mol)': delta_g_ref / 1000,
        'fit_params': params, 
        'fit_wavelength':fit_wavelength,
        'data':data_arr
    }
    
    print(f"拟合成功:")
    print(f"  - 拟合得到的 Tm = {tm_fit:.2f} °C")
    print(f"  - 拟合得到的 ΔH = {delta_h_fit/1000:.2f} kJ/mol")
    print(f"  - 计算得到 ΔG at 25°C = {delta_g_ref/1000:.2f} kJ/mol")

            
    return thermo_results


def plot_fitted_curves(thermo_results,ax=None,pointcolor=None,linecolor=None,showparams=False,plotfitted=True):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 7))
        show_plot = True
    else:
        fig = ax.get_figure()
        show_plot = False
    
    if linecolor == None:
        linecolor = 'k'
    if pointcolor == None:
        pointcolor= 'r'
    
    data_arr = thermo_results['data']
    wavelength = thermo_results['fit_wavelength']
    index = np.abs(data_arr[0,:,0]-wavelength).argmin()
    temperature, cd_signal = data_arr[:, index,2], data_arr[:,index, 1]
    ax.plot(temperature, cd_signal, 'o', markersize=4, color=pointcolor)
    print(temperature, cd_signal)
    if 'fit_params' in thermo_results.keys() and plotfitted:
        params = thermo_results['fit_params']
        temp_smooth = np.linspace(temperature.min(), temperature.max(), 200)
        fit_curve = vant_hoff_model(temp_smooth, *params)
        ax.plot(temp_smooth, fit_curve, '-', color=linecolor, linewidth=2.5, alpha=0.8)
    
    if showparams and 'fit_params' in thermo_results.keys():
        Tm = thermo_results['Tm (°C)']
        Tm = round(Tm,1)
        ax.text(0.95, 0.95, f'Tm={Tm} °C',
                    transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))



    

def extrapolate_and_plot_dg(deltaG_arr, ax=None):
    """
    对ΔG进行线性外推，计算ΔG(H₂O)，并绘制外推图。
    
    参数:
    - thermo_results (dict): analyze_and_fit_curves的输出。
    - ax (matplotlib.axes.Axes, optional): 要在其上绘图的Axes对象。如果为None，则创建新图。
    """
    if len(deltaG_arr) < 2:
        print("错误: 至少需要两个成功的拟合点才能进行线性外推。")
        return None, None

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        show_plot = True
    else:
        show_plot = False

    conc_points = deltaG_arr[:,0]
    delta_g_points = deltaG_arr[:,1]
    
    m_value_fit, delta_g_h2o_fit = np.polyfit(conc_points, delta_g_points, 1)

    print("--- 步骤2: 进行线性外推计算 ΔG(H₂O) ---")
    print(f"  - 外推得到 ΔG(H₂O) @ 25°C = {delta_g_h2o_fit:.2f} kJ/mol")
    print(f"  - 拟合得到 m-value = {abs(m_value_fit):.2f} kJ/(mol·M)")
    
    ax.plot(conc_points, delta_g_points, 'o', markersize=8, color='red', label='ΔG (fitted)')
    
    conc_line = np.linspace(0, max(conc_points) * 1.1, 100)
    delta_g_line = m_value_fit * conc_line + delta_g_h2o_fit
    ax.plot(conc_line, delta_g_line, '--', color='blue', label='extrapolate')
    
    ax.plot([0], [delta_g_h2o_fit], 's', markersize=12, color='green', 
            label=f'ΔG($H_2O$) = {delta_g_h2o_fit:.2f} kJ/mol', zorder=5)

    ax.set_title('ΔG extrapolate vs GuHCl', fontsize=16)
    ax.set_xlabel('GuHCl concentration (M)', fontsize=12)
    ax.set_ylabel('ΔG at 25°C (kJ/mol)', fontsize=12)
    ax.grid(True)
    ax.legend()
    
    if show_plot:
        print("绘图：ΔG线性外推图已生成。")
        plt.show()
    
    return delta_g_h2o_fit, m_value_fit