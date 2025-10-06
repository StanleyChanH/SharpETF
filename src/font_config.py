"""
中文字体配置模块
用于确保matplotlib能够正确显示中文字符
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
import logging

logger = logging.getLogger(__name__)

def setup_chinese_font():
    """设置matplotlib中文字体"""

    # 定义可选的中文字体列表 - 优先使用实际可用的中文字体
    chinese_fonts = [
        'AR PL UMing CN',        # 文鼎PL简中宋 (实际可用，优先)
        'AR PL UKai CN',         # 文鼎PL简中楷 (实际可用)
        'Noto Sans CJK JP',      # 思源黑体日文
        'Noto Serif CJK JP',     # 思源宋体日文
        'WenQuanYi Micro Hei',   # 文泉驿微米黑
        'SimHei',                # 黑体 (Windows)
        'Microsoft YaHei',       # 微软雅黑 (Windows)
        'DejaVu Sans'            # 备用字体
    ]

    try:
        # 获取系统所有可用字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        # 找到第一个可用的中文字体
        selected_font = None
        for font in chinese_fonts:
            if font in available_fonts:
                selected_font = font
                break

        if selected_font:
            # 强制使用serif字体来支持Noto Serif CJK SC
            if 'Serif' in selected_font:
                plt.rcParams['font.serif'] = [selected_font] + [f for f in chinese_fonts if f != selected_font and 'Serif' in f]
                plt.rcParams['font.family'] = 'serif'
            else:
                plt.rcParams['font.sans-serif'] = [selected_font] + [f for f in chinese_fonts if f != selected_font]
                plt.rcParams['font.family'] = 'sans-serif'

            plt.rcParams['axes.unicode_minus'] = False

            logger.info(f"✅ 中文字体设置成功: {selected_font}")
            print(f"✅ 中文字体设置成功: {selected_font} (字体族: {'serif' if 'Serif' in selected_font else 'sans-serif'})")

        else:
            # 如果没有找到中文字体，使用系统默认字体并警告
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False

            logger.warning("⚠️ 未找到合适的中文字体，可能影响中文显示")
            print("⚠️ 未找到合适的中文字体，可能影响中文显示")
            print("可用字体:", available_fonts[:10])  # 显示前10个字体

    except Exception as e:
        logger.error(f"❌ 字体设置失败: {e}")
        print(f"❌ 字体设置失败: {e}")

        # 使用最基本的字体设置
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False

def test_chinese_font():
    """测试中文字体是否正常工作"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        # 创建一个简单的测试图
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        ax.plot(x, y, label='正弦波')
        ax.set_title('中文字体测试 - ETF投资组合优化')
        ax.set_xlabel('时间轴')
        ax.set_ylabel('收益率')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 保存测试图
        test_path = 'outputs/font_test.png'
        plt.savefig(test_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ 中文字体测试图已保存: {test_path}")
        return True

    except Exception as e:
        print(f"❌ 中文字体测试失败: {e}")
        return False

# 在模块导入时自动设置字体
if __name__ != "__main__":
    setup_chinese_font()