# OpenClaw 招标雷达 - 部署指南

## 当前状态

网站内容已生成完毕，位于 `site/` 目录。

## 部署选项

### 选项1: Vercel（推荐）

**步骤**:
1. 访问 https://vercel.com
2. 用 GitHub/GitLab/Bitbucket 账号登录
3. 点击 "Add New Project"
4. 导入项目或选择本地文件夹 `site/`
5. 点击 Deploy

**优点**: 免费、快速、自动HTTPS、全球CDN

---

### 选项2: Netlify

**步骤**:
1. 访问 https://www.netlify.com
2. 用 GitHub/GitLab 登录
3. 拖拽 `site/` 文件夹到部署区域
4. 获得公开URL

**优点**: 拖拽部署、免费、自动HTTPS

---

### 选项3: GitHub Pages

**步骤**:
1. 创建 GitHub 仓库
2. 上传 `site/` 内容到仓库
3. 进入 Settings → Pages
4. 选择 main 分支，root 目录
5. 保存后获得 URL

**优点**: 完全免费、与Git集成

---

### 选项4: 阿里云/腾讯云对象存储

**步骤**:
1. 购买对象存储服务（OSS/COS）
2. 创建 bucket，开启静态网站托管
3. 上传 `site/` 文件
4. 绑定自定义域名

**优点**: 国内访问快、稳定

---

### 选项5: 本地测试（临时）

```bash
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site
python3 -m http.server 8080
```
访问 http://localhost:8080

---

## 快速部署脚本

### Vercel CLI 部署（需先登录）

```bash
cd site
npx vercel login
npx vercel --prod
```

### Netlify CLI 部署（需先登录）

```bash
cd site
npx netlify login
npx netlify deploy --prod
```

---

## 部署后配置

1. **记录公开URL**（如 https://xxx.vercel.app）
2. **更新收款页面链接**（在推广文案中）
3. **提交到搜索引擎**:
   - https://search.google.com/search-console
   - https://www.bing.com/webmasters

---

## 收款页面测试

部署后访问:
- `https://你的域名/payment/`
- 测试微信/支付宝收款码是否正常显示

---

## 下一步

1. 选择上方任一方式部署
2. 获得公开URL后告诉我
3. 我帮你配置自动获客流程

---

**建议**: 先用 Vercel 或 Netlify 快速验证，后期再迁移到国内服务器。
