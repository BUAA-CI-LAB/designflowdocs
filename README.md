# 面向 LoongArch 国产自主指令集：从 CPU 设计到芯片实现

本目录是可独立维护的 **XeLaTeX 书籍工程**，由 `designflowdocs` 整理迁移。以后直接修改 `.tex` 书稿；日常生成 PDF 不需要 RStudio、R、bookdown、knitr、Pandoc、Python、联网或另外两本书的目录。

## 编译

在本目录运行：

```sh
latexmk main.tex
```

输出为 **`build/main.pdf`**。已配置 XeLaTeX、多轮编译、SyncTeX 和独立输出目录。

- WSL / Linux / macOS：也可运行 `sh build.sh`。
- Windows：也可运行 `build.cmd`，需要将 TeX 发行版的 `latexmk` 加入 PATH。
- VS Code：打开整个工程，启用 LaTeX Workshop，打开 `main.tex` 执行构建。工程已提供配置，保存时自动编译。
- TeXstudio / TeXworks：使用 XeLaTeX 或 latexmk 构建 `main.tex`；推荐 latexmk 自动完成目录与引用的多轮更新。

常用命令：

```sh
latexmk main.tex
latexmk -pvc main.tex  # 持续监听，Ctrl+C 停止
latexmk -c main.tex    # 清理中间文件，保留 PDF
latexmk examples/code-styles.tex  # 重建字体与高亮样张
```

依赖含中文支持的 TeX 发行版，包括 `ctex`、Fandol、fontspec、unicode-math、listings、xeCJK-listings、longtable、booktabs、hyperref、bookmark、xurl、latexmk 等。本机 WSL 的 TeX Live 2025 已实际验证；Windows 原生构建尚未实测。构建使用 `-no-shell-escape`。

## 文件组织

```text
main.tex                  主文件、章节顺序和前后置页
config/book-info.tex      书名、作者、日期和 PDF 元数据
config/preamble.tex       正文与代码字体、开本、图表样式
config/code-style.tex     代码环境、颜色和语言规则
chapters/00-preface.tex   前言
chapters/01-*.tex … 09-*  9 个正文章节
chapters/20-references.tex 12 条手工参考文献
chapters/30-resources.tex 相关链接
assets/                   70 个原始资源文件
fonts/                    DejaVu 字体和许可证
build/main.pdf            完整书籍
examples/code-styles.tex  字体与代码高亮样张源文件
build/code-styles.pdf     编译好的样张
migration/                修订清单、来源与验收记录
scripts/check_project.py  可选的结构与迁移完整性检查
```

保留原书 Letter 开本及大致页边距。前置部分使用罗马页码，9 个正文章节使用阿拉伯页码，参考文献和相关链接不编号。正文共 12 份分章、153 个标题、67 幅图、9 个表格。分页随字体、代码折行及笔误修复自然变化。

`assets/` 与 `fonts/` 是真实文件，全部图片已随工程复制。无需安装 Windows 宋体或仿宋；中文使用 TeX 自带 Fandol，西文使用 Latin Modern。复制整个目录即可携带书稿。

## 修改书稿

**正文和章节：** 编辑 `chapters/`，调整章节顺序时修改 `main.tex`。新工程不会与旧 Rmd 自动同步，以新 `.tex` 为后续维护主稿。

**代码：** 程序使用 Latin Modern Mono，中文注释使用仿宋风格；目录树、日志及文本说明使用 DejaVu Sans Mono，保证线条和特殊空格完整。代码保留原始缩进及 TAB；可以跨页，长行自动折行。

```tex
\begin{CodeBlock}[language=BookSystemVerilog]
// 时序逻辑示例
always_ff @(posedge clk) begin
  if (!reset_n) data <= '0;
  else data <= next_data;
end
\end{CodeBlock}
```

代码环境内直接粘贴源代码，不要为 `$`、`_`、`#` 加 LaTeX 转义。高亮由 `listings` 在每次 XeLaTeX 编译时生成，代码内容不会执行。全书 176 个代码块均已标注语言，其中 168 个启用语法配色，8 个目录树、日志或文本说明保留纯文本样式。

| 内容 | `language` |
|---|---|
| Verilog / SystemVerilog | `BookVerilog` / `BookSystemVerilog` |
| C / C++ | `BookC` / `BookCpp` |
| Scala、Chisel、SpinalHDL | `BookScala` |
| Bash、Shell 命令 | `BookShell` |
| C Shell 脚本 | `BookCShell` |
| LoongArch 汇编 | `BookLoongArch` |
| Makefile | `BookMake` |
| JSON 配置，含原稿中的注释示例 | `BookJSON` |
| 设备树 DTS | `BookDTS` |
| Kconfig / defconfig | `BookConfig` |
| 链接脚本 | `BookLinker` |
| EDA Tcl | `BookTcl` |
| 目录树、终端输出、纯文本说明 | `BookText` |

关键词使用深蓝，类型和部分领域标识使用紫色，注释为绿色，字符串为棕色；配有浅底色和细边线。关键词另加粗，便于黑白打印。配色、字号和自定义关键词集中在 `config/code-style.tex`。与上一本迁移工程采用相同样式，本书增加了 C++、JSON、C Shell 等规则。

行内代码使用 `\texttt{reset\_n}`，网址使用 `\url{https://example.com/path}`。行内代码中的特殊字符仍需 LaTeX 转义。

**插图和引用：** 图片路径带明确扩展名。新增插图先写标题，再写标签；正文使用 `图\ref{fig:example}`。

```tex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{assets/03/eula-arch.png}
  \caption{示例图标题}
  \label{fig:example}
\end{figure}
```

**表格：** 使用可跨页的 `longtable`。段落型单元格内用 `\newline{}` 换行，表格行以 `\\` 结束。不要再插入 HTML `<br>`。

**书名和日期：** 修改 `config/book-info.tex`。日期默认取编译当天，需要固定版本日期时将 `\date{\today}` 改为具体日期。

**参考文献：** 现有 12 条参考文献是手工条目，当前不运行 BibTeX 或 Biber。新增文献直接维护参考文献章，或以后单独引入自动文献管理。

## GitHub 同步维护

远程仓库：<https://github.com/BUAA-CI-LAB/designflowdocs>，主分支为 `main`。
书稿、图片、字体、配置及迁移记录纳入版本管理；`build/` 下的书籍 PDF（`main.pdf`）和代码样张（`code-styles.pdf`）也同步到仓库，便于直接下载阅读。编译缓存、日志和 SyncTeX 等中间文件继续忽略。
修改书稿或代码样式后，请重新编译对应的 PDF，并与源文件一起提交。

本目录已关联远程仓库。开始修改前，先拉取远程更新（工作区应无未提交修改）：

```sh
git pull --ff-only
```

修改完成并确认编译正常后，检查改动、提交并上传：

```sh
git status
git diff
git add .
git commit -m "更新章节内容和 PDF"
git push
```

提交说明应替换成这次修改的实际内容。保存文件不会自动上传，`git commit` 记录本地版本，`git push` 才会同步到 GitHub。
如果拉取或推送提示本地与远程分支分叉，先运行 `git fetch origin`，再用 `git log --oneline --graph --all` 查看双方提交，合并并解决冲突后再推送；不要直接强制推送。

换电脑时，克隆仓库即可继续维护：

```sh
git clone https://github.com/BUAA-CI-LAB/designflowdocs.git
cd designflowdocs
latexmk main.tex
```

推送需要使用具有该仓库写权限的 GitHub 账号完成 Git 身份验证。
`.gitattributes` 统一 Git 中的文本换行，并为 Shell 和 Windows 批处理脚本保留适合各自平台的换行格式。

## 可选验收

以下工具只使用 Python 标准库，**不参与 PDF 构建**：

```sh
python3 scripts/check_project.py --require-build
python3 scripts/check_project.py --baseline --require-build
```

第一条检查章节、图片、引用、代码语言和编译日志；第二条还核对 176 个代码块的迁移结果与修订记录、70 个原始资源的哈希和章节顺序。166 个代码块未经修改，10 个块的明确错误已经修正并记录前后内容。以后有意改写内容时，基线检查提示变化是正常情况。

迁移改动、验收边界及源稿中仍缺少的信息见 [迁移说明](migration/迁移说明.md)。
