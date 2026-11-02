"""
全局配置。

为什么单独抽一个文件？
面试可讲：成本单价、mock 耗时这类"业务参数"和代码逻辑分离，
换模型、换供应商时只改这里，不动业务代码。
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "pipeline.db"
MEDIA_DIR = DATA_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)

# ---- mock 生成参数（模拟真实推理耗时，方便观察进度条效果）----
MOCK_MIN_SECONDS = 3
MOCK_MAX_SECONDS = 8

# ---- 成本单价（元）----
# 面试可讲：成本必须精确到"每次生成调用"，而不是只算每分钟，
# 因为真正的成本杀手是"抽卡率"——生成 10 次采纳 1 次。
PRICE_PER_GENERATION = 1.2      # 每次生成调用固定成本
PRICE_PER_SECOND = 0.05         # 按生成时长计的增量

# ---- 一次生成产出的候选数量 ----
CANDIDATES_PER_SHOT = 3

# ---- 每个镜头最大重试次数 ----
MAX_ATTEMPTS = 3
