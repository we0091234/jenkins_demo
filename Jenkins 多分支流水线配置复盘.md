# Jenkins 多分支流水线配置复盘

## 1. 适用场景与目标

这份文档用于记录当前仓库的 Jenkins 多分支流水线配置，方便后面复习和排查。

适用场景：

- GitHub + Jenkins `Multibranch Pipeline`
- `Jenkinsfile` 放在仓库根目录
- 仓库地址：`https://github.com/we0091234/jenkins_demo.git`

目标：

- 功能分支 / PR 跑一次 CI
- merge 到 `main` 后再跑一次完整 CICD

## 2. 当前 Jenkins 配置清单

### 2.1 任务基本信息

- 任务类型：`Multibranch Pipeline`
- 描述：`jenkins demo`

### 2.2 Branch Source

- Branch Source：`GitHub`
- Credentials：当前 GitHub 凭据
- Repository URL：`https://github.com/we0091234/jenkins_demo.git`

### 2.3 行为（Behaviors）

- `发现分支`
  - 策略：`不包括作为 PRs 的分支`
- `Discover pull requests from origin`
  - 策略：`当前 Pull Request 的版本`
- `从派生库上发现 Pull Request`
  - 当前已开启
  - 如果以后不处理 fork PR，可以删除
- `Clean before checkout`
  - 已开启
  - `Delete untracked nested repositories` 不勾
- `通过 SSH 检出`
  - 已开启
  - 当前使用构建节点 key
  - 需要确认这把 key 已经加到 GitHub，可被仓库访问

### 2.4 Build Configuration

- Mode：`by Jenkinsfile`
- 脚本路径：`Jenkinsfile`

### 2.5 扫描触发器

- `Periodically if not otherwise run`
  - 当前未勾选

说明：

- 如果 webhook 稳定，可以不勾
- 如果 webhook 不稳定，可以后面加定时扫描做兜底

### 2.6 孤儿项目策略

- `删除旧的流水线`：已勾

## 3. 触发逻辑说明

今天最容易混淆的是这三类构建：

### 3.1 发现分支

作用：

- 发现普通分支，比如 `main`、`feature/*`
- 当这些分支有新提交时，会触发普通分支构建

结论：

- push 到功能分支，可能触发一次 branch build

### 3.2 Discover pull requests from origin

作用：

- 当创建 PR 或更新 PR 时，触发 PR 构建

结论：

- 提 PR 后，会再触发一次 PR build

### 3.3 main 构建

作用：

- PR merge 到 `main` 后，`main` 有了新的 commit
- Jenkins 发现 `main` 最新提交变了，就会自动再跑一次 `main` 构建

结论：

- merge 到 `main` 后，会自动触发一次 `main` 构建

### 3.4 当前实际现象

当前这套单一 multibranch 任务下，常见现象是：

1. push 功能分支：一次分支构建
2. 提 PR：一次 PR 构建
3. merge 到 `main`：一次 `main` 构建

说明：

- 第 3 次构建必须保留，这是部署所需
- 前 1、2 次存在一定重复，这是当前单一 multibranch 配置下的正常现象

## 4. Jenkinsfile 行为总结

根据当前仓库里的 `Jenkinsfile`，流水线行为如下：

### 4.1 所有分支 / PR 都会执行

- 安装依赖
- 单元测试
- e2e
- Docker build

### 4.2 只有 `main` 才会执行

- `Deploy`
- `Cleanup images`

### 4.3 关键理解

- merge 后触发完整构建，不需要额外单独配置“merge trigger”
- 因为 multibranch 会自动感知 `main` 分支最新 commit 的变化
- Jenkins 不关心这次变更是“直接 push 到 main”还是“PR merge 到 main”
- 只要 `main` 更新，就会触发 `main` 构建

## 5. HTTPS 与 SSH 的区别

这部分今天最容易混淆，需要单独记住。

### 5.1 GitHub Branch Source 的仓库地址

`GitHub Branch Source` 里的仓库地址字段只接受 HTTPS：

```text
https://github.com/we0091234/jenkins_demo.git
```

这里的 HTTPS 用于：

- 识别仓库
- 发现分支
- 发现 PR

### 5.2 实际拉代码

真实拉代码可以通过 `通过 SSH 检出` 走 SSH。

也就是说：

- 仓库源地址继续写 HTTPS
- 检出方式可以单独切到 SSH

关键结论：

- 仓库地址必须是 HTTPS，不代表实际 checkout 不能走 SSH

## 6. 今天遇到的问题与解释

### 6.1 PR 没有自动出现构建

现象：

- 提了 PR 后，GitHub 页面没有立刻看到构建
- 手动点 `立刻扫描 仓库` 后，PR 被发现了

说明：

- PR discovery 配置本身是通的
- webhook 自动触发链路不一定完全稳定

### 6.2 GitHub `Checks 0`

现象：

- GitHub PR 页面显示 `Checks 0`

说明：

- 不代表 Jenkins 没有构建
- 可能只是 Jenkins 没有成功回写状态到 GitHub

### 6.3 checkout 卡在 `git fetch https://github.com/...`

现象：

- 构建经常卡在 `git fetch`

说明：

- 不是仓库太大
- 更像 Jenkins 到 GitHub 的 HTTPS / TLS 网络问题

### 6.4 `Resource not accessible by personal access token`

现象：

- Jenkins 无法更新 GitHub commit status

说明：

- GitHub token 权限不足
- Jenkins 无法回写状态到 GitHub

### 6.5 checkout 失败后 `junit` 又报错

现象：

- checkout 失败后，`post` 里的 `junit` 又继续报错

说明：

- 这是后续连带错误
- 第一根因仍然是 `Checkout SCM` 失败

## 7. 推荐的日常使用流程

以后推荐固定按下面步骤操作：

1. 切回 `main`
2. 执行 `git pull --rebase origin main`
3. 新建功能分支
4. 开发并提交
5. push 分支
6. 提 PR
7. 等 Jenkins 跑 PR 构建
8. merge 到 `main`
9. 等 Jenkins 跑 `main` 构建和部署
10. 删除本地和远程功能分支

## 8. Git 相关复习点

### 8.1 `git pull --rebase`

意思是：

- 先拿远程最新提交
- 再把本地提交重新接到远程最新提交后面

### 8.2 `C` 和 `C'` 的区别

- 内容可能类似
- 但 commit id 不同
- 因为父提交变了

举例：

```text
原来：A - B - C
远程：A - B - D
rebase 后：A - B - D - C'
```

### 8.3 如果 rebase 冲突

处理顺序：

1. 手动修改冲突文件
2. `git add`
3. `git rebase --continue`

如果不想继续：

```bash
git rebase --abort
```

## 9. 重点记忆

- `发现分支` 负责普通分支构建
- `Discover pull requests from origin` 负责 PR 构建
- merge 到 `main` 后自动触发 `main` 构建
- `Jenkinsfile` 里 `main` 条件决定是否部署
- 仓库源地址写 HTTPS，不代表实际 checkout 不能走 SSH
- 当前单一 multibranch 任务下，`branch build + PR build + main build` 是可能出现的
