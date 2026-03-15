# 飞书Bot配置（MVP版）

## 方案A: 最简单的Webhook推送

### 步骤1: 创建Bot
1. 打开任意飞书群（或新建群）
2. 群设置 → 群机器人 → 添加机器人
3. 选择 "自定义机器人"
4. 复制 Webhook URL

### 步骤2: 配置到系统

编辑 `skills/feishu_sender.py`:

```python
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
```

### 步骤3: 测试推送

```bash
python3 skills/feishu_sender.py --test
```

---

## 方案B: 创建公开群（获客用）

### 步骤1: 建群
- 群名：**招标雷达免费预览**
- 群介绍：每日早8点推送3条精选政府采购商机
- 设置：可搜索、无需审核

### 步骤2: 配置入群欢迎
群管理 → 入群欢迎 → 设置欢迎语：

```
欢迎加入招标雷达！

🎯 每日精选政府采购商机
⏰ 早8点自动推送
📊 免费版：每日3条
💎 完整版：每日10条+周报

订阅完整版：https://openclaw-tender-radar.vercel.app/payment/
```

### 步骤3: 配置自动推送
- 添加自定义机器人
- 获取Webhook
- 配置到系统

---

## 推荐：先做方案A（5分钟）

理由：
- 最简单
- 能推送到你的群
- 能测试功能

公开群可以稍后做（不影响MVP）

---

## 关键配置项

```python
# skills/feishu_sender.py

# Webhook地址（从飞书群获取）
FEISHU_WEBHOOK_URL = "你的Webhook地址"

# 推送设置
PUSH_CONFIG = {
    'free_group': {
        'webhook': '免费群Webhook',
        'content': 'summary',  # 只推送摘要（3条）
        'time': '08:00'
    },
    'paid_users': {
        'webhook': None,  # 私聊用user_id
        'content': 'full',  # 完整版（10条）
        'time': '08:00'
    }
}
```

配置完成后，系统每天自动推送到飞书！
