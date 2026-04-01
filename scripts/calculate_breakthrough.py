#!/usr/bin/env python3
"""
境界晋升人数计算器

输入参数计算N年后晋升到下一境界的人数。
使用正态分布模拟每年修为累积，考虑陨落因素。
"""

import math
from typing import Optional


def normal_cdf(x: float) -> float:
    """标准正态分布的CDF（使用误差函数近似）"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def calculate_breakthrough(
    population: int,
    lifespan: int,
    mean_cultivation: float,
    std_cultivation: float,
    cultivation_needed: float = 10000,
    years: int = 60
) -> dict:
    """
    计算晋升人数
    
    参数:
        population: 该境界当前人口
        lifespan: 该境界平均寿元（年）
        mean_cultivation: 年均修为（正态分布均值）
        std_cultivation: 年均修为标准差
        cultivation_needed: 晋升所需修为（默认10000）
        years: 模拟年数
    
    返回:
        包含详细结果的字典
    """
    
    total_breakthrough = 0
    
    for year in range(1, years + 1):
        # 第year年的修为分布
        total_mean = year * mean_cultivation
        total_std = math.sqrt(year) * std_cultivation
        
        # 晋升所需修为的Z分数
        z_score = (cultivation_needed - total_mean) / total_std
        
        # 晋升概率（总修为超过阈值）
        breakthrough_prob = 1 - normal_cdf(z_score)
        
        # 存活概率（假设死亡均匀分布在境界期间）
        # 在第year年仍然存活的概率 ≈ (lifespan - year + 0.5) / lifespan
        survival_prob = max(0, (lifespan - year + 0.5) / lifespan)
        
        # 该年晋升人数
        breakthrough_in_year = population * breakthrough_prob * survival_prob
        total_breakthrough += breakthrough_in_year
    
    # 计算晋升比例
    breakthrough_rate = (total_breakthrough / population) * 100 if population > 0 else 0
    
    return {
        "population": population,
        "lifespan": lifespan,
        "mean_cultivation": mean_cultivation,
        "std_cultivation": std_cultivation,
        "cultivation_needed": cultivation_needed,
        "years": years,
        "breakthrough_count": total_breakthrough,
        "breakthrough_rate": breakthrough_rate,
        "remaining_population": population - total_breakthrough
    }


def print_result(result: dict):
    """格式化打印结果"""
    print(f"\n{'='*50}")
    print(f"境界晋升计算结果")
    print(f"{'='*50}")
    print(f"人口: {result['population']:,}")
    print(f"寿元: {result['lifespan']}年")
    print(f"年均修为: μ={result['mean_cultivation']}, σ={result['std_cultivation']}")
    print(f"晋升所需修为: {result['cultivation_needed']:,}")
    print(f"模拟年数: {result['years']}年")
    print(f"{'='*50}")
    print(f"晋升人数: {result['breakthrough_count']:,.2f}")
    print(f"晋升比例: {result['breakthrough_rate']:.4f}%")
    print(f"剩余人口: {result['remaining_population']:,.2f}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 5:
        # 命令行参数
        population = int(sys.argv[1])
        lifespan = int(sys.argv[2])
        mean_cult = float(sys.argv[3])
        std_cult = float(sys.argv[4])
        years = int(sys.argv[5]) if len(sys.argv) > 5 else 60
        
        result = calculate_breakthrough(
            population, lifespan, mean_cult, std_cult,
            cultivation_needed=10000, years=years
        )
        print_result(result)
    else:
        # 演示用例
        print("=== 演示用例 ===")
        
        # 示例1: 炼气期 -> 筑基期
        result = calculate_breakthrough(
            population=500000,  # 50万炼气期
            lifespan=120,       # 炼气期寿元120年
            mean_cultivation=100,
            std_cultivation=50,
            cultivation_needed=10000,
            years=60
        )
        print_result(result)
        
        # 示例2: 高标准差
        result2 = calculate_breakthrough(
            population=500000,
            lifespan=120,
            mean_cultivation=100,
            std_cultivation=200,  # 更大的方差
            cultivation_needed=10000,
            years=60
        )
        print(f"（标准差200的情况）")
        print_result(result2)