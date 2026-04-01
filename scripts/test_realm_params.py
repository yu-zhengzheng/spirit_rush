#!/usr/bin/env python3
"""境界参数设计 - 直接计算N年后晋升比例"""

import math

def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def calc_promotion_rate(lifespan, mu, sigma, threshold, years):
    """计算years年后的晋升比例（考虑存活）"""
    total_promo = 0
    for t in range(1, years + 1):
        # t年后的总修为分布
        total_mu = t * mu
        total_sigma = math.sqrt(t) * sigma
        
        # 晋升概率
        z = (threshold - total_mu) / total_sigma
        promo_prob = 1 - normal_cdf(z)
        
        # 存活概率（均匀分布假设）
        survival = max(0, (lifespan - t + 0.5) / lifespan)
        
        total_promo += promo_prob * survival
    
    return total_promo

# 目标：60年后匹配金字塔
# 炼气50万 -> 筑基8万 = 16%
# 筑基8万 -> 金丹2000 = 2.5%
# 金丹2000 -> 元婴50 = 2.5%
# 元婴50 -> 化神1 = 2%

print("境界参数调试")
print("=" * 60)

# 1. 炼气->筑基 (目标16%)
# 60年总修为: μ=6000, σ=620
# 要16%在右尾，z≈0.994，threshold ≈ 6000 + 0.994*620 ≈ 6616
# 但实际上16%意味着大多数人升不了，所以threshold应该更高
# 让我用二分法找

def find_threshold(target_rate, lifespan, mu, sigma, years):
    """找到合适的阈值"""
    # 搜索范围
    lo = years * mu * 0.5
    hi = years * mu * 2
    
    for _ in range(50):
        mid = (lo + hi) / 2
        rate = calc_promotion_rate(lifespan, mu, sigma, mid, years)
        if rate > target_rate:
            lo = mid
        else:
            hi = mid
    
    return (lo + hi) / 2

# 调试各境界参数
tests = [
    ("炼气->筑基", 130, 100, 80, 16),
    ("筑基->金丹", 220, 80, 50, 2.5),
    ("金丹->元婴", 450, 50, 30, 2.5),
    ("元婴->化神", 900, 30, 20, 2),
]

results = []
for name, life, mu, sigma, target in tests:
    thresh = find_threshold(target/100, life, mu, sigma, 60)
    actual = calc_promotion_rate(life, mu, sigma, thresh, 60) * 100
    results.append((name, life, mu, sigma, thresh, actual))
    print(f"{name}: 阈值{thresh:.0f} → 实际{actual:.2f}% (目标{target}%)")

print("\n" + "=" * 60)
print("最终设计")
print("=" * 60)

print("""
┌─────────┬──────┬───────────┬─────┬──────────┬────────────┐
│ 境界    │ 寿元 │ 年均修为  │ σ   │ 晋升阈值 │ 60年晋升率 │
├─────────┼──────┼───────────┼─────┼──────────┼────────────┤
""")

for name, life, mu, sigma, thresh, rate in results:
    realm = name.split("->")[0].replace("化神", "化神期")
    print(f"│ {realm:7} │ {life:4} │ {mu:9} │ {sigma:3} │ {thresh:8.0f} │ {rate:10.2f}% │")

print("""├─────────┼──────┼───────────┼─────┼──────────┼────────────┤
│ 化神期  │ 2000 │ 20        │ 10  │ (飞升)   │ —          │
└─────────┴──────┴───────────┴─────┴──────────┴────────────┘
""")