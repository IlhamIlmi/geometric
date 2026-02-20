import streamlit as st
import math
import random
import matplotlib.pyplot as plt
import time
import streamlit.components.v1 as components

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="GeoMetric: Triangle Analyzer", page_icon="📐", layout="wide")

# --- INJEKSI CUSTOM CSS UMUM ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    /* --- DESAIN KOTAK AWAL --- */
    .stat-card {
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s ease-in-out; 
    }

    /* --- EFEK NGAMBANG & GLOW SAAT DISENTUH --- */
    .stat-card:hover {
        transform: translateY(-8px); 
        border-color: #00f2ff; 
        box-shadow: 0 10px 25px rgba(0, 242, 255, 0.4); 
        cursor: pointer;
    }

    .stat-title {
        color: #888888;
        font-size: 13px;
        font-weight: bold;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-value { font-size: 28px; font-weight: bold; margin: 0; }
    
    /* Warna Neon untuk Angka */
    .val-cyan { color: #00f2ff; text-shadow: 0 0 10px rgba(0, 242, 255, 0.3); }
    .val-purple { color: #bd00ff; text-shadow: 0 0 10px rgba(189, 0, 255, 0.3); }
    .val-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }

    .step-card { background-color: #2b2b2b; border-radius: 12px; margin-bottom: 15px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .step-header { color: #1a1a1a; font-weight: bold; padding: 8px 15px; font-size: 16px; }
    .step-body { padding: 15px; color: white; font-family: 'Consolas', monospace; font-size: 15px; line-height: 1.6; }
    .soal-kompetisi { font-size: 28px !important; text-align: center; color: #8be9fd; margin-bottom: 15px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI BANTU MATEMATIKA & VISUALISASI ---
def get_projection(p, a, b):
    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    ap_x = p[0] - a[0]
    ap_y = p[1] - a[1]
    len_sq = ab_x**2 + ab_y**2
    if len_sq == 0: return a
    t = (ap_x * ab_x + ap_y * ab_y) / len_sq
    return (a[0] + t * ab_x, a[1] + t * ab_y)

def draw_right_angle_mpl(ax, vertex, p1, p2, size):
    v1_x, v1_y = p1[0] - vertex[0], p1[1] - vertex[1]
    len1 = math.hypot(v1_x, v1_y)
    if len1 == 0: return
    u1_x, u1_y = (v1_x / len1) * size, (v1_y / len1) * size

    v2_x, v2_y = p2[0] - vertex[0], p2[1] - vertex[1]
    len2 = math.hypot(v2_x, v2_y)
    if len2 == 0: return
    u2_x, u2_y = (v2_x / len2) * size, (v2_y / len2) * size

    p_new1 = (vertex[0] + u1_x, vertex[1] + u1_y)
    p_new2 = (vertex[0] + u2_x, vertex[1] + u2_y)
    p_corner = (vertex[0] + u1_x + u2_x, vertex[1] + u1_y + u2_y)

    ax.plot([p_new1[0], p_corner[0], p_new2[0]], [p_new1[1], p_corner[1], p_new2[1]], color='#ff5555', linewidth=2)

def calculate_triangle(mode, v1, v2, v3):
    a, b, c = 0.0, 0.0, 0.0
    dA, dB, dC = 0.0, 0.0, 0.0
    steps = []

    try:
        if mode == "Sisi - Sisi - Sisi (SSS)":
            a, b, c = v1, v2, v3
            if (a + b <= c) or (a + c <= b) or (b + c <= a):
                return None, None, "Ketimpangan Segitiga: Jumlah dua sisi harus lebih besar dari sisi ketiga."
            
            dA = math.degrees(math.acos((b**2 + c**2 - a**2) / (2*b*c)))
            dB = math.degrees(math.acos((a**2 + c**2 - b**2) / (2*a*c)))
            dC = 180 - dA - dB
            
            steps.append(("0. DIKETAHUI", "#555555", f"Sisi a (BC) = {a}<br>Sisi b (AC) = {b}<br>Sisi c (AB) = {c}"))
            steps.append(("1. MENCARI SUDUT A (Aturan Kosinus)", "#61AFEF", f"a² = b² + c² - 2bc cosA<br>cosA = ({b}² + {c}² - {a}²) / (2·{b}·{c})<br><span style='color:#61AFEF; font-size:18px;'>∠A ≈ {dA:.2f}°</span>"))
            steps.append(("2. MENCARI SUDUT B (Aturan Kosinus)", "#C678DD", f"b² = a² + c² - 2ac cosB<br>cosB = ({a}² + {c}² - {b}²) / (2·{a}·{c})<br><span style='color:#C678DD; font-size:18px;'>∠B ≈ {dB:.2f}°</span>"))
            steps.append(("3. MENCARI SUDUT C", "#E06C75", f"∠C = 180° - (∠A + ∠B)<br><span style='color:#E06C75; font-size:18px;'>∠C ≈ {dC:.2f}°</span>"))

        elif mode == "Sisi - Sudut - Sisi (SAS)":
            b, dA, c = v1, v2, v3
            if dA >= 180 or dA <= 0: return None, None, "Sudut harus > 0 dan < 180."
            
            rad_A = math.radians(dA)
            a = math.sqrt(b**2 + c**2 - 2*b*c*math.cos(rad_A))
            dB = math.degrees(math.acos((a**2 + c**2 - b**2) / (2*a*c)))
            dC = 180 - dA - dB
            
            steps.append(("0. DIKETAHUI", "#555555", f"Sisi b = {b}<br>∠A = {dA}°<br>Sisi c = {c}"))
            steps.append(("1. MENCARI SISI a (Aturan Kosinus)", "#61AFEF", f"a = √({b}² + {c}² - 2·{b}·{c}·cos({dA}°))<br><span style='color:#61AFEF; font-size:18px;'>a ≈ {a:.4f}</span>"))
            steps.append(("2. MENCARI SUDUT B", "#C678DD", f"cosB = ({a:.2f}² + {c}² - {b}²) / (2·{a:.2f}·{c})<br><span style='color:#C678DD; font-size:18px;'>∠B ≈ {dB:.2f}°</span>"))
            steps.append(("3. MENCARI SUDUT C", "#E06C75", f"∠C = 180° - (∠A + ∠B)<br><span style='color:#E06C75; font-size:18px;'>∠C ≈ {dC:.2f}°</span>"))

        elif mode == "Sudut - Sisi - Sudut (ASA)":
            dA, c, dB = v1, v2, v3
            if dA + dB >= 180: return None, None, "Jumlah sudut A dan B harus < 180."
            
            dC = 180 - dA - dB
            rad_A, rad_B, rad_C = math.radians(dA), math.radians(dB), math.radians(dC)
            a = c * math.sin(rad_A) / math.sin(rad_C)
            b = c * math.sin(rad_B) / math.sin(rad_C)
            
            steps.append(("0. DIKETAHUI", "#555555", f"∠A = {dA}°<br>Sisi c = {c}<br>∠B = {dB}°"))
            steps.append(("1. MENCARI SUDUT C", "#E06C75", f"∠C = 180° - ({dA}° + {dB}°)<br><span style='color:#E06C75; font-size:18px;'>∠C = {dC:.2f}°</span>"))
            steps.append(("2. ATURAN SINUS (Mencari a & b)", "#98C379", f"a = {c} · sin({dA}°)/sin({dC:.2f}°) ≈ <span style='color:#98C379; font-weight:bold;'>{a:.2f}</span><br>b = {c} · sin({dB}°)/sin({dC:.2f}°) ≈ <span style='color:#98C379; font-weight:bold;'>{b:.2f}</span>"))

        s = (a + b + c) / 2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        peri = a + b + c
        
        steps.append(("4. LUAS & KELILING (Rumus Heron)", "#E5C07B", f"s = ({a:.2f} + {b:.2f} + {c:.2f}) / 2 = <span style='color:#E5C07B; font-weight:bold;'>{s:.2f}</span><br>L = √[s(s-a)(s-b)(s-c)]<br>L ≈ <span style='color:#E5C07B; font-size:18px;'>{area:.2f}</span><br>Keliling = <span style='color:#E5C07B; font-size:18px;'>{peri:.2f}</span>"))

        return (a, b, c, dA, dB, dC, area, peri), steps, None

    except Exception as e:
        return None, None, str(e)

def draw_triangle_plot(a, b, c, dA, dB, dC, show_alt, show_med, show_bis):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    xc = (c**2 + b**2 - a**2) / (2 * c)
    try:
        yc = math.sqrt(abs(b**2 - xc**2))
    except:
        yc = 0

    A, B, C = (0, 0), (c, 0), (xc, yc)
    max_dim = max(a, b, c) 

    if show_alt:
        proj_A = get_projection(A, B, C)
        proj_B = get_projection(B, A, C)
        proj_C = get_projection(C, A, B)
        ax.plot([A[0], proj_A[0]], [A[1], proj_A[1]], color='#ff5555', linestyle='--', linewidth=2, label='Garis Tinggi')
        ax.plot([B[0], proj_B[0]], [B[1], proj_B[1]], color='#ff5555', linestyle='--', linewidth=2)
        ax.plot([C[0], proj_C[0]], [C[1], proj_C[1]], color='#ff5555', linestyle='--', linewidth=2)

    if show_med:
        mid_BC = ((B[0]+C[0])/2, (B[1]+C[1])/2)
        mid_AC = ((A[0]+C[0])/2, (A[1]+C[1])/2)
        mid_AB = ((A[0]+B[0])/2, (A[1]+B[1])/2)
        ax.plot([A[0], mid_BC[0]], [A[1], mid_BC[1]], color='#f1fa8c', linestyle='-.', linewidth=2, label='Garis Berat')
        ax.plot([B[0], mid_AC[0]], [B[1], mid_AC[1]], color='#f1fa8c', linestyle='-.', linewidth=2)
        ax.plot([C[0], mid_AB[0]], [C[1], mid_AB[1]], color='#f1fa8c', linestyle='-.', linewidth=2)

    if show_bis:
        D_a = ((b*B[0] + c*C[0])/(b+c), (b*B[1] + c*C[1])/(b+c))
        D_b = ((a*A[0] + c*C[0])/(a+c), (a*A[1] + c*C[1])/(a+c))
        D_c = ((a*A[0] + b*B[0])/(a+b), (a*A[1] + b*B[1])/(a+b))
        ax.plot([A[0], D_a[0]], [A[1], D_a[1]], color='#50fa7b', linestyle=':', linewidth=2.5, label='Garis Bagi')
        ax.plot([B[0], D_b[0]], [B[1], D_b[1]], color='#50fa7b', linestyle=':', linewidth=2.5)
        ax.plot([C[0], D_c[0]], [C[1], D_c[1]], color='#50fa7b', linestyle=':', linewidth=2.5)

    ax.plot([A[0], B[0], C[0], A[0]], [A[1], B[1], C[1], A[1]], color='#4cc9f0', linewidth=3)
    
    # --- BAGIAN LABEL YANG SEMPAT HILANG ---
    sq_size = max_dim * 0.05
    if math.isclose(dA, 90, abs_tol=0.5): draw_right_angle_mpl(ax, A, C, B, sq_size)
    if math.isclose(dB, 90, abs_tol=0.5): draw_right_angle_mpl(ax, B, C, A, sq_size)
    if math.isclose(dC, 90, abs_tol=0.5): draw_right_angle_mpl(ax, C, A, B, sq_size)

    offset = max_dim * 0.05
    ax.text(A[0]-offset, A[1]-offset, f"A\n({dA:.0f}°)", fontsize=11, ha='right', color='white', fontweight='bold')
    ax.text(B[0]+offset, B[1]-offset, f"B\n({dB:.0f}°)", fontsize=11, ha='left', color='white', fontweight='bold')
    ax.text(C[0], C[1]+offset, f"C\n({dC:.0f}°)", fontsize=11, ha='center', color='white', fontweight='bold')

    ax.text((B[0]+C[0])/2 + offset, (B[1]+C[1])/2, "a", fontsize=12, color="#ffffff", fontweight='bold', style='italic')
    ax.text((A[0]+C[0])/2 - offset, (A[1]+C[1])/2, "b", fontsize=12, color='#ffffff', fontweight='bold', style='italic', ha='right')
    ax.text((A[0]+B[0])/2, (A[1]+B[1])/2 - offset, "c", fontsize=12, color='#ffffff', fontweight='bold', style='italic', va='top')
    # ---------------------------------------

    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# --- STATE MANAGEMENT ---
if 'quiz_q' not in st.session_state: st.session_state.quiz_q = None
if 'quiz_ans' not in st.session_state: st.session_state.quiz_ans = None
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None
if 'quiz_q_type' not in st.session_state: st.session_state.quiz_q_type = None

# State Kompetisi
if 'comp_active' not in st.session_state: st.session_state.comp_active = False
if 'comp_score' not in st.session_state: st.session_state.comp_score = 0
if 'comp_total' not in st.session_state: st.session_state.comp_total = 0
if 'comp_end_time' not in st.session_state: st.session_state.comp_end_time = 0
if 'comp_q' not in st.session_state: st.session_state.comp_q = None
if 'comp_ans' not in st.session_state: st.session_state.comp_ans = None

def generate_random_triangle():
    while True:
        a = random.randint(3, 15)
        b = random.randint(3, 15)
        min_c = abs(a - b) + 1
        max_c = a + b - 1
        if min_c > max_c: continue 
        c = random.randint(min_c, max_c)
        if a+b>c and a+c>b and b+c>a: 
            return a, b, c

def generate_quiz():
    q_type = random.choice(["keliling", "luas_heron", "luas_sas"])
    st.session_state.quiz_q_type = q_type
    
    if q_type == "keliling":
        a, b, c = generate_random_triangle()
        st.session_state.quiz_data = (a, b, c)
        st.session_state.quiz_q = f"Sisi: **a={a}, b={b}, c={c}**. KELILING = ?"
        st.session_state.quiz_ans = str(a + b + c)
        
    elif q_type == "luas_heron":
        a, b, c = generate_random_triangle()
        st.session_state.quiz_data = (a, b, c)
        st.session_state.quiz_q = f"Sisi: **a={a}, b={b}, c={c}**. LUAS = ? *(Bulat)*"
        s = (a+b+c)/2
        ans = math.sqrt(s * (s-a) * (s-b) * (s-c))
        st.session_state.quiz_ans = str(round(ans))
        
    elif q_type == "luas_sas":
        a = random.randint(3, 15)
        b = random.randint(3, 15)
        angle = random.choice([30, 45, 60, 90, 120, 135, 150]) 
        st.session_state.quiz_data = (a, b, angle)
        st.session_state.quiz_q = f"Sisi: **a={a}, b={b}** dan Sudut Apit **C={angle}°**. LUAS = ? *(Bulat)*"
        ans = 0.5 * a * b * math.sin(math.radians(angle))
        st.session_state.quiz_ans = str(round(ans))

def start_competition():
    st.session_state.comp_active = True
    st.session_state.comp_score = 0
    st.session_state.comp_total = 0
    st.session_state.comp_end_time = time.time() + 300 
    generate_comp_quiz()

def generate_comp_quiz():
    q_type = random.choice(["luas_heron", "luas_sas"])
        
    if q_type == "luas_heron":
        a, b, c = generate_random_triangle()
        st.session_state.comp_q = f"Sisi: a={a}, b={b}, c={c}. LUAS (Dibulatkan) = ?"
        s = (a+b+c)/2
        ans = math.sqrt(s * (s-a) * (s-b) * (s-c))
        st.session_state.comp_ans = str(round(ans))
        
    elif q_type == "luas_sas":
        a = random.randint(3, 15)
        b = random.randint(3, 15)
        angle = random.choice([30, 45, 60, 90, 120, 135, 150])
        st.session_state.comp_q = f"a={a}, b={b}, ∠C={angle}°. LUAS (Dibulatkan) = ?"
        ans = 0.5 * a * b * math.sin(math.radians(angle))
        st.session_state.comp_ans = str(round(ans))


# =========================================================================
# 🔴 PENGATURAN UI UTAMA (PEMISAHAN NORMAL VS LOCKDOWN MODE)
# =========================================================================

if st.session_state.comp_active:
    # --- LOCKDOWN MODE (SPEED RUN AKTIF) ---
    # CSS Agresif: Sembunyikan semua elemen navigasi bawaan Streamlit secara paksa
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        button[data-testid="collapsedControl"] { display: none !important; }
        button[kind="header"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .stApp > header { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    time_left = int(st.session_state.comp_end_time - time.time())
    
    if time_left <= 0:
        st.session_state.comp_active = False
        st.rerun()
    else:
        st.markdown("<h1 style='text-align: center; color: #ff5555;'>🔥 MODE SPEED RUN AKTIF 🔥</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Fokus! Semua menu dan tab lain dikunci sementara sampai waktu habis.</p>", unsafe_allow_html=True)
        
        components.html(f"""
        <div style="font-family: sans-serif; font-size: 28px; font-weight: bold; color: #ff5555; text-align: center; background: #2b2b2b; padding: 15px; border-radius: 8px; border: 2px solid #ff5555;">
            ⏱️ Waktu Tersisa: <span id="timer">{time_left}</span> detik
        </div>
        <script>
            var timeLeft = {time_left};
            var timerId = setInterval(function() {{
                timeLeft--;
                if (timeLeft <= 0) {{
                    clearInterval(timerId);
                    document.getElementById("timer").innerHTML = "HABIS!";
                }} else {{
                    document.getElementById("timer").innerHTML = timeLeft;
                }}
            }}, 1000);
        </script>
        """, height=90)
        
        st.markdown(f"<div class='soal-kompetisi'>{st.session_state.comp_q}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-size: 20px;'>Skor Sementara: <b style='color:#50fa7b;'>{st.session_state.comp_score}</b> Benar</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.form("comp_form", clear_on_submit=True):
                user_ans = st.text_input("Ketik jawaban (Angka Saja) lalu tekan Enter:", autocomplete="off")
                submitted = st.form_submit_button("Kirim Jawaban Cepat", use_container_width=True)
                
                if submitted:
                    if time.time() > st.session_state.comp_end_time:
                        st.session_state.comp_active = False
                        st.rerun()
                    else:
                        st.session_state.comp_total += 1
                        if user_ans:
                            try:
                                if math.isclose(float(user_ans), float(st.session_state.comp_ans), abs_tol=0.1):
                                    st.session_state.comp_score += 1
                            except:
                                pass
                        generate_comp_quiz()
                        st.rerun()
        
        st.markdown("---")
        col_a, col_b, col_c = st.columns([2,1,2])
        with col_b:
            if st.button("🛑 Menyerah", type="secondary", use_container_width=True):
                st.session_state.comp_active = False
                st.rerun()

else:
    # --- NORMAL MODE (TAMPILKAN SEMUA MENU) ---
    st.title("📐 GeoMetric: Triangle Analyzer")

    with st.expander("📖 Panduan Pengguna (Klik untuk membuka)", expanded=False):
        st.markdown("""
        **Selamat Datang di GeoMetric!**
        
        1. **Pilih Mode Input:** Gunakan dropdown di sidebar (kiri) untuk memilih jenis input.
        2. **Input Data:** Masukkan nilai sisi/sudut. Visualisasi akan otomatis terupdate.
        3. **Garis Istimewa:** Centang opsi di sidebar untuk menampilkan garis.
        4. **Langkah Pengerjaan:** Klik tab **📝 Langkah Pengerjaan Detail** untuk melihat rumus.
        5. **Latihan & Kompetisi:** Uji pemahamanmu, atau mainkan **Speed Run (300 Detik)**!
        """)

    with st.sidebar:
        st.header("Input Data")
        mode = st.selectbox("Pilih Mode Input:", ["Sisi - Sisi - Sisi (SSS)", "Sisi - Sudut - Sisi (SAS)", "Sudut - Sisi - Sudut (ASA)"])
        
        if "SSS" in mode:
            v1 = st.number_input("Sisi a (BC):", min_value=0.1, value=5.0, step=0.1)
            v2 = st.number_input("Sisi b (AC):", min_value=0.1, value=6.0, step=0.1)
            v3 = st.number_input("Sisi c (AB):", min_value=0.1, value=7.0, step=0.1)
        elif "SAS" in mode:
            v1 = st.number_input("Sisi b (Kiri):", min_value=0.1, value=6.0, step=0.1)
            v2 = st.number_input("Sudut A (Derajat):", min_value=1.0, max_value=179.0, value=60.0, step=1.0)
            v3 = st.number_input("Sisi c (Bawah):", min_value=0.1, value=7.0, step=0.1)
        elif "ASA" in mode:
            v1 = st.number_input("Sudut A (Derajat):", min_value=1.0, max_value=179.0, value=45.0, step=1.0)
            v2 = st.number_input("Sisi c (Tengah):", min_value=0.1, value=10.0, step=0.1)
            v3 = st.number_input("Sudut B (Derajat):", min_value=1.0, max_value=179.0, value=60.0, step=1.0)

        st.markdown("---")
        st.subheader("Garis Istimewa")
        show_alt = st.checkbox("Garis Tinggi (Altitude)")
        show_med = st.checkbox("Garis Berat (Median)")
        show_bis = st.checkbox("Garis Bagi (Bisector)")

    data, steps, err = calculate_triangle(mode, v1, v2, v3)

    tab1, tab2, tab3 = st.tabs(["📊 Visualisasi & Hasil", "📝 Langkah Pengerjaan Detail", "🎯 Mode Latihan & Kompetisi"])

    with tab1:
        if err:
            st.error(err)
        elif data:
            a, b, c, dA, dB, dC, area, peri = data
            
            jenis_sisi = "Sembarang"
            if math.isclose(a, b) and math.isclose(b, c): jenis_sisi = "Sama Sisi"
            elif math.isclose(a, b) or math.isclose(a, c) or math.isclose(b, c): jenis_sisi = "Sama Kaki"
            
            jenis_sudut = "Lancip"
            if any(math.isclose(x, 90, abs_tol=0.1) for x in [dA, dB, dC]): jenis_sudut = "Siku-siku"
            elif any(x > 90.1 for x in [dA, dB, dC]): jenis_sudut = "Tumpul"

            html_cards = f"""
            <div style="display: flex; justify-content: space-between; gap: 15px;">
                <div class="stat-card" style="flex: 1;">
                    <div class="stat-title">KELILING</div>
                    <div class="stat-value val-cyan">{peri:.2f}</div>
                </div>
                <div class="stat-card" style="flex: 1;">
                    <div class="stat-title">LUAS AREA (HERON)</div>
                    <div class="stat-value val-purple">{area:.2f}</div>
                </div>
                <div class="stat-card" style="flex: 1;">
                    <div class="stat-title">KLASIFIKASI</div>
                    <div class="stat-value val-green" style="font-size: 22px; line-height: 1.3;">{jenis_sudut}<br>{jenis_sisi}</div>
                </div>
            </div>
            """
            st.markdown(html_cards, unsafe_allow_html=True)

            fig = draw_triangle_plot(a, b, c, dA, dB, dC, show_alt, show_med, show_bis)
            st.pyplot(fig)

    with tab2:
        st.header("Analisis Matematis")
        if err:
            st.warning("Data segitiga tidak valid.")
        elif steps:
            for title, color, content in steps:
                card_html = f"""
                <div class="step-card" style="border: 2px solid {color};">
                    <div class="step-header" style="background-color: {color};">
                        {title}
                    </div>
                    <div class="step-body">
                        {content}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    with tab3:
        pilihan_mode = st.radio("Pilih Tipe Latihan:", ["Latihan Santai (Ada Pembahasan)", "Speed Run (Kompetisi 300 Detik)"], horizontal=True)
        st.markdown("---")

        if pilihan_mode == "Latihan Santai (Ada Pembahasan)":
            if st.button("Generate Soal Baru", on_click=generate_quiz):
                pass 
                
            if st.session_state.quiz_q:
                st.info(st.session_state.quiz_q)
                
                with st.form("form_latihan", clear_on_submit=True):
                    user_ans = st.text_input("Jawaban (Angka Saja):", autocomplete="off")
                    submitted = st.form_submit_button("Kirim Jawaban")
                    
                    if submitted:
                        if not user_ans:
                            st.warning("Mohon masukkan jawaban terlebih dahulu.")
                        else:
                            try:
                                is_correct = False
                                ans_correct = st.session_state.quiz_ans
                                
                                if math.isclose(float(user_ans), float(ans_correct), abs_tol=0.1):
                                    is_correct = True
                                        
                                if is_correct:
                                    st.success("✅ Tepat Sekali!")
                                else:
                                    st.error(f"❌ Kurang tepat. Jawaban yang benar adalah: {ans_correct}")
                                
                                q_type = st.session_state.quiz_q_type
                                st.markdown("### 💡 Pembahasan Detail:")
                                
                                if q_type == "keliling":
                                    a, b, c = st.session_state.quiz_data
                                    st.info(f"**Rumus Keliling** = a + b + c = {a} + {b} + {c} = **{ans_correct}**")
                                elif q_type == "luas_heron":
                                    a, b, c = st.session_state.quiz_data
                                    s = (a + b + c) / 2
                                    luas_asli = math.sqrt(s * (s - a) * (s - b) * (s - c))
                                    st.info(f"**Cari (s):** ({a} + {b} + {c}) / 2 = **{s}** \n\n **Rumus Heron:** √[{s} · ({s}-{a}) · ({s}-{b}) · ({s}-{c})] ≈ {luas_asli:.2f} \n\n **Dibulatkan:** **{ans_correct}**")
                                elif q_type == "luas_sas":
                                    a, b, angle = st.session_state.quiz_data
                                    luas_asli = 0.5 * a * b * math.sin(math.radians(angle))
                                    st.info(f"**Rumus Luas (Trigonometri):** 1/2 × a × b × sin(C) \n\n = 1/2 × {a} × {b} × sin({angle}°) \n\n ≈ {luas_asli:.2f} \n\n **Dibulatkan:** **{ans_correct}**")
                            except ValueError:
                                st.warning("Mohon masukkan hanya angka yang valid.")
                                
        else:
            st.markdown("<h3 style='text-align: center;'>Bersiaplah! Kamu punya waktu 300 detik.</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 MULAI KOMPETISI!", use_container_width=True, type="primary"):
                    start_competition()
                    st.rerun()
            
            if st.session_state.comp_total > 0:
                st.success(f"🏆 PERMAINAN SELESAI! Skor Terakhir Kamu: **{st.session_state.comp_score} BENAR** dari {st.session_state.comp_total} soal.")
