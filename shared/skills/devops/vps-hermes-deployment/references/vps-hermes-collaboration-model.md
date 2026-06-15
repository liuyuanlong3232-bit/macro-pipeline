# VPS Hermes 协作模式

## 架构

```
用户 ←→ 本地 Hermes（我）
               │
               ├─ SSH (root) → VPS 系统（改文件/跑脚本/cron）
               │
               └─ hermes chat -q → VPS Hermes（诊断问题、分析报告）
```

## 分工

| 角色 | 能做什么 | 不能做什么 |
|------|---------|-----------|
| **VPS Hermes** | 诊断问题、分析报告、生成内容、读取日志 | ❌ 改系统文件、改.env、未经批准的命令 |
| **本地 Hermes (SSH root)** | 改系统文件、修cron、跑脚本、scp | ❌ 在VPS上对话（我是本地Hermes） |
| **用户** | 最终决策 | — |

## 典型协作流程

### 发现问题
```
用户: "今天为什么没发报告"
  → VPS Hermes (hermes chat -q): 检查cron/日志 → 发现语法错误
  → 报告给用户: "cron 第8行6个时间字段，整文件被忽略"
  → 用户: "修"
  → 本地 Hermes (SSH): sed -i 修复 → 验证 → 完成
```

### 为什么 VPS Hermes 不能自修
1. `patch` 拒绝写 `/etc/cron.d/`（系统保护）
2. `terminal` 被 "User denied" 拦截（没人在线批准）
3. 读不了 `.env` 文件（凭证保护）

**结论：** VPS Hermes是**诊断师**，本地 Hermes (SSH) 是**执行者**。

## 发给 VPS Hermes 的命令

```bash
# 直接问问题
ssh vps "hermes chat -q '检查定时任务是否正常'"

# 问具体问题
ssh vps "hermes chat -q '查看最近报告日志，为什么没发邮件'"

# 续接之前会话
ssh vps "hermes chat --resume <session_id> -q '你刚才说的修复方案，确认一下'"
```

## 局限

- `hermes chat -q` 超时默认为30s，复杂问题可能超时
- VPS Hermes 分析需要消耗 MiMo Token Plan Credits
- 诊断结果需要用户确认后才能执行修复
