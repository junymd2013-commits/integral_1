import streamlit as st
import random
import time
import plotly.graph_objects as go

# --------------------------------
# 係数整形（1省略、0非表示、符号調整）
# --------------------------------
def format_term(coeff, power):
    if coeff == 0:
        return ""
    sign = "+" if coeff > 0 else "-"
    c = abs(coeff)
    c_str = "" if c == 1 and power != 0 else str(c)
    if power == 0:
        term = f"{c}"
    elif power == 1:
        term = f"{c_str}x"
    else:
        term = f"{c_str}x^{power}"
    return f"{sign}{term}"

def format_polynomial(coeffs):
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        term = format_term(coeff, power)
        if term:
            terms.append(term)
    expr = "".join(terms)
    return expr[1:] if expr.startswith("+") else expr


# --------------------------------
# レベル別係数範囲
# --------------------------------
def get_coeff_range(level):
    if level == "初級":
        return (-2, 2)
    elif level == "中級":
        return (-5, 5)
    else:
        return (-10, 10)


# --------------------------------
# 定積分の計算
# --------------------------------
def integral_linear(a, b, x1, x2):
    return (a/2)*(x2**2 - x1**2) + b*(x2 - x1)

def integral_quadratic(a, b, c, x1, x2):
    return (a/3)*(x2**3 - x1**3) + (b/2)*(x2**2 - x1**2) + c*(x2 - x1)

def integral_cubic(a, b, c, d, x1, x2):
    return (a/4)*(x2**4 - x1**4) + (b/3)*(x2**3 - x1**3) + (c/2)*(x2**2 - x1**2) + d*(x2 - x1)


# --------------------------------
# 問題生成
# --------------------------------
def generate_problem(mode, level):
    lower = [-2, -1, 0]
    upper = [1, 2, 3, 4, 5]
    low, high = get_coeff_range(level)

    while True:
        x1 = random.choice(lower)
        x2 = random.choice(upper)

        if mode == "一次関数":
            a = random.randint(low, high)
            b = random.randint(low, high)
            if a == 0:
                continue
            val = integral_linear(a, b, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "x1": x1, "x2": x2, "answer": int(round(val))}

        elif mode == "二次関数":
            a = random.randint(low, high)
            b = random.randint(low, high)
            c = random.randint(low, high)
            if a == 0:
                continue
            val = integral_quadratic(a, b, c, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "c": c, "x1": x1, "x2": x2, "answer": int(round(val))}

        else:
            a = random.randint(low, high)
            b = random.randint(low, high)
            c = random.randint(low, high)
            d = random.randint(low, high)
            if a == 0:
                continue
            val = integral_cubic(a, b, c, d, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "c": c, "d": d, "x1": x1, "x2": x2, "answer": int(round(val))}


# --------------------------------
# グラフ（積分区間を塗る）
# --------------------------------
def plot_function_with_area(mode, params):
    x1, x2 = params["x1"], params["x2"]
    xs = [x1 + (x2 - x1) * i / 200 for i in range(201)]

    if mode == "一次関数":
        a, b = params["a"], params["b"]
        ys = [a*x + b for x in xs]
        expr = format_polynomial([a, b])

    elif mode == "二次関数":
        a, b, c = params["a"], params["b"], params["c"]
        ys = [a*x**2 + b*x + c for x in xs]
        expr = format_polynomial([a, b, c])

    else:
        a, b, c, d = params["a"], params["b"], params["c"], params["d"]
        ys = [a*x**3 + b*x**2 + c*x + d for x in xs]
        expr = format_polynomial([a, b, c, d])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)"))

    area_x = [x for x in xs if x1 <= x <= x2]
    start_idx = next(i for i, x in enumerate(xs) if x >= x1)
    end_idx = len(xs) - 1 - next(i for i, x in enumerate(reversed(xs)) if x <= x2)
    area_y = ys[start_idx:end_idx+1]

    fig.add_trace(go.Scatter(
        x=area_x,
        y=area_y,
        fill='tozeroy',
        mode='lines',
        line=dict(color='rgba(255,100,100,0.5)'),
        name="積分区間"
    ))

    fig.update_layout(
        title=f"f(x) = {expr}",
        xaxis_title="x",
        yaxis_title="f(x)"
    )

    return fig


# --------------------------------
# Streamlit UI
# --------------------------------
st.title("定積分の自動問題生成アプリ（一次・二次・三次）")

mode = st.selectbox("関数の種類を選んでください", ["一次関数", "二次関数", "三次関数"])
level = st.radio("問題のレベルを選んでください", ["初級", "中級", "上級"], horizontal=True)

# 初期化
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "correct" not in st.session_state:
    st.session_state.correct = 0
if "total" not in st.session_state:
    st.session_state.total = 0

if "answer_id" not in st.session_state:
    st.session_state.answer_id = 0

if "prev_mode" not in st.session_state:
    st.session_state.prev_mode = mode
if "prev_level" not in st.session_state:
    st.session_state.prev_level = level

# 問題更新
if (
    "problem" not in st.session_state
    or st.session_state.prev_mode != mode
    or st.session_state.prev_level != level
):
    st.session_state.problem = generate_problem(mode, level)
    st.session_state.prev_mode = mode
    st.session_state.prev_level = level
    st.session_state.answer_id += 1
    st.session_state.problem_start = time.time()

params = st.session_state.problem
x1, x2 = params["x1"], params["x2"]

# 問題表示
st.subheader("【問題】")

if mode == "一次関数":
    expr = format_polynomial([params["a"], params["b"]])
elif mode == "二次関数":
    expr = format_polynomial([params["a"], params["b"], params["c"]])
else:
    expr = format_polynomial([params["a"], params["b"], params["c"], params["d"]])

st.latex(rf"\int_{{{x1}}}^{{{x2}}} \left({expr}\right)\,dx")

# 解答欄（キーを動的に変更 → 毎回空欄）
user = st.text_input(
    "答えを入力してください（整数）",
    key=f"user_answer_{st.session_state.answer_id}",
    placeholder="ここに答えを入力"
)

# 採点
if st.button("採点する"):

    st.session_state.total += 1

    # 数値変換
    if user.isdigit() or (user.startswith("-") and user[1:].isdigit()):
        user_int = int(user)
    else:
        user_int = None

    if user_int == params["answer"]:
        st.success("正解です！")
        st.session_state.correct += 1
    else:
        st.error(f"不正解です。正しい答えは {params['answer']} です。")

    # 時間計測
    elapsed = time.time() - st.session_state.problem_start
    st.write(f"この問題にかかった時間：{elapsed:.1f} 秒")

    # グラフ
    st.subheader("【グラフ】")
    st.plotly_chart(plot_function_with_area(mode, params), use_container_width=True)

    # 正答率
    accuracy = st.session_state.correct / st.session_state.total * 100
    st.write(f"正答率：{accuracy:.1f}%")

    # 次の問題へ
    st.session_state.problem = generate_problem(mode, level)
    st.session_state.problem_start = time.time()
    st.session_state.answer_id += 1  # ★ 解答欄を空欄にする（キー更新）

# ★ 次の問題へ進むボタン
if st.button("次の問題へ"):
    st.session_state.problem = generate_problem(mode, level)
    st.session_state.problem_start = time.time()
    st.session_state.answer_id += 1  # 解答欄を空欄にする

# アプリ全体の経過時間
total_elapsed = time.time() - st.session_state.start_time
st.write(f"アプリ起動からの経過時間：{total_elapsed:.1f} 秒")
