# visualizer.py
import os
import warnings
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil
from typing import List, Dict, Optional, Union

class Visualizer:
    """电池数据可视化工具"""
    
    def __init__(self, data_fetcher):
        """初始化可视化器"""
        self.data_fetcher = data_fetcher
    
    def analyze_cell_cp(self, 
                        bad_id: str, 
                        processes: Optional[List[str]] = None, 
                        save: bool = False, 
                        save_path: Optional[str] = None, 
                        raw: bool = False, 
                        show: bool = True) -> Optional[Dict]:
        """
        分析电池特征分布并生成可视化图表
        
        参数:
            bad_id: 标记为异常的电池ID
            processes: 要分析的工艺类型列表，默认为 ['FOR', 'CAP', 'ADS']
            save: 是否保存图表
            save_path: 图表保存路径，默认为当前目录
            raw: 是否返回原始数据
            show: 是否显示图表
        
        返回:
            如果 raw=True，返回包含各工艺数据的字典；否则返回 None
        """
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        processes = processes or ['FOR', 'CAP', 'ADS']
        data_dict = {}
        
        # 数据准备
        for process in processes:
            df = self.data_fetcher.get_container_extend_by_celllist([bad_id], [process])
            if df.empty:
                print(f"未找到工艺 {process} 的数据")
                continue
                
            df['bad'] = df['cell_id'].eq(bad_id).astype(int)
            data_dict[process] = df
        
        # 生成可视化
        for process, df in data_dict.items():
            # 特征筛选
            valid_features = self._get_valid_features(df)
            
            if not valid_features:
                print(f"工艺 {process} 没有有效特征，跳过绘图")
                continue
            
            # 绘制特征分布图
            self._plot_feature_distributions(
                df, valid_features, bad_id, process, save, save_path, show
            )
        
        return data_dict if raw else None
    
    def analyze_cell_ftp(self,bad_id, proc=None):
        def dynamic_x_for(step_no):
            return 'sequence_no' if step_no in [1, 3, 5] else 'capacity'

        def dynamic_x_cap(step_no):
            return 'soc' if step_no in [2, 5, 7, 9] else 'sequence_no'

        def dynamic_x_ads(step_no):
            return 'soc' if step_no in [2, 4, 6] else 'sequence_no'

        def plot_scatter(data, step_nos, dynamic_x_func):
            cols = 3
            rows = (len(step_nos) + cols - 1) // cols
            with plt.style.context('default'):
                fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3))
                axes = axes.flatten()

                for idx, step_no in enumerate(step_nos):
                    ax = axes[idx]
                    xx = dynamic_x_func(step_no)
                    sns.scatterplot(
                        data=data.query('step_no == @step_no and bad == 0'),
                        x=xx, y='voltage', linewidth=0, s=15, ax=ax
                    )
                    sns.scatterplot(
                        data=data.query('step_no == @step_no and bad == 1'),
                        x=xx, y='voltage', linewidth=0, color='orange', s=9, ax=ax
                    )
                    if step_no == 2 and data['voltage'].values[0] < 1000:
                        ax.set_ylim(1100,2500)
                    ax.set_title(f'Step {step_no}')

                for j in range(len(step_nos), len(axes)):
                    axes[j].axis('off')

                plt.tight_layout()
                figures.append(fig)

            processes = proc
            curves = {}
            for proc_key in processes:
                container = get_container_extend_by_cellid(bad_id, [proc_key])
                df = get_ftp_curves_by_celllist(container.cell_id, proc_key)
                df['bad'] = 0
                df.loc[df['cell_id'] == bad_id, 'bad'] = 1
                curves[proc_key] = df

            max_or_min = 'max' if base == 'ordos' else 'min'
            cap_data = curves['CAP']
            maxq = cap_data.query('step_no == 5').groupby('cell_id')['capacity'].agg(max_or_min).reset_index()
            maxq.columns = ['cell_id', 'max_q']
            maxq['max_q'] = maxq['max_q'].abs()

            for key, df in curves.items():
                df = pd.merge(df, maxq, on='cell_id', how='outer')
                df['soc'] = np.where(df['max_q'].isna(), df['sequence_no'], 100 * df.capacity / df.max_q)
                curves[key] = df

            if 'FOR' in proc and not curves['FOR'].empty:
                print('FOR')
                step_nos = [1, 2, 3, 4, 5]
                plot_scatter(curves['FOR'], step_nos, dynamic_x_for)

            if 'CAP' in proc:
                print('CAP')
                cap_curves = curves['CAP']
                cap_curves_removed = remove_rework_curves(cap_curves)
                step_nos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                plot_scatter(cap_curves, step_nos, dynamic_x_cap)

            if 'ADS' in proc:
                print('ADS')
                step_nos = [1, 2, 3, 4, 5, 6, 7]
                plot_scatter(curves['ADS'], step_nos, dynamic_x_ads)
    def _get_valid_features(self, df):
        """提取有效特征列（非空且有足够变化）"""
        # 首先确定可能的特征列（通常在位置11到倒数第5列之间）
        features = df.columns[11:-5]
        
        # 筛选有效特征（非空值占比超过50%且唯一值>1）
        valid_features = []
        for feat in features:
            ser = df[feat]
            if ser.nunique() > 1 and ser.isna().mean() <= 0.5:
                valid_features.append(feat)
                
        return valid_features
    
    def _plot_feature_distributions(self, df, features, cell_id, process, save, save_path, show):
        """绘制特征分布图"""
        # 动态布局计算
        cols = min(len(features), 4)
        rows = ceil(len(features) / cols)
        
        # 创建子图
        fig, axes = plt.subplots(rows, cols, figsize=(cols*5, rows*4))
        axes = np.array(axes).flatten() if isinstance(axes, np.ndarray) else np.array([axes]).flatten()
        
        # 绘制特征分布
        for ax, feat in zip(axes, features):
            sns.histplot(data=df, x=feat, hue='bad', ax=ax)
            ax.set_title(feat)
            ax.grid(alpha=0.3)
        
        # 关闭多余子图
        for ax in axes[len(features):]:
            ax.axis('off')
            
        plt.tight_layout()
        plt.suptitle(f'{cell_id}_{process}_distribution', y=1.02)

        # 保存逻辑
        if save:
            save_path = save_path or os.getcwd()
            folder = os.path.join(save_path, 'ana_cell_cp', cell_id)
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, f'{cell_id}_{process}_features.png')
            plt.savefig(file_path, bbox_inches='tight')
            print(f'Saved to {file_path}')
            
        if show:
            plt.show()
        else:
            plt.close()