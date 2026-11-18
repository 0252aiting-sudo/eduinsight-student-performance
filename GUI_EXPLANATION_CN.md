# EduInsight PyWebView GUI 代码说明（教师讲解版）

> **改版范围说明：** 本次只替换图形使用者界面（GUI）。`analyzer.py`、`student.py`、`ai_comment.py`、`report.py`、`main.py` 与 `student-mat.csv` 的业务分析逻辑没有更改。新界面仍然调用原有的 `PerformanceAnalyzer`、`OllamaAI` 和 `ReportGenerator`。

---

## 1. 整体架构：Python 与网页界面如何合作

新版不是普通浏览器网站，也不需要启动 Flask/Django 服务器。它是一个本机桌面程式：

```text
使用者
  ↓ 点击网页按钮
web/index.html + web/app.js      ← 前端：画面、按钮、表格、图表
  ↓ window.pywebview.api.方法名(...)
PyWebView JavaScript Bridge
  ↓ 调用 Python 类的方法
 gui.py / EduInsightAPI           ← 后端桥梁：读取资料、调用原有系统
  ↓
analyzer.py / ai_comment.py / report.py / student-mat.csv
```

- **PyWebView**：建立原生桌面窗口，并提供 Python 与 JavaScript 的安全沟通桥梁。
- **HTML**：定义页面的结构，例如侧边栏、标题、表格容器。
- **CSS**：定义专业简约风格、颜色、间距、卡片与响应式布局。
- **JavaScript**：处理按钮事件、切换页面、向 Python 请求数据、将数据绘制到页面。
- **Python**：保留数据处理责任；网页不直接读取 CSV，也不直接分析成绩。

---

# 2. `gui.py`：Python 程式入口与 API Bridge

`gui.py` 是新版 GUI 的唯一 Python 界面文件。它替代旧版 CustomTkinter 的所有 `CTkFrame`、`CTkButton`、`CTkTextbox` 等画面元件。

## 2.1 引入模块

```python
from pathlib import Path
import os
import pandas as pd
import webview

from analyzer import PerformanceAnalyzer
from ai_comment import OllamaAI
from report import ReportGenerator
```

| 代码 | 作用 |
|---|---|
| `Path` | 处理文件路径，避免 Windows/macOS/Linux 路径写法不同的问题。 |
| `os` | 生成报告时暂时切换工作目录。 |
| `pandas as pd` | 读取 `student-mat.csv` 文件，产生 DataFrame。 |
| `webview` | PyWebView 套件；建立桌面窗口及 Python–JavaScript bridge。 |
| `PerformanceAnalyzer` | 原有代码，计算平均成绩、及格数、失败数和影响因素。 |
| `OllamaAI` | 原有代码，生成 AI 评论；未启动 Ollama 时自动使用规则式评论。 |
| `ReportGenerator` | 原有代码，生成文字报告。 |

```python
BASE_DIR = Path(__file__).resolve().parent
```

这行会取得 `gui.py` 所在的项目目录。例如：

```text
C:\...\asss
```

因此无论使用者从哪个终端路径启动程式，程式都能正确找到：

```text
student-mat.csv
web/index.html
Student_Report.txt
```

## 2.2 `EduInsightAPI` 类

```python
class EduInsightAPI:
```

这是**前端可以调用的 Python 方法集合**。在 `webview.create_window(..., js_api=api)` 中传入实例后，JavaScript 可通过：

```javascript
window.pywebview.api.get_dashboard()
```

调用 Python 的：

```python
def get_dashboard(self):
```

这就是 PyWebView 的核心桥梁。

### 初始化：`__init__`

```python
def __init__(self):
    self.data = pd.read_csv(BASE_DIR / "student-mat.csv", sep=";")
    self.analyzer = PerformanceAnalyzer(self.data)
    self.ai = OllamaAI()
    self.report = ReportGenerator(self.data)
```

| 行为 | 说明 |
|---|---|
| `pd.read_csv(..., sep=";")` | 读取原有学生成绩 CSV。此数据集以分号，而非逗号分隔。 |
| `self.data` | 存放所有 395 名学生的 DataFrame。 |
| `PerformanceAnalyzer(self.data)` | 使用原来的分析类，不复制、不改写其统计规则。 |
| `OllamaAI()` | 使用原来的 AI / fallback 评论功能。 |
| `ReportGenerator(self.data)` | 使用原来的报告生成功能。 |

### `_clean(value)`：资料格式转换

```python
@staticmethod
def _clean(value):
    if hasattr(value, "item"):
        return value.item()
    return value
```

Pandas 有时会传回 `numpy.int64` 等类型，JavaScript 的 JSON 不一定能直接处理。`value.item()` 会把它转成普通 Python `int` / `float`，确保能安全传给网页。

`@staticmethod` 表示它不需要使用 `self` 中的数据；它只是一个工具函数。

### `get_dashboard()`：Dashboard 数据

```python
def get_dashboard(self):
    passed = self.analyzer.pass_students()
    total = len(self.data)
    grades = [int(x) for x in self.data["G3"].tolist()]
    study = self.data.groupby("studytime")["G3"].mean()
```

此方法为 Dashboard 汇集所有数字：

- `passed`：调用原有 `pass_students()`；成绩 `G3 >= 10` 为及格。
- `total`：DataFrame 的资料行数，即总学生人数。
- `grades`：所有学生最终成绩，用于前端绘制成绩分布柱状图。
- `groupby("studytime")["G3"].mean()`：按照每周学习时间等级分组，计算每组平均最终成绩。

最后 `return {...}` 会回传一个**只包含 JSON 可传输数据的字典**：

```python
{
  "total": 395,
  "average": 10.42,
  "passed": 265,
  "grades": [...],
  "study_time": {"1": 9.1, "2": 10.2, ...}
}
```

前端获得这个对象后，才负责把数字显示成卡片和图表。**统计计算仍在 Python 进行。**

### `get_student(student_id)`：按 ID 搜索学生

这个方法对应旧 CTk 的 `search_student()`。

第一段是输入检查：

```python
try:
    student_id = int(student_id)
except (TypeError, ValueError):
    return {"ok": False, "message": "Please enter a valid numeric Student ID."}
```

前端传来的 ID 可能是空白或文字，故先转换为整数；失败时不让程式崩溃，而是回传错误讯息。

```python
if not 1 <= student_id <= len(self.data):
    return {"ok": False, "message": f"Student ID must be between 1 and {len(self.data)}."}
row = self.data.iloc[student_id - 1]
```

- 使用者输入 ID 是从 1 开始。
- Pandas 行号是从 0 开始。
- 因此需要 `student_id - 1`。

接下来完全调用原有逻辑：

```python
factors = self.analyzer.analyze_performance_factors(row)
comment = self.ai.generate_performance_analysis(student_data, factors)
```

- `factors`：保留原本的 Failures 38%、Study Time 27%、Absences 22%、Health 13% 分析与建议。
- `comment`：保留原本 Ollama 调用；Ollama 未运行则使用 `_fallback_analysis()`。

最后将学生资料、因素列表和评论组织为字典回传。`"ok": True` 是前端判断本次搜寻是否成功的标志。

### `find_by_grade(grade)` 与 `get_scholarship_students()`

这两项把原本 `main.py` 的命令列功能也做成 UI：

```python
result = self.data[self.data["G3"] == grade]
```

依最终成绩筛选学生。

```python
self.data[self.data["G3"] >= 18]
```

筛选原本定义的奖学金资格学生。这里的门槛没有改变，仍是 `G3 >= 18`。

### `_student_rows(frame)`

```python
def _student_rows(self, frame):
```

这是表格资料的共用格式化工具。它将 DataFrame 转换为前端表格需要的简短资料：ID、学校、性别、年龄和最终成绩。

```python
"id": int(index + 1)
```

再次把 Pandas 的 0-based index 转成使用者看得懂的 1-based ID。

### `get_top_students()`

```python
return self._student_rows(self.data.sort_values("G3", ascending=False).head(10))
```

- `sort_values(..., ascending=False)`：由高至低排序成绩。
- `.head(10)`：取得前十名。
- `_student_rows(...)`：转换成可显示在网页表格的资料。

### `generate_report()`：生成原有报告

```python
old_cwd = os.getcwd()
try:
    os.chdir(BASE_DIR)
    self.report.generate_report()
    content = (BASE_DIR / "Student_Report.txt").read_text(encoding="utf-8")
```

`ReportGenerator` 原来的程式以相对路径写入 `Student_Report.txt`。因此 GUI 暂时把当前目录切换至项目资料夹，确保报告保存在正确位置。随后读取报告内容回传给前端显示和下载。

```python
finally:
    os.chdir(old_cwd)
```

无论成功或出错，都恢复原本的工作目录。这是安全清理做法。

### `get_app_info()`

```python
return {"dataset": "student-mat.csv", "students": len(self.data), "ollama": self.ai.check_ollama_running()}
```

传回顶部状态列所需的资料：数据集名称、学生数，以及 Ollama 是否连接成功。

### `close_app()`：退出应用程序

```python
def close_app(self):
    if webview.windows:
        webview.windows[0].destroy()
```

此方法供侧边栏底部的 **Exit application** 按钮调用。JavaScript 通过 `window.pywebview.api.close_app()` 请求 Python 关闭第一个原生 PyWebView 窗口；`destroy()` 会结束 GUI。它只负责退出界面，不会改动 CSV、分析数据或报告逻辑。

## 2.3 `run()`：创建桌面窗口

```python
def run():
    api = EduInsightAPI()
    window = webview.create_window(
        "EduInsight | Student Analytics",
        (BASE_DIR / "web" / "index.html").as_uri(),
        js_api=api,
        width=1440,
        height=900,
        min_size=(1120, 680),
        background_color="#F8F9FA",
    )
    webview.start(debug=False)
```

| 参数 | 说明 |
|---|---|
| `api = EduInsightAPI()` | 建立负责数据和原有系统调用的对象。 |
| 第一个参数 | Windows 标题栏显示的应用标题。 |
| `index.html` URI | 告诉 PyWebView 加载本机的 HTML 文件，不需网络或服务器。`as_uri()` 可安全处理 Windows 路径。 |
| `js_api=api` | 把 Python API 暴露给 JavaScript。 |
| `width` / `height` | 初始窗口大小。 |
| `min_size` | 防止缩放得太小导致页面难以使用。 |
| `background_color` | 网页尚未加载完成时的背景色，匹配设计主题。 |
| `webview.start()` | 开启 GUI 事件循环；等同旧版 CTk 的 `mainloop()`。 |

```python
if __name__ == "__main__":
    run()
```

只有直接执行 `python gui.py` 时才启动窗口；若其他程式 import `gui.py`，不会自动打开 GUI。这是 Python 标准写法。

---

# 3. `web/index.html`：页面骨架

HTML 不包含大量业务资料；它只提供固定的页面结构和 JavaScript/CSS 文件入口。

```html
<aside class="sidebar"> ... </aside>
<main class="main"> ... <section id="page">...</section> </main>
```

- `<aside>`：深色左边栏。
- `<main>`：右侧主内容区。
- `<section id="page">`：动态内容容器。JavaScript 会依使用者点击的 Dashboard、Search、Analytics 或 Reports，把不同 HTML 放入此区域。

## 3.1 导航按钮

```html
<button class="nav active" data-page="dashboard">...</button>
<button class="nav" data-page="students">...</button>
```

`data-page` 是给 JavaScript 使用的自订资料属性：

- `dashboard` → `renderDashboard()`
- `students` → `renderStudents()`
- `analytics` → `renderAnalytics()`
- `reports` → `renderReports()`

`active` 类别代表目前被选中的按钮；CSS 会让它变成蓝色。

## 3.2 动态文字位置

```html
<div id="crumb">OVERVIEW</div>
<h1 id="page-title">Dashboard</h1>
<div id="dataset-label">Loading dataset…</div>
```

这些 `id` 让 JavaScript 能准确找到并更新文字。比如数据加载后，`dataset-label` 会显示：

```text
student-mat.csv · 395 students
```

## 3.3 资源载入顺序

```html
<link rel="stylesheet" href="styles.css">
<script src="app.js"></script>
```

- CSS 在 `<head>` 先加载，避免页面短暂出现没有样式的状态。
- JavaScript 在 `<body>` 最后加载，这样它执行时 HTML 元素已经存在。

---

# 4. `web/styles.css`：专业简约视觉系统

## 4.1 主题颜色变量

```css
:root {
  --primary: #4285F4;
  --hover: #1A73E8;
  --sidebar: #202124;
  --bg: #F8F9FA;
  --card: #fff;
}
```

`:root` 代表全页面根层。用 CSS variable 的优点是：主题统一、日后改色只需改一处。

| CSS 变量 | 用处 |
|---|---|
| `--primary` | 主按钮、重点数字、进度条、图表。 |
| `--hover` | 鼠标停在主按钮或柱状图上时的深蓝色。 |
| `--sidebar` | 左方导航深色背景。 |
| `--bg` | 主内容浅灰背景。 |
| `--card` | 白色数据卡片与面板背景。 |
| `--line` | 卡片、表格和页面的低对比度分隔线。 |
| `--muted` | 次要说明文字。 |
| `--green` / `--red` | 及格和不及格等状态提示。 |

## 4.2 基础重设

```css
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); ... }
```

- `box-sizing: border-box`：元素宽高包含 padding/border，布局计算较稳定。
- `margin: 0`：去除浏览器默认白边。

## 4.3 固定侧边栏

```css
.sidebar {
  width: 250px;
  height: 100vh;
  position: fixed;
  display: flex;
  flex-direction: column;
}
.main { margin-left: 250px; }
```

- `100vh`：侧边栏高度等于窗口高度。
- `position: fixed`：滚动主内容时侧边栏保持不动。
- `.main` 留出 250px 左边距，避免被侧边栏遮挡。

## 4.4 卡片与统计网格

```css
.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 17px;
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
}
```

CSS Grid 让四张 KPI 卡片自动等宽排列。`minmax(160px, 1fr)` 代表每一格最小 160px，剩余空间平均分配。卡片使用白底、细边线、圆角和非常轻的阴影，符合专业简约风格。

## 4.5 图表样式

```css
.bar-chart { display: flex; align-items: end; }
.bar { background: var(--primary); }
.bar:hover { background: var(--hover); }
```

柱形图并没有使用额外的 JavaScript 图表套件，而是用普通 `<div>` 柱加 CSS Flexbox 建立：

- `align-items: end` 让所有柱从底部对齐；
- JavaScript 计算每个柱的百分比高度；
- hover 时从主蓝色变成指定的深蓝色。

圆环图使用：

```css
background: conic-gradient(...)
```

以 CSS 的圆锥渐变画出通过/失败比例；中间以 `::after` 伪元素画白色圆形，形成 donut chart。

## 4.6 Hover 与图表动画

新版在 Dashboard 与 Analytics 的卡片使用较缓慢的 transition：

```css
.card:hover {
  transform: scale(1.015);
  background: #f6f9fe;
  transition: transform .38s ease, background-color .38s ease;
}
```

因此鼠标停留在小卡片时，卡片会轻微放大、背景稍微加深，而不是突然跳动。Top Performing Students 的表格行也使用相同的 `.38s` 缓动；鼠标停在某位学生时，该行会变浅蓝并轻微放大。

成绩柱状图使用 `@keyframes bar-rise` 由底部缓慢长出，JavaScript 同时由 `0` 递增至实际人数。通过率圆环则由 JavaScript 的 `requestAnimationFrame` 从 `0%` 逐帧绘制到真实通过率，中央百分比也会同步递增。动画只影响呈现方式，真实统计数据仍来自 Python。

## 4.7 响应式设计

```css
@media(max-width:950px) { ... }
```

当窗口宽度小于 950px：

- 侧边栏由 250px 缩至 70px；
- 品牌文字、菜单文字隐藏，保留图示；
- 四张统计卡变成两列；
- 双栏内容变成单栏。

因此即使用户缩小桌面窗口，界面也不会严重挤压。

---

# 5. `web/app.js`：交互、数据传输与动态页面

这是前端的主要控制器。

## 5.1 常用工具与全局状态

```javascript
const $ = s => document.querySelector(s);
const page = $('#page');
let dashboard = null;
let currentReport = '';
```

| 代码 | 说明 |
|---|---|
| `$` | `document.querySelector` 的简写，例如 `$('#page')` 找到 id 为 page 的元素。 |
| `page` | 主内容区域，所有动态页面都会放进去。 |
| `dashboard` | 暂存 Dashboard 数据，进入 Analytics 时可复用，减少 Python 调用。 |
| `currentReport` | 暂存最新生成的报告文字，供下载功能使用。 |

```javascript
const headings = { dashboard: ['OVERVIEW', 'Dashboard'], ... };
```

此对象定义每个页面的上方小标题（breadcrumb）和主标题，导航切换时统一更新。

## 5.2 防止 HTML 注入：`esc()`

```javascript
function esc(s) {
  return String(s).replace(/[&<>'"]/g, ...);
}
```

这会把 `<`、`>`、`&` 等特殊字符转义。例如学生评论里若有 `<script>`，也只会显示为文字，不能被浏览器当作代码执行。虽然本系统资料来自本机 CSV，此做法仍是良好的安全习惯。

## 5.3 Toast 提示：`toast()`

```javascript
function toast(text) {
  const t = $('#toast');
  t.textContent = text;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2600);
}
```

生成报告成功后，右下角出现短暂提示。`setTimeout` 在 2.6 秒后移除 `show` 类别，CSS 的透明度 transition 让提示淡出。

## 5.4 可复用 UI 建立函数

### `stat()`

```javascript
function stat(label, value, foot='', color='blue') { ... }
```

负责产生一张 Dashboard KPI 卡片。避免对「总学生数、平均成绩、通过率」重复写相同 HTML。

### `bars(values)`

```javascript
const max = Math.max(...values, 1);
height: ${Math.max(4, v / max * 100)}%
```

- 找出最高频率 `max`；
- 每一个成绩的学生人数 `v` 除以最大值，得到相对高度百分比；
- `Math.max(4, ...)` 让数量非常小的项目仍可看见至少 4% 的柱子。

### `lineChart(points)`

`points` 是例如：

```javascript
{"1": 9.1, "2": 10.2, "3": 11.5, "4": 12.7}
```

该函数自行生成 SVG `<polyline>` 路径与 `<circle>` 数据点，画出学习时间与平均成绩的趋势线。优点是无需安装 Chart.js 等额外依赖，应用更轻量。

### `table(rows)`

将 Python 回传的学生列表产生统一的 HTML table。若 `rows` 是空数组，则显示“No students match this search.”，不会产生空白表格。

---

## 5.5 `renderDashboard()`：主页

```javascript
async function renderDashboard() {
  dashboard = await window.pywebview.api.get_dashboard();
```

重点：

- `window.pywebview.api` 是 PyWebView 注入的 Python API；
- `get_dashboard()` 实际执行的是 `gui.py` 中同名 Python 方法；
- `await` 是因为 Python 调用需要时间，JavaScript 等待其回传再画页面；
- 回传资料存到 `dashboard`。

```javascript
page.innerHTML = `...`;
```

把 KPI 卡、成绩柱状图、及格/失败圆环图和学习时间线图放进主内容区。这里**仅做显示**，没有改变或重新定义 Python 成绩统计规则。

## 5.6 `renderStudents()`、`bindSearchTabs()`：学生搜索页面

`renderStudents()` 创建：

1. Student ID 输入框；
2. Search button；
3. 三个 tabs：By Student ID、By Final Grade、Scholarship eligible；
4. 空的结果区域 `#search-results`。

`bindSearchTabs()` 负责各 tab 点击后的状态变化：

- ID tab：显示 ID 输入框并绑定 `searchId()`；
- Grade tab：显示成绩输入框并绑定 `searchGrade()`；
- Scholarship tab：隐藏不需要的搜索输入栏，立即调用 Python `get_scholarship_students()`，然后直接显示奖学金资格学生表格。

```javascript
b.classList.add('active');
```

这会让目前 tab 获得蓝色文字与底线；其他 tab 移除 active 状态。

## 5.7 `searchId()`：完整学生资料与 AI 评论

```javascript
const x = await window.pywebview.api.get_student(id);
```

将输入 ID 传给 Python。返回数据结构示例：

```javascript
{
  ok: true,
  student: {...},
  factors: [...],
  comment: "Performance Level: ..."
}
```

若 `ok` 为 `false`：

```javascript
r.innerHTML = `<div class="empty">${esc(x.message)}</div>`;
```

显示 Python 回传的验证错误，例如 ID 超出范围。

若成功，页面分两栏：

- 左栏：Student ID、学校、性别、年龄、失败次数、学习时间、缺席与健康；
- 右栏：原有四项因素及其重要性进度条；
- 下方：原有 AI / fallback 生成的 Performance Comment。

因素进度条的宽度由原有 importance 值决定：

```javascript
style="width:${f.importance}%"
```

所以 38% 的 Failures 显示为最长、13% 的 Health 显示为最短；这只是图形化表达原本的数值，没有改变权重。

## 5.8 `searchGrade()`：按成绩筛选

```javascript
const x = await window.pywebview.api.find_by_grade($('#grade').value);
```

把成绩输入传给 Python，Python 根据 `G3 == grade` 筛选，前端用共用 `table(x.students)` 显示。

## 5.9 `renderAnalytics()`：分析页

```javascript
const d = dashboard || await window.pywebview.api.get_dashboard();
const top = await window.pywebview.api.get_top_students();
```

逻辑是：若 Dashboard 数据仍存在则直接使用，否则再请求 Python；Top 10 则调用 Python 排序功能。之后画出：

- 最高、最低、及格、失败 KPI；
- 成绩分布；
- 学习时间趋势；
- Top 10 表格。

## 5.10 `renderReports()`、`makeReport()`、`downloadReport()`：报告页

```javascript
const r = await window.pywebview.api.generate_report();
```

这会运行原有的 `ReportGenerator.generate_report()`，产生项目目录内的：

```text
Student_Report.txt
```

回传的 `r.content` 显示在深色等宽字体区域，方便预览。

下载功能：

```javascript
new Blob([currentReport], {type: 'text/plain'})
```

`Blob` 是浏览器内存中的文字档案。`<a>` 标签配合 `download='Student_Report.txt'`，让用户再选择保存一份报告到自己指定的下载位置。

因此报告有两份可能位置：

1. Python 原始逻辑保存的项目文件夹内 `Student_Report.txt`；
2. 用户点击 Download 后保存的位置。

## 5.11 `navigate(name)`：统一页面切换

```javascript
async function navigate(name) {
  const [crumb, title] = headings[name];
  ...
  if (name === 'dashboard') await renderDashboard();
  if (name === 'students') renderStudents();
  if (name === 'analytics') await renderAnalytics();
  if (name === 'reports') renderReports();
}
```

这是整个单页桌面界面的导航中心。它：

1. 更新页面标题；
2. 更新侧边栏 active 按钮；
3. 先显示 Loading；
4. 根据页面名称调用相应的 render function。

## 5.12 `pywebviewready`：正确启动时机

```javascript
window.addEventListener('pywebviewready', async () => { ... });
```

PyWebView 必须先把 Python API 建立完成，前端才可以使用：

```javascript
window.pywebview.api
```

因此所有第一次读取数据和注册导航逻辑，都放在 `pywebviewready` 事件后执行。启动后依序发生：

1. Python 创建窗口并载入 HTML；
2. PyWebView bridge 准备完成，触发 `pywebviewready`；
3. JavaScript 取得 `get_app_info()`；
4. 显示数据集名称与 Ollama 状态；
5. 绑定侧边栏 click 事件；
6. 自动打开 Dashboard。

---

# 6. 可向老师总结的重点

你可以这样说明：

> 我把原本用 CustomTkinter 编写的桌面 UI 改为 PyWebView。PyWebView 让 Python 创建原生应用窗口，同时在窗口内使用 HTML、CSS 和 JavaScript 实现更现代化、容易维护的界面。Python 仍负责 CSV 读取、成绩统计、AI 评论和文字报告；JavaScript 只负责收集用户输入、调用 PyWebView API，并把 Python 回传的数据呈现为卡片、表格和轻量图表。因此系统的业务规则，例如及格门槛 G3 ≥ 10、优秀/奖学金门槛 G3 ≥ 18、四项表现因素的重要性，全部保持不变。

## 功能对照

| 原 CustomTkinter 功能 | PyWebView 新位置 | 原业务逻辑是否改变 |
|---|---|---|
| Dashboard | Dashboard 页面 KPI 与图表 | 否 |
| Search Student by ID | Student Search → By Student ID | 否 |
| Performance Factors | 搜索结果右栏及进度条 | 否 |
| AI Performance Comment | 搜索结果下方 Comment | 否 |
| Pass vs Fail / Histogram / Study Time | Analytics / Dashboard 图表 | 否，只有图表渲染技术改变 |
| Generate Report | Reports 页面 | 否 |
| Open/Download Report | Reports 预览与 Download | 原报告内容不变，新增前端下载便利性 |
| Exit button | 侧边栏底部的 **Exit application** 按钮 | 否；按钮通过 PyWebView 调用 `close_app()` 关闭原生窗口，不影响分析系统 |

---

# 7. 运行所需文件与依赖

```powershell
python -m pip install -r requirements.txt
python gui.py
```

`requirements.txt` 的作用是列出运行所需 Python 套件：

```text
pandas>=2.0     # 读取和处理 CSV
requests>=2.31  # 原有 Ollama API 请求
pywebview>=5.0  # 新版桌面 GUI
```

**注意：** import 名称是 `webview`，但 pip 安装包名称是 `pywebview`，因此安装指令是 `pip install pywebview`。
