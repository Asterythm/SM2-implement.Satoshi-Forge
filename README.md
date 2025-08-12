# SM2 实现优化项目

本仓库提供SM2算法的Python实现，包括基础椭圆曲线运算、签名/验证、优化，以及签名陷阱的POC验证。

## 项目结构
- `src/sm2.py`：SM2核心实现，包括椭圆曲线点运算、SM3哈希、密钥生成、签名/验证。
- `src/sm2_optimized.py`：SM2优化版本（后续添加）。
- `poc/`：签名陷阱POC和伪造签名（后续添加）。

## 运行方式
运行 `python src/sm2.py` 测试基础功能（无外部依赖）。

## Elliptic Curve Cryptography

### 1. ECC基础
椭圆曲线方程：$y^2 = x^3 + a x + b$（有限域 $\mathbb{F}_q$ 上），对称性允许点压缩表示。

**有限域 $\mathbb{F}_q$**：
- 元素个数 $q = p^m$（$p$ 为素数，$m$ 为正整数）。
- 若 $m = 1$，为素域；若 $m \geq 2$，为扩展域（如 $m = 2$ 为二元域）。

**群阶与循环子群**：
- 曲线群阶 $|E(\mathbb{F}_q)|$，表示椭圆曲线群的元素个数。
- 循环子群阶 $r$ 为 $|E(\mathbb{F}_q)|$ 的最大素因子，余因子 $h = |E(\mathbb{F}_q)| / r$。
- 生成循环子群：随机选取点 $P \in E(\mathbb{F}_q)$，计算 $G = h \cdot P$，其阶为 $r$，子群 $\langle G \rangle$ 同构于 $\mathbb{Z}_r$。

**数学推导：点加法（P + Q）**：
- 设 $P = (x_1, y_1)$，$Q = (x_2, y_2)$，斜率 $\lambda = \frac{y_2 - y_1}{x_2 - x_1} \mod p$。
- $x_3 = \lambda^2 - x_1 - x_2 \mod p$。
- $y_3 = \lambda (x_1 - x_3) - y_1 \mod p$。

**点倍（2P）**：
- 斜率 $\lambda = \frac{3 x_1^2 + a}{2 y_1} \mod p$，然后按点加公式计算。

### 2. SM2参数
- 有限域 $\mathbb{F}_q$：$q$ 为256位素数。
- 曲线参数：$a, b$ 定义方程，基点 $G = (x_G, y_G)$，阶 $n$，余因子 $h = |E(\mathbb{F}_q)| / n$。
- PDF Page 2 参数已用于代码实现。

后续更新将添加优化、签名陷阱及伪造签名的总结和推导。

### 3. SM2实现优化
**标量乘 $Q = k P$**：
- 基础算法：double-and-add。
- **推导**：
  - 将 $k$ 展开为二进制：$k = \sum k_i 2^i$，则 $Q = \sum k_i (2^i P)$。
  - 算法：初始化 $Q = O$，$addend = P$。对 $k$ 的每位，若 $k_i = 1$，则 $Q = Q + addend$；每次 $addend = 2 \cdot addend$。
- **优化**：滑动窗口法（窗口大小 $w = 4$）：
  - 预计算 $[1, 2, \ldots, 2^w-1]P$，将 $k$ 分块解析，减少点加次数（约降低 25% 操作）。
  - 实现见 `sm2_optimized.py`。

**模逆运算**：
- 使用扩展欧几里德算法求 $k^{-1} \mod n$。
- **推导**：
  - 目标：求 $gcd(r_0, r_1) = s r_0 + t r_1 = 1$，则 $t$ 为 $r_1^{-1} \mod r_0$。
  - 初始化：$s_0 = 1, t_0 = 0; s_1 = 0, t_1 = 1$。
  - 迭代：$q_{i-1} = (r_{i-2} - r_i) / r_{i-1}$，更新 $s_i = s_{i-2} - q_{i-1} s_{i-1}$，$t_i = t_{i-2} - q_{i-1} t_{i-1}$，直到 $r_i = 0$。
  - 返回 $t = t_{i-1} \mod r_0$。

**公钥格式**：
- 未压缩：04 || x || y（x, y 各256位）。
- 压缩：02 || x（若 y 偶数）或 03 || x（若 y 奇数）。
- 恢复：由 $x$ 计算 $y^2 = x^3 + a x + b \mod p$，求平方根 $\beta$，根据奇偶调整。


### 4. SM2签名陷阱
**签名算法**：
- 计算 $Z_A = H_{256}(ENTLA || ID_A || a || b || x_G || y_G || x_A || y_A)$。
- 设置 $M' = Z_A || M$，$e = H_v(M')$（$H_v$ 为 SM3，输出 $v = 256$ 位）。
- 随机 $k \in [1, n-1]$，计算 $kG = (x_1, y_1)$，$r = e + x_1 \mod n$。
- 计算 $s = (1 + d_A)^{-1} \cdot (k - r \cdot d_A) \mod n$。
- 签名 $(r, s)$。

**验证算法**：
- 计算 $Z_A$，$M' = Z_A || M$，$e = H_v(M')$。
- 计算 $t = r + s \mod n$，$(x_1, y_1) = s G + t P_A$。
- 检查 $R = e + x_1 \mod n = r$。

**陷阱1: 泄露 k 导致 d 泄露**：
- **推导**：
  - $s (1 + d_A) = k - r d_A \mod n$。
  - 变形：$s + s d_A = k - r d_A$。
  - $s + r d_A + s d_A = k$。
  - $d_A (s + r) = k - s$。
  - $d_A = (k - s) (s + r)^{-1} \mod n$。
- POC：`leak_k.py`，验证泄露 k 后恢复 d。

**陷阱2: 同一用户重用 k 签名不同消息**：
- **推导**：
  - 消息 $M_1$：$s_1 (1 + d_A) = k - r_1 d_A$。
  - 消息 $M_2$：$s_2 (1 + d_A) = k - r_2 d_A$。
  - 相减：$(s_1 - s_2) (1 + d_A) = (r_2 - r_1) d_A$。
  - $s_1 - s_2 + (s_1 - s_2) d_A = (r_2 - r_1) d_A$。
  - $d_A (s_1 - s_2 - r_2 + r_1) = s_2 - s_1$。s
  - $d_A = (s_2 - s_1) (s_1 - s_2 + r_1 - r_2)^{-1} \mod n$。
- POC：`reuse_k_same_user.py`，验证重用 k 恢复 d。

**陷阱3: 不同用户重用 k**：
- **推导**：
  - Alice: $s_1 (1 + d_A) = k - r_1 d_A$，$d_A = (k - s_1) (s_1 + r_1)^{-1} \mod n$。
  - Bob: s_2 (1 + d_B) = k - r_2 d_B$，$d_B = (k - s_2) (s_2 + r_2)^{-1} \mod n$。
  - 若 k 共享，Alice 可计算 Bob 的 $d_B$，反之亦然。
- POC：`reuse_k_diff_users.py`，验证互推私钥。

**陷阱4: 同一 d 和 k 用于 ECDSA 和 SM2**：
- **推导**：
  - ECDSA: s_1 = k^{-1} (e_1 + r_1 d) \mod n$。
  - SM2: $s_2 = (1 + d)^{-1} (k - r_2 d) \mod n$。
  - 联立：
    - $d r_1 = k s_1 - e_1 \mod n$。
    - $d s_2 + r_2 d = k - s_2 \mod n$。
    - 解得: $d = (s_1 s_2 - e_1) (r_1 - s_1 s_2 - s_1 r_2)^{-1} \mod n$。
- POC：`ecdsa_sm2_same_dk.py`，验证跨算法泄露 d。
