import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Union
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class Tool:
    @staticmethod
    def select_nth_data(df, n=0, gap_threshold_minutes=90):
        """
        根据时间顺序将分容数据分段，再选择第 N 次数据段或者最后一次数据段。
        
        参数:
            df: DataFrame，包含以下列：
                ['cell_id', 'datetime', 'step_no', 'sequence_no', 'voltage',
                'current', 'capacity', 'temperature']
            n: 要保留的测试次序（从1开始计数），或者传入字符串 'last' 表示保留最后一次的分容数据。
            gap_threshold_minutes: 时间间隔阈值（单位为分钟），当两个相邻数据点的时间差大于此值时，
                视作新一段数据的开始。默认90分钟。
        
        返回:
            筛选后的DataFrame，仅保留选择的分容数据段。  
        """
        # 拷贝 DataFrame 并确保 datetime 列为 datetime 类型
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 按时间升序排序
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # 计算相邻行的时间差（以分钟为单位）
        df['time_diff'] = df['datetime'].diff().dt.total_seconds() / 60.0
        
        # 当时间差大于阈值时，认为是新的分段（第一次记录也视作一个分段）
        # 使用 cumsum 生成每个样本所属的段号，每次 gap 大于阈值，段号加1
        df['test_run'] = (df['time_diff'] > gap_threshold_minutes).cumsum()
        
        # 判断选择的分段是第 N 次还是最后一次
        if n == 'last':
            target_run = df['test_run'].max()
        elif isinstance(n, int) and n >= 0:
            target_run = n
        else:
            raise ValueError("参数 n 必须为大于等于1的整数 或 'last'")
        
        # 过滤出属于 target_run 的数据
        selected_df = df[df['test_run'] == target_run].copy()
        
        # 删除辅助的计算列
        selected_df = selected_df.drop(columns=['time_diff', 'test_run'])
        
        return selected_df
    @staticmethod
    def remove_rework_curves(df: pd.DataFrame, threshold_hours: float = 3) -> pd.DataFrame:
        """Remove rework curves based on time difference threshold."""
        df = df.sort_values('datetime')
        df['time_diff'] = df['datetime'].diff().dt.total_seconds() / 3600 
        df['new_period'] = df['time_diff'] > threshold_hours
        df['period_id'] = df['new_period'].cumsum()
        first_period_df = df[df['period_id'] == 0]
        return first_period_df.drop(['new_period', 'period_id', 'time_diff'], axis=1)
    @staticmethod
    def calculate_dqdv(df: pd.DataFrame, 
                      spec: str = 'FOR', 
                      step: Optional[int] = None, 
                      fine_output: bool = False) -> Union[pd.Series, np.ndarray]:
        """Calculate dQ/dV from capacity-voltage data."""
        # Set default step and voltage threshold based on spec
        if spec == 'FOR' and step is None:
            step = 2
            voltage_lower = 2100
        
        # Filter data
        filtered_df = df.query(f'step_no == {step} and voltage > {voltage_lower} and current != 0')
        
        # If not enough data points, return empty result
        if len(filtered_df) < 4:  # Minimum points for cubic spline
            if fine_output:
                return np.array([])
            else:
                return pd.Series([], index=filtered_df.voltage)
        
        # Create spline and calculate derivative
        spline = UnivariateSpline(filtered_df.voltage, filtered_df.capacity, s=45, k=3)
        
        if fine_output:
            # Generate fine grid for smooth curve
            voltage_fine = np.linspace(filtered_df.voltage.min(), filtered_df.voltage.max(), 500)
            return spline.derivative()(voltage_fine)
        else:
            # Calculate at original voltage points
            return spline.derivative()(filtered_df.voltage)
    @staticmethod
    def cal_avg_voltage(df: pd.DataFrame, 
                      spec: str = 'FOR', 
                      step: Optional[int] = None, 
                      fine_output: bool = False) -> Union[pd.Series, np.ndarray]:
        """calculate average charge voltage v(dq)/Q"""
        pass
    @staticmethod
    def remove_outliers(df, columns, k=3):
        """
        移除 DataFrame 中多个指定列的异常值。

        参数:
        - df: pandas DataFrame
        - columns: 需要处理的列名称列表
        - k: 控制异常值范围的倍数（默认3），常用值：1.5 或 3

        返回:
        - 去除异常值后的 DataFrame，仅保留在所有指定列中均落于正常范围内的记录
        """
        # 输入参数类型检查
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df 必须是 pandas DataFrame")
        if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
            raise ValueError("columns 必须是字符串列表")
        
        # 检查 columns 是否存在于 df 中
        missing_columns = set(columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"以下列名不存在于 DataFrame 中: {missing_columns}")
        
        # 处理空 DataFrame 或空 columns 列表
        if df.empty or not columns:
            return df
        
        # 初始化一个全为 True 的掩码
        mask = pd.Series(True, index=df.index)
        
        # 缓存四分位数计算结果
        quantile_cache = {}
        
        for column in columns:
            if column not in df.select_dtypes(include=[float]).columns:
                continue  # 跳过非浮点类型的列
            
            if column not in quantile_cache:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                quantile_cache[column] = (Q1, Q3, IQR)
            else:
                Q1, Q3, IQR = quantile_cache[column]
            
            lower_bound = Q1 - k * IQR
            upper_bound = Q3 + k * IQR
            
            # 仅保留在当前列内位于上下界之间的数据
            mask &= (df[column] >= lower_bound) & (df[column] <= upper_bound)
        
        # 返回只包含满足所有条件的数据
        return df[mask]
    @staticmethod
    def curve_fit(x, y, degree=3, plot=False, func_type='polynomial', custom_func=None, p0=None):
        """
        通用曲线拟合函数
        
        参数:
            x: 自变量数据
            y: 因变量数据
            degree: 多项式拟合的阶数或其他拟合函数的参数个数
            plot: 是否绘制拟合结果图
            func_type: 拟合函数类型，可选 'polynomial'(多项式), 'exponential'(指数), 
                    'logarithmic'(对数), 'power'(幂函数), 'custom'(自定义)
            custom_func: 当func_type='custom'时，用户自定义的拟合函数
            p0: 自定义初始参数，如果为None则使用默认初始值
        
        返回:
            popt: 最优参数值
            pcov: 参数的协方差矩阵
            r_squared: 拟合优度R²
            func: 拟合后的函数
        """
        import numpy as np
        from scipy.optimize import curve_fit
        import matplotlib.pyplot as plt
        
        # 将输入转换为numpy数组
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
        
        # 定义各种拟合函数
        def polynomial_func(x, *params):
            y = np.zeros_like(x)
            for i, param in enumerate(params):
                y += param * x ** i
            return y
        
        def exponential_func(x, a, b, c):
            return a * np.exp(b * x) + c
        
        def logarithmic_func(x, a, b, c):
            return a * np.log(b * x) + c
        
        def power_func(x, a, b, c):
            return a * x ** b + c
        
        # 选择拟合函数
        if func_type == 'polynomial':
            fit_func = polynomial_func
            default_p0 = np.ones(degree + 1)  # 对于多项式，参数个数是阶数+1
        elif func_type == 'exponential':
            fit_func = exponential_func
            default_p0 = [1.0, 0.1, 0.0]
        elif func_type == 'logarithmic':
            fit_func = logarithmic_func
            default_p0 = [1.0, 1.0, 0.0]
        elif func_type == 'power':
            fit_func = power_func
            default_p0 = [1.0, 1.0, 0.0]
        elif func_type == 'custom' and custom_func is not None:
            fit_func = custom_func
            default_p0 = np.ones(degree)
        else:
            raise ValueError("无效的拟合函数类型或缺少自定义函数")
        
        # 使用用户提供的初始参数或默认参数
        actual_p0 = p0 if p0 is not None else default_p0
        
        try:
            # 执行曲线拟合
            popt, pcov = curve_fit(fit_func, x, y, p0=actual_p0, maxfev=10000)
            
            # 计算拟合优度 R²
            y_pred = fit_func(x, *popt)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum((y - y_pred) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # 创建拟合函数
            def fitted_func(x_new):
                return fit_func(x_new, *popt)
            
            # 绘制拟合结果
            if plot:
                plt.figure(figsize=(10, 6))
                plt.scatter(x, y, color='blue', label='原始数据')
                
                # 生成拟合曲线点
                x_fit = np.linspace(min(x), max(x), 1000)
                y_fit = fit_func(x_fit, *popt)
                
                # 添加参数值到图例
                param_str = ', '.join([f'p{i}={val:.4g}' for i, val in enumerate(popt)])
                
                plt.plot(x_fit, y_fit, 'r-', label=f'拟合曲线 (R² = {r_squared:.4f})\n参数: {param_str}')
                plt.xlabel('X')
                plt.ylabel('Y')
                plt.title(f'{func_type.capitalize()} 拟合结果')
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.show()
            
            return popt, pcov, r_squared, fitted_func
        
        except Exception as e:
            print(f"拟合过程中出现错误: {str(e)}")
            return None, None, None, None

    
    @staticmethod
    def gaussian_filter1d(x,y,sigma=30,mode='nearest',plot =False):

        y_filtered = gaussian_filter1d(y, sigma=sigma,mode=mode)

        if plot:
            plt.figure(figsize=(8, 5))
            plt.scatter(x, y, s=5, label="Origin", alpha=0.6)
            plt.plot(x, y_filtered, color='red', linewidth=2, label="Gaussian Filter")
            plt.legend()
            plt.show()
        return y_filtered
    @staticmethod
    def savgol_filter1d(y, window_length=None, polyorder=3,plot =False):
        x= np.arange(len(y))
        if window_length is None:
            window_length = len(y) // 20
        y_smooth = savgol_filter(y, window_length, polyorder)
        print(len(x),len(y_smooth))
        if plot:
            plt.figure(figsize=(8, 5))
            plt.scatter(x, y_smooth, s=5, label="Origin", alpha=0.6)
            plt.plot(x, y_smooth, color='red', linewidth=2, label="savgol")
            plt.legend()
            plt.show()
        return y_smooth
    @staticmethod
    def segment_sequence(seq):
        result = []
        segment_num = 1
        for i, num in enumerate(seq):
            if num == 0:
                if i > 0 and seq[i - 1] != 0:
                    segment_num += 1
                result.append(segment_num)
            else:
                if i > 0 and seq[i - 1] == 0:
                    segment_num += 1
                result.append(segment_num)
        return result



from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.feature_selection import (
    SelectKBest, f_regression, mutual_info_regression,
    RFE, RFECV, SelectFromModel, VarianceThreshold
)
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score



class RegressionFeatureSelector:
    """
    用于回归问题的特征筛选器
    提供多种特征选择方法，并能比较不同方法的效果
    预处理过程不包含数据清洗，请确保数据已经清洗好
    # 使用示例
    
    X = features_df  # tsfresh提取的特征
    y = target_values  # 目标变量(连续值)

    # 初始化特征选择器
    selector = RegressionFeatureSelector(X, y)

    # 比较多种特征选择方法
    comparison = selector.compare_methods(k=15)

    # 使用带交叉验证的RFE选择特征
    selected_features, _ = selector.rfecv_selection(min_features=5)

    # 获取基于多种方法投票的最佳特征
    best_features = selector.get_best_features(n_features=15)

    # 评估不同特征子集
    feature_sets = {
        'Pearson Top 10': selector.correlation_selection(method='pearson', k=10)[0],
        'Random Forest Top 10': selector.rf_selection(k=10)[0],
        'RFECV Selected': selector.rfecv_selection(min_features=5)[0],
        'Voting Best 15': selector.get_best_features(n_features=15)
    }
    evaluation, detailed_results = selector.evaluate_feature_subsets(feature_sets)
    """
    

    
    def __init__(self, X, y, feature_names=None):
        """
        初始化特征筛选器
        
        参数:
            X: 特征矩阵，numpy数组或pandas DataFrame
            y: 目标变量，用于回归的连续值
            feature_names: 特征名称列表，如果X是DataFrame则自动提取
        """
        # 将数据转换为DataFrame以便更好处理
        if isinstance(X, pd.DataFrame):
            self.X = X.copy()
            self.feature_names = X.columns.tolist()
        else:
            self.X = pd.DataFrame(X)
            if feature_names is not None:
                self.X.columns = feature_names
                self.feature_names = feature_names
            else:
                self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
                self.X.columns = self.feature_names
        
        # 处理目标变量
        if isinstance(y, pd.Series):
            self.y = y.values
        else:
            self.y = np.array(y)
            
        # 存储原始数据
        self.X_original = self.X.copy()
        
        # 初始化筛选结果存储
        self.results = {}
        
        # 数据预处理
        self._preprocess_data()
            
    def _preprocess_data(self):
        """数据预处理：处理缺失值和标准化特征"""
        # 处理缺失值
        self.X = self.X.fillna(self.X.mean())
        
        # 检查常数列并移除
        constant_filter = VarianceThreshold(threshold=0)
        constant_filter.fit(self.X)
        constant_cols = [col for i, col in enumerate(self.X.columns) 
                        if not constant_filter.get_support()[i]]
        if constant_cols:
            print(f"移除{len(constant_cols)}个常数列: {constant_cols}")
            self.X = self.X.drop(columns=constant_cols)
            self.feature_names = self.X.columns.tolist()
        
        # 标准化特征
        self.scaler = StandardScaler()
        self.X_scaled = pd.DataFrame(
            self.scaler.fit_transform(self.X),
            columns=self.X.columns
        )
    
    def correlation_selection(self, method='pearson', k=10):
        """基于相关系数的特征选择
        
        参数:
            method: 'pearson'或'spearman'
            k: 选择的特征数量
        """
        # 计算相关系数
        if method == 'pearson':
            corr = np.array([abs(np.corrcoef(self.X[col], self.y)[0, 1]) 
                             for col in self.X.columns])
        elif method == 'spearman':
            corr = np.array([abs(pd.Series(self.X[col]).corr(
                             pd.Series(self.y), method='spearman')) 
                             for col in self.X.columns])
        else:
            raise ValueError("方法必须是'pearson'或'spearman'")
            
        # 获取相关系数最高的特征索引
        top_indices = np.argsort(corr)[-k:][::-1]
        selected_features = self.X.columns[top_indices].tolist()
        
        # 保存结果
        self.results[f'{method}_correlation'] = {
            'scores': corr,
            'selected_features': selected_features,
            'support': np.in1d(self.X.columns, selected_features)
        }
        
        return selected_features, corr
    
    def mutual_info_selection(self, k=10):
        """基于互信息的特征选择
        
        参数:
            k: 选择的特征数量
        """
        # 使用互信息回归
        selector = SelectKBest(mutual_info_regression, k=k)
        selector.fit(self.X, self.y)
        
        # 获取分数和选择的特征
        scores = selector.scores_
        selected_features = self.X.columns[selector.get_support()].tolist()
        
        # 保存结果
        self.results['mutual_info'] = {
            'scores': scores,
            'selected_features': selected_features,
            'support': selector.get_support()
        }
        
        return selected_features, scores
    
    def f_regression_selection(self, k=10):
        """基于F统计量的特征选择
        
        参数:
            k: 选择的特征数量
        """
        # 使用F回归统计量
        selector = SelectKBest(f_regression, k=k)
        selector.fit(self.X, self.y)
        
        # 获取分数和选择的特征
        scores = selector.scores_
        selected_features = self.X.columns[selector.get_support()].tolist()
        
        # 保存结果
        self.results['f_regression'] = {
            'scores': scores,
            'selected_features': selected_features,
            'support': selector.get_support()
        }
        
        return selected_features, scores
    
    def lasso_selection(self, alpha=0.01, k=10):
        """基于Lasso回归的特征选择
        
        参数:
            alpha: Lasso正则化强度
            k: 选择的特征数量
        """
        # 训练Lasso模型
        lasso = Lasso(alpha=alpha, max_iter=10000)
        lasso.fit(self.X_scaled, self.y)
        
        # 获取特征重要性
        importance = np.abs(lasso.coef_)
        
        # 选择最重要的k个特征
        top_indices = np.argsort(importance)[-k:][::-1]
        selected_features = self.X.columns[top_indices].tolist()
        
        # 保存结果
        self.results['lasso'] = {
            'scores': importance,
            'selected_features': selected_features,
            'support': np.in1d(self.X.columns, selected_features),
            'model': lasso
        }
        
        return selected_features, importance
    
    def rf_selection(self, k=10):
        """基于随机森林的特征选择
        
        参数:
            k: 选择的特征数量
        """
        # 训练随机森林模型
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(self.X, self.y)
        
        # 获取特征重要性
        importance = rf.feature_importances_
        
        # 选择最重要的k个特征
        top_indices = np.argsort(importance)[-k:][::-1]
        selected_features = self.X.columns[top_indices].tolist()
        
        # 保存结果
        self.results['random_forest'] = {
            'scores': importance,
            'selected_features': selected_features,
            'support': np.in1d(self.X.columns, selected_features),
            'model': rf
        }
        
        return selected_features, importance
    
    def gbm_selection(self, k=10):
        """基于梯度提升树的特征选择
        
        参数:
            k: 选择的特征数量
        """
        # 训练梯度提升树模型
        gbm = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gbm.fit(self.X, self.y)
        
        # 获取特征重要性
        importance = gbm.feature_importances_
        
        # 选择最重要的k个特征
        top_indices = np.argsort(importance)[-k:][::-1]
        selected_features = self.X.columns[top_indices].tolist()
        
        # 保存结果
        self.results['gradient_boosting'] = {
            'scores': importance,
            'selected_features': selected_features,
            'support': np.in1d(self.X.columns, selected_features),
            'model': gbm
        }
        
        return selected_features, importance
    
    def rfe_selection(self, k=10, estimator=None):
        """递归特征消除
        
        参数:
            k: 选择的特征数量
            estimator: 用于RFE的评估器，默认为线性回归
        """
        # 默认使用线性回归
        if estimator is None:
            estimator = LinearRegression()
            
        # 使用RFE选择特征
        selector = RFE(estimator, n_features_to_select=k, step=1)
        selector.fit(self.X, self.y)
        
        # 获取特征排名和选择的特征
        ranking = selector.ranking_
        selected_features = self.X.columns[selector.support_].tolist()
        
        # 保存结果
        self.results['rfe'] = {
            'scores': -ranking,  # 负排名作为分数，越高越重要
            'selected_features': selected_features,
            'support': selector.support_
        }
        
        return selected_features, -ranking
    
    def rfecv_selection(self, min_features=5, estimator=None, cv=5):
        """带交叉验证的递归特征消除
        
        参数:
            min_features: 最小特征数量
            estimator: 用于RFECV的评估器，默认为线性回归
            cv: 交叉验证折数
        """
        # 默认使用线性回归
        if estimator is None:
            estimator = LinearRegression()
            
        # 使用RFECV选择特征
        selector = RFECV(estimator, min_features_to_select=min_features, 
                        step=1, cv=cv, scoring='neg_mean_squared_error')
        selector.fit(self.X, self.y)
        
        # 获取特征排名和选择的特征
        ranking = selector.ranking_
        selected_features = self.X.columns[selector.support_].tolist()
        
        # 绘制CV分数曲线
        plt.figure(figsize=(10, 6))
        plt.title('RFECV: 不同特征数量的MSE得分')
        plt.xlabel('特征数量')
        plt.ylabel('MSE (负)')
        plt.plot(range(min_features, len(ranking) + 1), selector.grid_scores_)
        plt.axvline(x=len(selected_features), color='r', linestyle='--')
        plt.text(len(selected_features)+0.5, min(selector.grid_scores_), 
                 f'选择了{len(selected_features)}个特征', 
                 verticalalignment='bottom')
        plt.grid(True)
        plt.show()
        
        # 保存结果
        self.results['rfecv'] = {
            'scores': -ranking,  # 负排名作为分数，越高越重要
            'selected_features': selected_features,
            'support': selector.support_,
            'grid_scores': selector.grid_scores_
        }
        
        return selected_features, -ranking
    
    def compare_methods(self, k=10, methods=None):
        """比较不同特征选择方法
        
        参数:
            k: 每种方法选择的特征数量
            methods: 要比较的方法列表，默认为所有方法
        """
        if methods is None:
            methods = ['pearson', 'spearman', 'mutual_info', 'f_regression', 
                      'lasso', 'random_forest', 'gradient_boosting', 'rfe']
            
        # 运行每种方法
        all_results = {}
        for method in methods:
            if method == 'pearson':
                features, scores = self.correlation_selection(method='pearson', k=k)
            elif method == 'spearman':
                features, scores = self.correlation_selection(method='spearman', k=k)
            elif method == 'mutual_info':
                features, scores = self.mutual_info_selection(k=k)
            elif method == 'f_regression':
                features, scores = self.f_regression_selection(k=k)
            elif method == 'lasso':
                features, scores = self.lasso_selection(k=k)
            elif method == 'random_forest':
                features, scores = self.rf_selection(k=k)
            elif method == 'gradient_boosting':
                features, scores = self.gbm_selection(k=k)
            elif method == 'rfe':
                features, scores = self.rfe_selection(k=k)
            else:
                continue
                
            all_results[method] = features
            
        # 计算特征选择的一致性
        all_selected = set()
        for method, features in all_results.items():
            all_selected.update(features)
            
        # 创建特征-方法矩阵
        selection_matrix = pd.DataFrame(0, index=list(all_selected), 
                                        columns=list(all_results.keys()))
        
        for method, features in all_results.items():
            for feature in features:
                selection_matrix.loc[feature, method] = 1
                
        # 计算每个特征被选择的次数
        selection_matrix['total'] = selection_matrix.sum(axis=1)
        selection_matrix = selection_matrix.sort_values('total', ascending=False)
        
        # 绘制热图
        plt.figure(figsize=(12, max(8, len(all_selected) * 0.3)))
        sns.heatmap(selection_matrix.drop('total', axis=1), cmap='viridis', 
                    cbar=False, linewidths=.5)
        plt.title('不同特征选择方法比较')
        plt.ylabel('特征名称')
        plt.xlabel('选择方法')
        plt.tight_layout()
        plt.show()
        
        # 绘制每个特征被选择次数的条形图
        plt.figure(figsize=(12, max(8, len(all_selected) * 0.3)))
        selection_matrix['total'].sort_values().plot(kind='barh')
        plt.title('特征被不同方法选择的次数')
        plt.xlabel('被选择次数')
        plt.ylabel('特征名称')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        return selection_matrix
    
    def get_best_features(self, n_features=10, threshold=0.5, voting='majority'):
        """基于多种方法的投票获取最佳特征
        
        参数:
            n_features: 要返回的特征数量
            threshold: 如果使用阈值投票，特征被选择的最小比例
            voting: 'majority'(多数投票)或'threshold'(阈值投票)
        """
        if not self.results:
            print("请先运行特征选择方法")
            return []
            
        # 获取所有特征
        all_features = self.X.columns.tolist()
        
        # 创建选择矩阵
        support_matrix = np.zeros((len(all_features), len(self.results)))
        
        for i, (method, result) in enumerate(self.results.items()):
            if 'support' in result:
                support = result['support']
                if len(support) == len(all_features):
                    support_matrix[:, i] = support
                    
        # 计算每个特征被选择的次数
        feature_votes = support_matrix.sum(axis=1)
        
        if voting == 'majority':
            # 多数投票：选择得票最多的n_features个特征
            top_indices = np.argsort(feature_votes)[-n_features:][::-1]
            selected_features = [all_features[i] for i in top_indices]
        else:
            # 阈值投票：选择投票比例超过threshold的特征
            min_votes = threshold * len(self.results)
            selected_indices = np.where(feature_votes >= min_votes)[0]
            selected_features = [all_features[i] for i in selected_indices]
            # 如果特征太多，只取前n_features个
            if len(selected_features) > n_features:
                top_votes = feature_votes[selected_indices]
                top_indices = np.argsort(top_votes)[-n_features:][::-1]
                selected_features = [selected_features[i] for i in top_indices]
                
        return selected_features
    
    def evaluate_feature_subsets(self, feature_sets, model=None, cv=5):
        """评估不同特征子集的性能
        
        参数:
            feature_sets: 字典，键为名称，值为特征列表
            model: 评估模型，默认为Ridge回归
            cv: 交叉验证折数
        """
        if model is None:
            model = Ridge(alpha=1.0)
            
        # 创建交叉验证对象
        kf = KFold(n_splits=cv, shuffle=True, random_state=42)
        
        # 存储结果
        results = {}
        
        for name, features in feature_sets.items():
            # 只选择特定特征
            X_subset = self.X[features]
            
            # 进行交叉验证
            mse_scores = -cross_val_score(model, X_subset, self.y, 
                                         scoring='neg_mean_squared_error', 
                                         cv=kf, n_jobs=-1)
            r2_scores = cross_val_score(model, X_subset, self.y, 
                                       scoring='r2', cv=kf, n_jobs=-1)
            
            # 存储结果
            results[name] = {
                'mse_mean': mse_scores.mean(),
                'mse_std': mse_scores.std(),
                'r2_mean': r2_scores.mean(),
                'r2_std': r2_scores.std(),
                'features': features
            }
            
        # 创建结果数据框
        result_df = pd.DataFrame({
            'Feature Set': list(results.keys()),
            'Num Features': [len(v['features']) for v in results.values()],
            'MSE (Mean)': [v['mse_mean'] for v in results.values()],
            'MSE (Std)': [v['mse_std'] for v in results.values()],
            'R² (Mean)': [v['r2_mean'] for v in results.values()],
            'R² (Std)': [v['r2_std'] for v in results.values()]
        })
        
        # 按MSE排序
        result_df = result_df.sort_values('MSE (Mean)')
        
        # 绘制MSE比较图
        plt.figure(figsize=(12, 6))
        plt.errorbar(result_df['Feature Set'], result_df['MSE (Mean)'], 
                     yerr=result_df['MSE (Std)'], fmt='o', capsize=5)
        plt.title('不同特征子集的MSE比较')
        plt.xlabel('特征子集')
        plt.ylabel('均方误差 (MSE)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        # 绘制R²比较图
        plt.figure(figsize=(12, 6))
        plt.errorbar(result_df['Feature Set'], result_df['R² (Mean)'], 
                     yerr=result_df['R² (Std)'], fmt='o', capsize=5)
        plt.title('不同特征子集的R²比较')
        plt.xlabel('特征子集')
        plt.ylabel('决定系数 (R²)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        return result_df, results
    
    def plot_feature_importance(self, method=None, top_n=20):
        """绘制特征重要性
        
        参数:
            method: 特征选择方法名称
            top_n: 显示前几个重要特征
        """
        if method is None and self.results:
            # 使用第一个可用的方法
            method = list(self.results.keys())[0]
            
        if method not in self.results:
            print(f"方法'{method}'不可用，请先运行特征选择")
            return
            
        # 获取特征得分
        scores = self.results[method]['scores']
        features = self.X.columns
        
        # 创建特征重要性数据框
        importance_df = pd.DataFrame({'feature': features, 'importance': scores})
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        # 只绘制前top_n个特征
        if len(importance_df) > top_n:
            importance_df = importance_df.head(top_n)
            
        # 绘制条形图
        plt.figure(figsize=(12, max(8, len(importance_df) * 0.3)))
        sns.barplot(x='importance', y='feature', data=importance_df)
        plt.title(f'特征重要性 ({method})')
        plt.xlabel('重要性分数')
        plt.ylabel('特征名称')
        plt.grid(True, axis='x')
        plt.tight_layout()
        plt.show()
        
        return importance_df

