import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Page configuration
st.set_page_config(page_title="Bragg Diffraction", layout="centered")
st.title("Bragg Diffraction Simulator")
st.markdown("Interactive X-ray diffraction geometry for cubic crystals")

# --- Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Crystal")
    crystal_type = st.selectbox(
        "Structure",
        ["Simple Cubic", "BCC (Body-Centered Cubic)", "FCC (Face-Centered Cubic)"]
    )
    a = st.number_input("Lattice constant $a$ (Å)", value=4.0, min_value=0.1, format="%.2f")
    
    st.subheader("Miller Indices")
    c1, c2, c3 = st.columns(3)
    with c1:
        h = st.number_input("h", value=1, min_value=0, step=1)
    with c2:
        k = st.number_input("k", value=1, min_value=0, step=1)
    with c3:
        l = st.number_input("l", value=1, min_value=0, step=1)

with col2:
    st.subheader("X-ray Beam")
    wavelength = st.number_input("Wavelength $\\lambda$ (Å)", value=1.54, min_value=0.01, format="%.3f")
    n_order = st.number_input("Order $n$", value=1, min_value=1, step=1)

# --- Calculations ---
# Handle (000) case
if h == 0 and k == 0 and l == 0:
    st.error("Miller indices (000) undefined")
    st.stop()

# d-spacing for cubic crystals: d = a / sqrt(h² + k² + l²)
d_spacing = a / np.sqrt(h**2 + k**2 + l**2)

# Bragg's Law: nλ = 2d sinθ → θ = arcsin(nλ / 2d)
sin_theta = (n_order * wavelength) / (2 * d_spacing)

if sin_theta > 1:
    theta_deg = None
    possible = False
else:
    theta_deg = np.degrees(np.arcsin(sin_theta))
    possible = True

# Structure factor check (selection rules)
if crystal_type == "Simple Cubic":
    allowed = True
    rule_msg = "All reflections allowed"
elif crystal_type == "BCC (Body-Centered Cubic)":
    allowed = ((h + k + l) % 2 == 0)
    rule_msg = "h+k+l even" if allowed else "h+k+l odd (forbidden)"
else:  # FCC
    allowed = (h % 2 == k % 2 == l % 2)
    rule_msg = "h,k,l unmixed" if allowed else "Mixed indices (forbidden)"

# --- Results Display ---
st.divider()
st.subheader("Results")

res_cols = st.columns(4)
with res_cols[0]:
    st.metric("d-spacing", f"{d_spacing:.3f} Å")
with res_cols[1]:
    if possible:
        st.metric("θ", f"{theta_deg:.2f}°")
    else:
        st.metric("θ", "—")
with res_cols[2]:
    if possible:
        st.metric("2θ", f"{2*theta_deg:.2f}°")
    else:
        st.metric("2θ", "—")
with res_cols[3]:
    st.metric("Status", "Allowed" if allowed else "Forbidden")

# Warning messages
if not possible:
    st.error(f"Diffraction impossible: $n\\lambda/(2d) = {sin_theta:.3f} > 1$")
elif not allowed:
    st.warning(f"Structure factor F = 0 ({rule_msg}). Systematic absence.")

# Bragg equation display
if possible:
    st.latex(f"2d\\sin\\theta = n\\lambda \\Rightarrow 2({d_spacing:.3f})\\sin({theta_deg:.2f}°) = {n_order}({wavelength})")
else:
    st.latex(f"2d = {2*d_spacing:.3f} \\text{{ Å}} < n\\lambda = {n_order * wavelength:.3f} \\text{{ Å}}")

# --- Visualization ---
if possible:
    st.subheader("Geometry")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    theta_rad = np.radians(theta_deg)
    
    # Crystal planes (horizontal lines)
    plane_positions = np.arange(-3, 1) * d_spacing
    for i, y in enumerate(plane_positions):
        ax.axhline(y=y, color='#2563eb', linewidth=2, alpha=0.6)
        if i == 0:
            ax.text(-2.2, y, f'({h}{k}{l}) planes', fontsize=10, va='center', color='#2563eb')
    
    # Beam geometry
    x_range = np.linspace(-2, 2, 100)
    
    # Incident beam (from top-left)
    x_inc = np.linspace(-2, 0, 50)
    y_inc = np.tan(theta_rad) * x_inc
    ax.plot(x_inc, y_inc, 'r-', linewidth=2.5, label=f'Incident ({n_order}λ)')
    
    # Diffracted beam (to top-right)
    x_diff = np.linspace(0, 2, 50)
    y_diff = -np.tan(theta_rad) * x_diff
    ax.plot(x_diff, y_diff, 'g-', linewidth=2.5, label='Diffracted')
    
    # Scattering center
    ax.plot(0, 0, 'ko', markersize=8, zorder=5)
    
    # Angle indicator θ
    arc = patches.Arc((0, 0), 1.5, 1.5, angle=0, theta1=90-theta_deg, theta2=90, 
                      color='purple', linewidth=2)
    ax.add_patch(arc)
    ax.text(0.4, 0.8, f'θ', fontsize=12, color='purple', fontweight='bold')
    
    # 2θ indicator between beams
    arc2 = patches.Arc((0, 0), 2.0, 2.0, angle=90-theta_deg, theta1=0, theta2=2*theta_deg, 
                       color='orange', linewidth=2, linestyle='--')
    ax.add_patch(arc2)
    ax.text(-0.3, 1.2, f'2θ', fontsize=11, color='orange', fontweight='bold')
    
    # d-spacing bracket
    ax.annotate('', xy=(1.8, -d_spacing), xytext=(1.8, 0),
                arrowprops=dict(arrowstyle='<->', color='#2563eb', lw=1.5))
    ax.text(1.9, -d_spacing/2, f'd\n{d_spacing:.2f}Å', fontsize=9, color='#2563eb', va='center')
    
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-3.5, 2)
    ax.set_aspect('equal')
    ax.legend(loc='lower right', framealpha=0.9)
    ax.set_title(f'Bragg Diffraction: {crystal_type} ({h}{k}{l}), λ={wavelength}Å')
    ax.set_xlabel('Position (Å)')
    ax.set_ylabel('Position (Å)')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    st.caption(f"Incident angle θ = {theta_deg:.2f}° produces constructive interference with path difference {n_order}λ")

st.divider()
st.markdown("*Bragg's Law: $2d\\sin\\theta = n\\lambda$*  •  *Cubic d-spacing: $d = a/\\sqrt{h^2+k^2+l^2}$*")