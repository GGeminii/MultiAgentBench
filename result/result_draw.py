import matplotlib.pyplot as plt
import numpy as np

# 设置全局样式
plt.style.use('seaborn-v0_8-whitegrid')

import matplotlib.pyplot as plt
import numpy as np

def draw_iteration_scores():
    # 配置中文
    plt.rcParams['font.sans-serif'] = ['SimSun']  # Windows
    # plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 23

    # 数据
    iterations = [1, 3, 5, 7, 9, 11]
    task_score = [73.33, 79.45, 85.33, 79.99, 66.67, 73.33]
    planning_score = [60, 66, 77.60, 74.2, 73.2, 78.18]
    communication_score = [50, 62, 78.4, 76.26, 80.36, 80.12]
    collaboration_score = [55, 64, 78.0, 75.23, 76.78, 79.15]

    # 绘图
    plt.figure(figsize=(12, 6))
    plt.title("不同迭代次数下gpt-4o-mini在研究协作场景中的表现", fontweight='bold')
    plt.xlabel("迭代次数")
    plt.ylabel("评估得分")
    plt.grid(True, linestyle='-', alpha=0.7)

    # 核心修改：所有折线改为虚线（linestyle='-'），保留显眼配色和标记
    plt.plot(iterations, task_score, marker='o', markersize=10, color='#1f77b4', linestyle='-', label='任务得分（TS）')
    plt.plot(iterations, planning_score, marker='^', markersize=10, color='#ff7f0e', linestyle='-', label='规划得分')
    plt.plot(iterations, communication_score, marker='s', markersize=10, color='#d62728', linestyle='-',
             label='沟通得分')
    plt.plot(iterations, collaboration_score, marker='D', markersize=10, color='#9467bd', linestyle='-',
             label='协作得分')

    # 图例保持原有配置
    plt.legend(
        loc='lower right',
        ncol=2,
        fontsize=20,
        columnspacing=2,
        handletextpad=0.8,
        borderpad=0.8,
        labelspacing=0.5
    )
    # 导出 SVG 矢量图
    plt.savefig('drawing/迭代次数得分图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()


def draw_agent_number_scores():
    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 23

    agent_numbers = [1, 2, 3, 4, 5, 6, 7, 8]
    ts_scores = [66.67, 66.67, 73.33, 86.67, 86.67, 87.89, 93.33, 86.67]
    cs_scores = [38, 82, 40, 63.2, 66, 72, 84, 73]
    avg_kpi = [100, 88.89, 56.25, 51.44, 47.09, 41.23, 37.04, 28.12]

    plt.figure(figsize=(12, 6))
    plt.title("不同智能体数量下gpt-4o-mini在研究协作场景中的表现", fontweight='bold')
    plt.xlabel("智能体数量")
    plt.ylabel("评估得分")
    plt.grid(True, linestyle='-', alpha=0.7)

    # 核心修改：所有折线改为虚线（linestyle='-'），统一样式
    plt.plot(agent_numbers, avg_kpi, marker='o', markersize=10, color='#1f77b4', linestyle='-', label='Avg KPI (%)')
    plt.plot(agent_numbers, cs_scores, marker='s', markersize=10, color='#d62728', linestyle='-', label='协作得分（CS）')
    plt.plot(agent_numbers, ts_scores, marker='^', markersize=10, color='#ff7f0e', linestyle='-', label='任务得分（TS）')

    # 图例保持原有配置
    plt.legend(
        loc='best',
        ncol=3,
        fontsize=20,
        columnspacing=1.5,
        handletextpad=0.8,
        borderpad=0.5
    )
    # 导出 svg 矢量图
    plt.savefig('drawing/智能体数量得分图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()

def ablation_study():
    # 配置字体和样式
    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 23

    configs = ['完整框架', 'ABL-RW', 'ABL-PN', 'ABL-RD']
    ts_scores = [76.6, 63.5, 72.5, 70.2]
    cs_scores = [72.6, 61.2, 69.3, 68.5]
    kpi_scores = [81.0, 60.5, 74.6, 72.3]
    rewards = [0.65, 0.38, 0.58, 0.55]
    convergences = [7, 13, 9, 10]

    # 柱状图
    plt.figure(figsize=(12, 6))
    bar_width = 0.2
    x = np.arange(len(configs))

    # 绘制柱状图（保留原有低饱和颜色和样式）
    bars1 = plt.bar(x - bar_width, ts_scores, bar_width, label='TS',
                    color='skyblue', edgecolor='navy', linewidth=1.5, alpha=0.6)
    bars2 = plt.bar(x, cs_scores, bar_width, label='CS',
                    color='lightgreen', edgecolor='darkgreen', linewidth=1.5, alpha=0.6)
    bars3 = plt.bar(x + bar_width, kpi_scores, bar_width, label='KPI (%)',
                    color='salmon', edgecolor='darkred', linewidth=1.5, alpha=0.6)

    # ===================== 核心修改：移除柱子内的数值文字（删除原标签代码） =====================
    # 原数值标签代码已全部删除，无其他改动

    # 水平图例（保持原有配置）
    plt.legend(
        loc='upper right',  # 位置保持右上角
        ncol=3,  # 3列水平排列
        frameon=False,  # 无边框（原有配置）
        fontsize=23,  # 字体大小
        columnspacing=2,  # 列之间的间隔
        handletextpad=0.8,  # 颜色块和文字之间的间距
        borderpad=0  # 图例内边距
    )

    # 图表样式（保持不变）
    plt.title("不同消融实验配置下的 TS/CS/KPI 得分对比", fontweight='bold')
    plt.xlabel("消融实验配置")
    plt.ylabel("得分")
    plt.xticks(x, configs)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, max(kpi_scores) + 8)
    plt.tight_layout()

    plt.savefig('drawing/消融实验柱状图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()

    # 雷达图（完全保留原有配置，无任何修改）
    metrics = ['TS', 'CS', 'KPI (%)', '平均奖励值', '收敛速度（迭代次数）']
    normalized_data = np.array([
        [76.6 / 100, 72.6 / 100, 81.0 / 100, 0.65 / 1, 1 / 7],
        [63.5 / 100, 61.2 / 100, 60.5 / 100, 0.38 / 1, 1 / 13],
        [72.5 / 100, 69.3 / 100, 74.6 / 100, 0.58 / 1, 1 / 9],
        [70.2 / 100, 68.5 / 100, 72.3 / 100, 0.55 / 1, 1 / 10]
    ])

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
    normalized_data_closed = np.concatenate((normalized_data, normalized_data[:, [0]]), axis=1)
    angles_closed = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    colors = ['lightblue', 'lightcoral', 'lightgreen', 'moccasin']
    labels = configs

    for i in range(len(configs)):
        ax.plot(angles_closed, normalized_data_closed[i], 'o-', markersize=10, color=colors[i],
                label=labels[i])
        ax.fill(angles_closed, normalized_data_closed[i], alpha=0.25, color=colors[i])

    ax.set_thetagrids(angles * 180 / np.pi, metrics, fontsize=20)
    for label, angle in zip(ax.get_xticklabels(), angles):
        label.set_rotation(angle * 180 / np.pi)
        label.set_horizontalalignment('center')
        label.set_verticalalignment('center')
        if '收敛速度' in label.get_text() or '平均奖励值' in label.get_text():
            label.set_fontsize(18)
            label.set_position((label.get_position()[0], label.get_position()[1] + 0.1))

    ax.set_title("不同实验配置的多指标雷达图对比", fontweight='bold', fontsize=28, y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.1), fontsize=16)
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('drawing/消融实验雷达图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()


def efficiency_study():
    # -------------------------- 字体全局配置 --------------------------
    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 33

    # -------------------------- 数据 --------------------------
    scenarios = ['研究协作', '编程合作', '价格商议']
    baseline_time = [26.50, 25.48, 7.14]
    our_time = [28.75, 9.47, 7.38]

    # 核心修改1：Token数据换算为「十万」为单位（除以100000）
    baseline_token = [340089 / 100000, 734046 / 100000, 144547 / 100000]  # 3.40/7.34/1.45
    our_token = [389868 / 100000, 237190 / 100000, 167149 / 100000]  # 3.90/2.37/1.67

    # ===================== 横向合并：1行2列 =====================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7))
    bar_width = 0.30
    x = np.arange(len(scenarios))

    # -------------------------------------------------------------------------
    # 子图1：时间对比 (a)
    # -------------------------------------------------------------------------
    bars1 = ax1.bar(x - bar_width / 2, baseline_time, bar_width, label='基线方法',
                    color='skyblue', edgecolor='navy', linewidth=1.5, alpha=0.6)
    bars2 = ax1.bar(x + bar_width / 2, our_time, bar_width, label='本文框架',
                    color='lightgreen', edgecolor='darkgreen', linewidth=1.5, alpha=0.6)

    # 核心修改3：移除柱子内的数值文字（删除原标签代码）

    ax1.set_title("不同场景下的任务执行时间对比（分钟）", fontweight='bold')
    ax1.set_xlabel("应用场景")
    ax1.set_ylabel("执行时间（分钟）")
    ax1.set_xticks(x, scenarios)

    # 核心修改2：给时间纵轴补充刻度（3-5个），让刻度更丰富
    ax1.set_ylim(0, max(baseline_time) + 8)
    ax1.set_yticks(np.arange(0, max(baseline_time) + 10, 10))  # 0/5/10/15/20/25/30...

    ax1.legend(loc='upper right', fontsize=33,
               columnspacing=1, handletextpad=0.8, borderpad=0)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # (a) 标注
    ax1.text(0.5, -0.45, '(a)', transform=ax1.transAxes,
             ha='center', va='center', fontsize=33, fontweight='bold')

    # -------------------------------------------------------------------------
    # 子图2：Token对比 (b)
    # -------------------------------------------------------------------------
    bars3 = ax2.bar(x - bar_width / 2, baseline_token, bar_width, label='基线方法',
                    color='salmon', edgecolor='darkred', linewidth=1.5, alpha=0.6)
    bars4 = ax2.bar(x + bar_width / 2, our_token, bar_width, label='本文框架',
                    color='lightgreen', edgecolor='darkgreen', linewidth=1.5, alpha=0.6)

    # 核心修改3：移除柱子内的数值文字（删除原标签代码）

    ax2.set_title("不同场景下的Token消耗对比", fontweight='bold')
    ax2.set_xlabel("应用场景")
    ax2.set_ylabel("Token消耗（十万）")  # 标签已匹配单位
    ax2.set_xticks(x, scenarios)

    # 核心修改2：给Token纵轴补充刻度（3-5个），适配十万单位
    ax2.set_ylim(0, max(baseline_token) + 1)
    ax2.set_yticks(np.arange(0, max(baseline_token) + 2, 3))  # 0/1/2/3/4/5/6/7/8...

    ax2.legend(loc='upper right', fontsize=33,
               columnspacing=1, handletextpad=0.8, borderpad=0)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # (b) 标注
    ax2.text(0.5, -0.45, '(b)', transform=ax2.transAxes,
             ha='center', va='center', fontsize=33, fontweight='bold')

    # -------------------------------------------------------------------------
    # 布局调整
    # -------------------------------------------------------------------------
    plt.tight_layout()

    plt.savefig('drawing/效率对比横向合并图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

def separate_efficiency_study():
    # -------------------------- 配置字体和样式 --------------------------
    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 23

    # -------------------------- 数据准备 --------------------------
    scenarios = ['研究协作', '编程合作', '价格商议']
    baseline_time = [26.50, 25.48, 7.14]
    baseline_token = [340089, 734046, 144547]
    our_time = [28.75, 9.47, 7.38]
    our_token = [389868, 237190, 167149]

    # ===================== 第一张图：时间对比柱状图 =====================
    plt.figure(figsize=(12, 6))
    bar_width = 0.2
    x = np.arange(len(scenarios))

    # 绘制柱状图
    bars1 = plt.bar(x - bar_width/2, baseline_time, bar_width, label='基线方法',
                    color='skyblue', edgecolor='navy', linewidth=1.5, alpha=0.6)  # skyblue低饱和蓝
    bars2 = plt.bar(x + bar_width/2, our_time, bar_width, label='本文框架',
                    color='lightgreen', edgecolor='darkgreen', linewidth=1.5, alpha=0.6)  # lightgreen低饱和绿

    # 添加数值标签（靠上位置，小字体避免遮挡）
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height * 0.8,
                 f'{height:.2f}', ha='center', va='center',
                 color='black', fontweight='bold', fontsize=10)
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height * 0.8,
                 f'{height:.2f}', ha='center', va='center',
                 color='black', fontweight='bold', fontsize=10)

    # 图表样式
    plt.title("不同场景下的任务执行时间对比（分钟）", fontweight='bold')
    plt.xlabel("应用场景")
    plt.ylabel("执行时间（分钟）")
    plt.xticks(x, scenarios)
    # 核心修改：图例水平排列（ncol=2）+ 调整间隔
    plt.legend(loc='upper right', frameon=False, fontsize=33,
               ncol=2, columnspacing=1, handletextpad=0.8, borderpad=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, max(baseline_time) + 8)
    # 添加(a)标注（居中靠下）
    plt.text(0.5, -0.45, '(a)', transform=plt.gca().transAxes,
             ha='center', va='center', fontsize=33, fontweight='bold')
    plt.tight_layout()

    # 保存独立SVG
    plt.savefig('drawing/效率对比_时间图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()  # 关闭画布避免干扰

    # ===================== 第二张图：Token对比柱状图 =====================
    plt.figure(figsize=(12, 6))
    bar_width = 0.2
    x = np.arange(len(scenarios))

    # 绘制柱状图
    bars3 = plt.bar(x - bar_width/2, baseline_token, bar_width, label='基线方法',
                    color='salmon', edgecolor='darkred', linewidth=1.5, alpha=0.6)  # salmon低饱和红
    bars4 = plt.bar(x + bar_width/2, our_token, bar_width, label='本文框架',
                    color='lightgreen', edgecolor='darkgreen', linewidth=1.5, alpha=0.6)  # lightgreen低饱和绿

    # 添加数值标签（科学计数法，避免数字过长）
    for bar in bars3:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height * 0.8,
                 f'{height:.0e}', ha='center', va='center',
                 color='black', fontweight='bold', fontsize=10)
    for bar in bars4:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height * 0.8,
                 f'{height:.0e}', ha='center', va='center',
                 color='black', fontweight='bold', fontsize=10)

    # 图表样式
    plt.title("不同场景下的Token消耗对比", fontweight='bold')
    plt.xlabel("应用场景")
    plt.ylabel("Token消耗数量")
    plt.xticks(x, scenarios)
    # 核心修改：图例水平排列（ncol=2）+ 调整间隔
    plt.legend(loc='upper right', frameon=False, fontsize=23,
               ncol=2, columnspacing=1, handletextpad=0.8, borderpad=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, max(baseline_token) + 100000)
    # 添加(b)标注
    plt.text(0.5, -0.45, '(b)', transform=plt.gca().transAxes,
             ha='center', va='center', fontsize=23, fontweight='bold')
    plt.tight_layout()

    # 保存独立SVG
    plt.savefig('drawing/效率对比_Token图.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

if __name__ == '__main__':
    draw_iteration_scores()
    draw_agent_number_scores()
    # ablation_study()
    # efficiency_study()
    # separate_efficiency_study()