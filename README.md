# SM2 实现优化项目
本仓库提供 SM2 算法的 Python 实现，包括基础椭圆曲线运算、签名/验证、优化，以及签名陷阱的 POC 验证。基于附件讲义（20250713-wen-sm2-public.pdf）进行总结和实现。
项目结构

**src/sm2.py**：SM2 核心实现，包括椭圆曲线点运算、SM3 哈希、密钥生成、签名/验证。
**src/sm2_optimized.py**：SM2 优化版本（后续添加）。
**poc/**：签名陷阱 POC 和伪造签名（后续添加）。

## 运行方式
运行以下命令测试基础功能（无需外部依赖）：
```
python src/sm2.py
```

## 1. ECC 基础
椭圆曲线定义在有限域 $\mathbb{F}_q$ 上，方程为 $y^2 = x^3 + ax + b$，其对称性（$(x, y)$ 和 $(x, -y)$ 均在曲线上）允许点压缩表示。
有限域 $\mathbb{F}_q$：

元素个数 $| \mathbb{F}_q | = q$，其中 $q = p^m$（$p$ 为素数，$m$ 为正整数）。
若 $m=1$，为素域；若 $m \geq 2$，为扩展域（如 $m=2$ 为二元域）。
特征为 $p$。

### 群阶与循环子群：

曲线群 $E(\mathbb{F}_q)$ 的阶为 $N = \#E(\mathbb{F}_q)$。
寻找循环子群 $$，其阶 $r$ 为 $N$ 的最大素因子，余因子 $h = N/r$。
生成子群：随机选 $P \in E(\mathbb{F}_q)$，令 $G = h \cdot P$，则 $$ 阶为 $r$，同构于 $\mathbb{Z}_r$。

### 点加法与点倍：

点加法（$P + Q$，$P = (x_1, y_1)$，$Q = (x_2, y_2)$，$P \neq Q$）：$$ \lambda = \frac{y_2 - y_1}{x_2 - x_1} \mod p $$$$ x_3 = \lambda^2 - x_1 - x_2 \mod p $$$$ y_3 = \lambda (x_1 - x_3) - y_1 \mod p $$
点倍（$2P$）：$$ \lambda = \frac{3 x_1^2 + a}{2 y_1} \mod p $$$$ x_3 = \lambda^2 - 2 x_1 \mod p $$$$ y_3 = \lambda (x_1 - x_3) - y_1 \mod p $$

## SM2 参数
SM2 定义在素域 $\mathbb{F}_q$（256 位素数 $q$）上，参数包括：

+ 曲线参数 $a, b$。
+ 基点 $G = (x_G, y_G)$，阶为 $n$。
+ 余因子 $h = \#E(\mathbb{F}_q) / n$。具体参数见 src/sm2.py
