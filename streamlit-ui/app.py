import streamlit as st
import requests
import time
import matplotlib.pyplot as plt
import networkx as nx
from math import pow
import plotly.graph_objects as go

API_URL = "http://api:8000/api"

st.set_page_config(page_title="Math API UI", page_icon="🧠", layout="wide")

import plotly.graph_objects as go

def render_power_plot(base: int, exponent: int):
    max_x = max(exponent, 20)
    x_vals = list(range(0, max_x + 1))
    y_vals = [pow(base, i) for i in x_vals]

    frames = [
        go.Frame(
            data=[
                go.Scatter(
                    x=x_vals[:k + 1],
                    y=y_vals[:k + 1],
                    mode="lines+markers",
                    line=dict(color="#2ecc71", width=4),
                    marker=dict(size=8)
                )
            ],
            name=f"frame{k}"
        )
        for k in range(len(x_vals))
    ]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[x_vals[0]],
                y=[y_vals[0]],
                mode="lines+markers",
                fill='tozeroy',
                line=dict(color="#2ecc71", width=4),
                marker=dict(size=8)
            )
        ],
        layout=go.Layout(
            title=dict(
                text=f"📈 Power Function: y = {base}^x",
                font=dict(size=22),
                x=0.5
            ),
            xaxis=dict(
                title="x",
                tickfont=dict(size=14),
                showline=True,
                linewidth=1,
                linecolor="rgba(255,255,255,0.3)",
                ticks="outside",
                ticklen=6,
                tickcolor="rgba(255,255,255,0.2)",
                gridcolor="rgba(255,255,255,0.05)",
                showspikes=True,
                spikemode="across",
                spikesnap="cursor",
                spikethickness=1,
                spikecolor="green"
            ),
            yaxis=dict(
                title="y",
                tickfont=dict(size=14),
                showline=True,
                linewidth=1,
                linecolor="rgba(255,255,255,0.3)",
                ticks="outside",
                ticklen=6,
                tickcolor="rgba(255,255,255,0.2)",
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False,
                hoverformat=".4s",
                tickformat=".3s"
            ),
            height=600,
            margin=dict(l=60, r=40, t=60, b=100),
            template="plotly_dark",
            updatemenus=[
                {
                    "type": "buttons",
                    "direction": "right",
                    "x": 0.5,
                    "xanchor": "center",
                    "y": -0.3,
                    "yanchor": "top",
                    "buttons": [
                        {
                            "label": "▶ Play",
                            "method": "animate",
                            "args": [None, {
                                "frame": {"duration": 300, "redraw": True},
                                "fromcurrent": True
                            }]
                        },
                        {
                            "label": "⏹ Pause",
                            "method": "animate",
                            "args": [[None], {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": False},
                                "transition": {"duration": 0}
                            }]
                        }
                    ]
                }
            ]
        ),
        frames=frames
    )

    st.plotly_chart(fig, use_container_width=True)

def render_fibonacci_graph(n: int):
    if n > 7:
        st.warning("Visualization limited to n ≤ 7.")
        return

    st.subheader(f"🌿 Recursive Fibonacci Visualization: Fib({n})")

    nodes = []
    edges = []
    steps = []

    def add_node(n, depth=0, x=0.0, spread=1.0, parent=None):
        node_id = f"{n}_{len(nodes)}"
        node = {"id": node_id, "label": f"Fib({n})", "x": x, "y": -depth, "parent": parent}
        nodes.append(node)
        steps.append((node, parent))
        if parent:
            edges.append((parent, node_id))
        if n > 1:
            add_node(n - 1, depth + 1, x - spread, spread / 2, node_id)
            add_node(n - 2, depth + 1, x + spread, spread / 2, node_id)

    add_node(n)

    # Axis range is calculated once
    x_vals = [n["x"] for n in nodes]
    y_vals = [n["y"] for n in nodes]
    x_range = [min(x_vals) - 1, max(x_vals) + 1]
    y_range = [min(y_vals) - 1, max(y_vals) + 1]

    placeholder = st.empty()
    seen_nodes = []
    seen_edges = []

    for idx, (node, parent) in enumerate(steps):
        seen_nodes.append(node)
        if parent:
            seen_edges.append((parent, node["id"]))

        fig = go.Figure()

        # Draw edges
        for src_id, tgt_id in seen_edges:
            src = next(n for n in seen_nodes if n["id"] == src_id)
            tgt = next(n for n in seen_nodes if n["id"] == tgt_id)
            fig.add_trace(go.Scatter(
                x=[src["x"], tgt["x"]],
                y=[src["y"], tgt["y"]],
                mode="lines",
                line=dict(color="rgba(160,160,160,0.3)", width=1),
                hoverinfo="skip",
                showlegend=False
            ))

        # Draw nodes
        fig.add_trace(go.Scatter(
            x=[n["x"] for n in seen_nodes[:-1]],
            y=[n["y"] for n in seen_nodes[:-1]],
            text=[n["label"] for n in seen_nodes[:-1]],
            textposition="bottom center",
            mode="markers+text",
            marker=dict(size=18, color="#5dade2", line=dict(width=1, color="white")),
            hoverinfo="text",
            showlegend=False,
            opacity=0.8
        ))

        # Highlight the current node
        fig.add_trace(go.Scatter(
            x=[node["x"]],
            y=[node["y"]],
            text=[node["label"]],
            textposition="bottom center",
            mode="markers+text",
            marker=dict(size=22, color="#e74c3c", line=dict(width=2, color="white")),
            hoverinfo="text",
            showlegend=False,
            opacity=1.0
        ))

        # Freeze axis and layout
        fig.update_layout(
            height=600,
            xaxis=dict(visible=False, range=x_range),
            yaxis=dict(visible=False, range=y_range),
            margin=dict(l=10, r=10, t=40, b=20),
            template="plotly_dark",
            title=f"Fibonacci Recursive Tree: Fib({n})",
            annotations=[dict(
                text=f"🧠 Step {idx+1}/{len(steps)}",
                xref="paper", yref="paper",
                x=0.99, y=1.05, showarrow=False,
                font=dict(size=12, color="gray"),
                xanchor="right"
            )]
        )

        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.4)

    st.success("🎉 Animation complete.")

def render_factorial_chain(n: int):
    if n > 20:
        st.warning("Visualization limited to n ≤ 20.")
        return

    # Build values and labels
    values = [1]
    labels = ["1"]
    multipliers = []
    for i in range(1, n + 1):
        result = values[-1] * i
        values.append(result)
        labels.append(str(result))
        multipliers.append(f"×{i}")

    # Coordinates for vertical chain
    x = [0] * len(labels)
    y = list(reversed(range(len(labels))))

    # Create node trace
    node_trace = go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        text=labels,
        textposition="middle center",
        marker=dict(
            size=40,
            color="#58D68D",
            line=dict(color="white", width=2)
        ),
        hoverinfo="text",
        showlegend=False
    )

    # Create edge traces with annotations
    edge_traces = []
    annotations = []
    for i in range(len(labels) - 1):
        edge_traces.append(go.Scatter(
            x=[x[i], x[i+1]],
            y=[y[i], y[i+1]],
            mode="lines",
            line=dict(color="rgba(200,200,200,0.3)", width=2),
            hoverinfo="none",
            showlegend=False
        ))
        annotations.append(dict(
            x=x[i],
            y=(y[i] + y[i+1]) / 2,
            text=multipliers[i],
            showarrow=False,
            font=dict(size=14),
            xanchor="right",
            yanchor="middle",
            opacity=0.7
        ))

    # Build figure
    fig = go.Figure(data=[*edge_traces, node_trace])
    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=30, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=annotations,
        template="plotly_dark",
        title=f"🧮 Factorial Sequence: {n}!",
    )

    st.plotly_chart(fig, use_container_width=True)


# ========== Layout ==========
left, right = st.columns([1, 4])

with left:
    st.header("🧠 Math Microservice UI")
    st.caption("Select an operation, enter your values, and visualize the results.")

    operation = st.selectbox("Select Operation", ["Power", "Fibonacci", "Factorial"])
    value = st.number_input("Value", min_value=0, value=2, step=1)

    exponent = None
    if operation == "Power":
        exponent = st.number_input("Exponent", min_value=0, value=2, step=1)

    compute_btn = st.button("🚀 Compute")



# ========== Compute & Visualization ==========
with right:
    top_container = st.container()
    plot_container = st.container()

    if compute_btn:
        with st.spinner("Processing..."):
            payload = {"value": value}
            if operation == "Power":
                payload["exponent"] = exponent
            endpoint = f"{API_URL}/{operation.lower()}"

            try:
                start = time.perf_counter()
                res = requests.post(endpoint, json=payload)
                res.raise_for_status()
                end = time.perf_counter()

                result = res.json()
                elapsed = (end - start) * 1000

                with top_container:
                    st.success(f"{result['operation'].capitalize()} result: {result['result']}")
                    st.caption(f"⏱️ Completed in {elapsed:.2f} ms")

                # Plot inside container to lock vertical height
                with plot_container:
                    fig, ax = plt.subplots(figsize=(6, 3))

                    if operation == "Power" and exponent <= 20:
                       render_power_plot(value, exponent)
                       
                    elif operation == "Fibonacci":
                        if value > 7:
                            st.warning("Tree visualization limited to n ≤ 7.")
                        else:
                            render_fibonacci_graph(value)

                    elif operation == "Factorial":
                        if value > 20:
                            st.warning("Chain view limited to n ≤ 20.")
                        else:
                            render_factorial_chain(value)

            except Exception as e:
                with top_container:
                    st.error(f"❌ {e}")
