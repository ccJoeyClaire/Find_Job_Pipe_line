### Git 基本概念（用于版本控制）

- 仓库（repo）：存代码和历史记录的地方，本地和 GitHub 上各有一份。

- 提交（commit）：一次“保存快照”，记录某一时刻的代码状态。

- 分支（branch）：并行开发的“时间线”，常见 main（或 master）、dev、功能分支。

------

### 本地常用操作流程（单人 / 日常）

```bash
\# 1. 初始化仓库（已有仓库就跳过）

git init

\# 2. 查看当前状态

git status

\# 3. 把改动加入暂存区

git add <文件>     # 如：git add app.py

git add .        # 所有改动

\# 4. 提交（加说明）

git commit -m "feat: 初始化项目结构"

\# 5. 查看历史

git log --oneline
```



------

### 分支与多人协作基本流程

#### 创建与切换分支

```bash
\# 创建并切到新分支（开发新需求/修 bug）

git checkout -b feature/add-login  # 新功能

\# 或

git checkout -b fix/bug-123    # 修 bug

\# 在分支上开发、提交

git add .

git commit -m "feat: 完成登录接口"
```



#### 与远程同步（GitHub）

```bash
\# 第一次关联远程仓库

git remote add origin https://github.com/<user>/<repo>.git

\# 推送本地分支到远程

git push -u origin feature/add-login

\# 之后同一分支只需要

git push
```



#### 更新本地代码（避免冲突）

```bash
\# 回到主分支

git checkout main

\# 拉取最新代码

git pull origin main

\# 把主分支更新合并到自己分支

git checkout feature/add-login

git merge main   # 或者用 rebase：git rebase main
```



------

### 解决冲突（简要）

1. git pull 或 git merge 时提示冲突。

2. 打开提示冲突的文件，手动修改保留的内容。

3. 修改后：

```bash
git add <有冲突的文件>

git commit     # 完成合并提交
```



------

### GitHub 常用操作（简洁版）

- 创建远程仓库

- GitHub 网页 → New repository → 填名称 → 创建。

- 本地执行：

- ```bash
    git remote add origin https://github.com/<user>/<repo>.git
  
    git push -u origin main
  ```

  

- Pull Request（推荐多人协作方式）

1. 本地创建分支开发 → 提交 → 推送到 GitHub（git push -u origin feature/...）。

1. 在 GitHub 仓库页面点击 Compare & pull request。

1. 填标题和说明 → 选择目标分支（一般 main/dev）→ 提交 PR。

1. 让同事 Review、评论、修改。

1. 审核通过后 Merge，删除分支（可选）。

- Issues

- 用于记录需求、Bug、待办事项。

- GitHub 仓库 → Issues → New issue → 填标题/描述。

- 可关联 PR（在 PR 描述里写 Fixes #<issue-number>）。

- Code Review 建议（简要）

- 提交信息清晰，例如：feat: 增加职位筛选接口 / fix: 修复 MinIO 连接超时问题。

- 一个 PR 只做一件事，避免太大。

- Review 时关注：逻辑正确性、错误处理、可读性、是否影响已有功能。

------

### 推荐基础习惯（总结）

- 每个功能一个分支：feature/... / fix/...。

- 小步提交：每次改动说明清楚，便于回滚。

- 先拉后推：git pull → 解决冲突 → git push。

- 所有改动通过 PR 合并：保证有人 Review，减少线上事故。