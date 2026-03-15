# 飞书Bot配置指南

## 快速配置（5分钟）

### 步骤1: 创建飞书群
1. 打开飞书 → 点击"+" → 创建群组
2. 群名: **招标雷达免费预览**
3. 群介绍: 每日早8点推送精选政府采购商机
4. 设置: 可搜索、无需审核加入

### 步骤2: 添加机器人
1. 进入群聊 → 右上角"..." → 群设置
2. 点击"群机器人" → "添加机器人"
3. 选择"自定义机器人"
4. 机器人名字: 招标雷达
5. 点击"添加"

### 步骤3: 复制Webhook
1. 添加后会显示Webhook地址
2. 格式: `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx`
3. 复制整个地址

### 步骤4: 配置到系统
编辑文件:
```bash
/home/daministrator/.openclaw/workspace/openclaw-income-factory/config/feishu.conf
```

添加:
```
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的地址
```

### 步骤5: 测试
```bash
cd ~/openclaw-income-factory
python3 skills/feishu_sender.py --test
```

## 使用场景

### 场景1: 免费预览群
- 每日推送3条精选招标
- 用户主动加入
- 自然转化到付费

### 场景2: 付费用户群
- 每日推送10条完整版
- 周报分析
- VIP服务

## 安全提醒
⚠️ Webhook地址不要泄露！
- 相当于群的"钥匙"
- 任何人拿到都可以发消息
- 如泄露，在飞书中删除机器人重新创建

## 故障排除

### 发送失败
1. 检查Webhook地址是否正确
2. 检查网络连接
3. 检查机器人是否被移出群聊

### 消息格式错误
- 飞书对Markdown支持有限
- 避免复杂表格
- 使用简单文本+链接
