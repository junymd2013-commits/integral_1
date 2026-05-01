import streamlit as st
import random
import plotly.graph_objects as go

# --------------------------------
# 係数整形（1省略、0非表示、符号調整）
# --------------------------------
def format_term(coeff, power):
    if coeff == 0:
        return ""

    sign = "+" if coeff > 0 else "-"
    c = abs(coeff)

    if c == 1 and power != 0:
        c_str = ""
    else:
        c_str = str(c)

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
    if expr.startswith("+"):
        expr = expr[1:]
    return expr


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

        else:  # 三次関数
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

    # 積分区間の塗りつぶし
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

# モード or レベル変更時に必ず新しい問題を生成
if "prev_mode" not in st.session_state:
    st.session_state.prev_mode = mode
if "prev_level" not in st.session_state:
    st.session_state.prev_level = level

if (
    "problem" not in st.session_state
    or st.session_state.prev_mode != mode
    or st.session_state.prev_level != level
    or st.button("新しい問題を生成")
):
    st.session_state.problem = generate_problem(mode, level)
    st.session_state.prev_mode = mode
    st.session_state.prev_level = level

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

# 解答入力
user = st.number_input("答えを入力してください（整数）", step=1)

# 採点
if st.button("採点する"):
    if user == params["answer"]:
        st.success("正解です！")
    else:
        st.error(f"不正解です。正しい答えは {params['answer']} です。")

    # グラフ
    st.subheader("【グラフ】")
    st.plotly_chart(plot_function_with_area(mode, params), use_container_width=True)

    # ヒント
    st.subheader("【ヒント】")

    if level == "初級":
        st.latex(r"\int (ax+b)\,dx = \frac{a}{2}x^2 + bx")
        st.latex(r"\int (ax^2+bx+c)\,dx = \frac{a}{3}x^3 + \frac{b}{2}x^2 + cx")
        st.latex(r"\int (ax^3+bx^2+cx+d)\,dx = \frac{a}{4}x^4 + \frac{b}{3}x^3 + \frac{c}{2}x^2 + dx")
    elif level == "中級":
        st.write("不定積分を求めてから、上端と下端を代入して差をとります。")
    else:
        st.write("グラフの面積として考えると理解しやすいです。区間 [x_1, x_2] の符号に注意してください。")

    # 解説
    st.subheader("【解説】")
    st.write(f"区間 [{x1}, {x2}] で評価すると {params['answer']} になります。")
