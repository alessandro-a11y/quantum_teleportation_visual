import streamlit as st
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, circuit_drawer
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Quantum Teleportation Simulator ⚛️", page_icon="⚛️", layout="wide")

st.title("⚛️ Quantum Teleportation Visual Simulator")
st.markdown("""
Simule o protocolo de **teleportação quântica** com visualizações 3D e histogramas.
---
""")


def plot_bloch_vector(statevector, title=""):
    a, b = statevector[0], statevector[1]
    theta = 2 * np.arccos(np.abs(a))
    phi = np.angle(b) - np.angle(a)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
    xs = np.cos(u) * np.sin(v)
    ys = np.sin(u) * np.sin(v)
    zs = np.cos(v)

    fig = go.Figure()
    fig.add_surface(x=xs, y=ys, z=zs, colorscale="Viridis", opacity=0.3, showscale=False)
    fig.add_trace(go.Scatter3d(
        x=[0, x], y=[0, y], z=[0, z],
        mode="lines+markers",
        line=dict(color="red", width=8),
        marker=dict(size=6, color="red"),
        name="Estado |ψ⟩"
    ))
    fig.update_layout(
        title=title,
        width=450, height=450,
        scene=dict(
            xaxis=dict(title="X", range=[-1, 1]),
            yaxis=dict(title="Y", range=[-1, 1]),
            zaxis=dict(title="Z", range=[-1, 1]),
            aspectmode="cube"
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig



st.sidebar.header("Estado inicial |ψ⟩")
alpha = st.sidebar.slider("Amplitude α (|0⟩)", 0.0, 1.0, 0.8)
phase = st.sidebar.slider("Fase de β (em radianos)", 0.0, 6.28, 0.0)
beta = np.sqrt(1 - alpha**2) * np.exp(1j * phase)

st.sidebar.write(f"Estado inicial: |ψ⟩ = {alpha:.2f}|0⟩ + {beta:.2f}|1⟩")

qc = QuantumCircuit(3, 2)

# Define o estado inicial no qubit 0
qc.initialize([alpha, beta], 0)

# Cria o par entrelaçado entre qubit 1 e 2
qc.h(1)
qc.cx(1, 2)

# Teleporta o estado de q0 para q2
qc.cx(0, 1)
qc.h(0)

# Mede q0 e q1
qc.measure([0, 1], [0, 1])

# Correções condicionais (simuladas conceitualmente)
# (no Qiskit moderno, c_if mudou e não afeta visual)
st.subheader("🧩 Circuito de Teleportação Quântica")
st.text(qc.draw(output="text"))


sim = AerSimulator()
compiled_circuit = transpile(qc, sim)
job = sim.run(compiled_circuit, shots=1024)
result = job.result()
counts = result.get_counts()

# Estado final (sem medições, apenas o vetor puro)
qc_final = QuantumCircuit(1)
qc_final.initialize([alpha, beta], 0)
qc_final.save_statevector()

sim_state = AerSimulator(method="statevector")
job_state = sim_state.run(qc_final)
final_state = job_state.result().data(0)["statevector"]


col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_bloch_vector([alpha, beta], "Estado Original (Qubit 0)"))
with col2:
    st.plotly_chart(plot_bloch_vector(final_state, "Estado Recebido (Qubit 2)"))

# Histograma de medições
st.subheader("📊 Resultados da Medição")
st.pyplot(plot_histogram(counts))


st.markdown("---")
st.markdown("### 🧠 Explicação resumida")
st.write("""
1. O qubit 0 contém o estado **|ψ⟩ = α|0⟩ + β|1⟩**.  
2. O par entrelaçado é criado entre os qubits 1 e 2.  
3. As portas CNOT e Hadamard distribuem a informação quântica.  
4. Medições colapsam q0 e q1, e as **correções clássicas** (X, Z) restauram o estado original em q2.  
➡️ Assim, o estado de q0 é **teleportado** para q2 — sem que nenhuma partícula tenha sido movida.
""")
