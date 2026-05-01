import streamlit as st
import random
import plotly.graph_objects as go

# -----------------------------
# 1. 定積分の計算関数
# -----------------------------
def integral_linear(a, b, x1, x2):
    return (a/2)*(x2**2 - x1**2) + b*(x2 - x1)

def integral_quadratic(a, b, c, x1, x2):
    return (a/3)*(x2**3 - x1**3) + (b/2)*(x2**2 - x1**2) + c*(x2 - x1)

def integral_cubic(a, b, c, d, x1, x2):
    return (a/4)*(x2**4 - x1**4) + (b/3)*(x2**3 - x1**3) + (c/2)*(x2**2 - x1**2) + d*(x2 - x1)

# -----------------------------
# 2. 問題生成
# -----------------------------
def generate_problem(mode):
    lower = [-2, -1, 0]
    upper = [1, 2, 3, 4, 5]

    while True:
        x1 = random.choice(lower)
        x2 = random.choice(upper)

        if mode == "一次関数":
            a = random.randint(-5, 5)
            b = random.randint(-5, 5)
            if a == 0:
                continue
            val = integral_linear(a, b, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "x1": x1, "x2": x2, "answer": int(round(val))}

        elif mode == "二次関数":
            a = random.randint(-3, 3)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            if a == 0:
                continue
            val = integral_quadratic(a, b, c, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "c": c, "x1": x1, "x2": x2, "answer": int(round(val))}

        elif mode == "三次関数":
            a = random.randint(-2, 2)
            b = random.randint(-3, 3)
            c = random.randint(-5, 5)
            d = random.randint(-5, 5)
            if a == 0:
                continue
            val = integral_cubic(a, b, c, d, x1, x2)
            if abs(val - round(val)) < 1e-9:
                return {"a": a, "b": b, "c": c, "d": d, "x1": x1, "x2": x2, "answer": int(round(val))}

# -----------------------------
# 3. グラフ生成（Plotly）
# -----------------------------
def plot_function(mode, params):
    x1, x2 = params["x1"], params["x2"]
    xs = [x1 + (x2 - x1) * i / 200 for i in range(201)]

    if mode == "一次関数":
        a, b = params["a"], params["b"]
        ys = [a*x + b for x in xs]
        formula = f"{a}x + {b}"

    elif mode == "二次関数":
        a, b, c = params["a"], params["b"], params["c"]
        ys = [a*x**2 + b*x + c for x in xs]
        formula = f"{a}x^2 + {b}x + {c}"

    else:
        a, b, c, d = params["a"], params["b"], params["c"], params["d"]
        ys = [a*x**3 + b*x**2 + c*x + d for x in xs]
        formula = f"{a}x^3 + {b}x^2 + {c}x + {d}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)"))
    fig.add_vline(x=x1, line_width=2, line_dash="dash", line_color="green")
    fig.add_vline(x=x2, line_width=2, line_dash="dash", line_color="red")
    fig.update_layout(title=f"f(x) = {formula}", xaxis_title="x", yaxis_title="f(x)")
    return fig

# -----------------------------
# 4. Streamlit UI
# -----------------------------
st.title("定積分の自動問題生成アプリ（一次・二次・三次）")

mode = st.selectbox("関数の種類を選んでください", ["一次関数", "二次関数", "三次関数"])

if "problem" not in st.session_state or st.button("新しい問題を生成"):
    st.session_state.problem = generate_problem(mode)

params = st.session_state.problem
x1, x2 = params["x1"], params["x2"]

# 問題表示
st.subheader("【問題】")

if mode == "一次関数":
    st.latex(rf"\int_{{{x1}}}^{{{x2}}} ({params['a']}x + {params['b']})\,dx")

elif mode == "二次関数":
    st.latex(rf"\int_{{{x1}}}^{{{x2}}} ({params['a']}x^2 + {params['b']}x + {params['c']})\,dx")

else:
    st.latex(rf"\int_{{{x1}}}^{{{x2}}} ({params['a']}x^3 + {params['b']}x^2 + {params['c']}x + {params['d']})\,dx")

# 解答入力
user = st.number_input("答えを入力してください（整数）", step=1)

# 採点
if st.button("採点する"):
    if user == params["answer"]:
        st.success("正解です！")
    else:
        st.error(f"不正解です。正しい答えは {params['answer']} です。")

    # グラフ表示
    st.subheader("【グラフ】")
    st.plotly_chart(plot_function(mode, params), use_container_width=True)

    # 解説
    st.subheader("【解説】")
    if mode == "一次関数":
        st.latex(r"\int (ax+b)\,dx = \frac{a}{2}x^2 + bx")
    elif mode == "二次関数":
        st.latex(r"\int (ax^2+bx+c)\,dx = \frac{a}{3}x^3 + \frac{b}{2}x^2 + cx")
    else:
        st.latex(r"\int (ax^3+bx^2+cx+d)\,dx = \frac{a}{4}x^4 + \frac{b}{3}x^3 + \frac{c}{2}x^2 + dx")

    st.latex(rf"\text{{区間 }}[{x1},{x2}] \text{{ で評価すると }} {params['answer']}")
