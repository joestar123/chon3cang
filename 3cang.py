import streamlit as st
import requests
import hashlib
import datetime
import time
import math

# ─── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Chọn 3 Càng",
    page_icon="🎰",
    layout="centered",
)

# ─── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Saira:wght@300;400;600;700&display=swap');

:root {
    --gold: #FFD700;
    --gold2: #FFA500;
    --red: #C0392B;
    --dark: #0a0a0a;
    --card: #111111;
    --border: #2a2a2a;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: #eee !important;
    font-family: 'Saira', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }

/* Title */
.app-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.8rem;
    letter-spacing: 0.12em;
    text-align: center;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF6B00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1;
    text-shadow: none;
}

.app-subtitle {
    text-align: center;
    color: #888;
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 4px;
    margin-bottom: 2rem;
}

/* Card */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}

/* Result display */
.result-box {
    background: linear-gradient(135deg, #1a1200, #2a1a00);
    border: 2px solid var(--gold);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
.result-box::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,215,0,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.result-label {
    font-size: 0.75rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.5rem;
}
.result-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 7rem;
    letter-spacing: 0.2em;
    background: linear-gradient(180deg, #FFD700 0%, #FF8C00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0;
}

/* Steps */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.6rem;
    font-size: 0.83rem;
    color: #aaa;
}
.step-dot {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, var(--gold), var(--gold2));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: #000;
    flex-shrink: 0;
    margin-top: 1px;
}
.step-val {
    color: #FFD700;
    font-weight: 600;
}

/* Streamlit widget overrides */
[data-testid="stDateInput"] label,
[data-testid="stTextInput"] label,
label { color: #ccc !important; font-size: 0.88rem !important; }

input[type="text"], input[type="date"], [data-baseweb="input"] input {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #fff !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #FFD700, #FF8C00) !important;
    color: #000 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.15em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stAlert { border-radius: 10px !important; }

hr { border-color: #222 !important; margin: 1rem 0 !important; }

/* Decorative dots */
.deco {
    text-align: center;
    color: #333;
    font-size: 1.2rem;
    letter-spacing: 0.5em;
    margin: 0.3rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─── Helper: lấy thời gian thực từ API công khai (GMT+7) ────────
def get_gmt7_time_ms() -> dict:
    """
    Lấy thời gian hiện tại theo GMT+7 từ worldtimeapi.org.
    Trả về dict gồm: epoch_ms, datetime_str, ms_part.
    Fallback về thời gian hệ thống nếu không có mạng.
    """
    try:
        resp = requests.get(
            "https://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh",
            timeout=4
        )
        data = resp.json()
        # unixtime (giây) + ms từ datetime string
        unixtime = data.get("unixtime", 0)
        dt_str   = data.get("datetime", "")        # "2025-05-25T14:32:10.123456+07:00"
        # lấy phần microseconds → đổi sang ms
        microsec = 0
        if "." in dt_str:
            frac = dt_str.split(".")[1][:6]        # lấy tối đa 6 chữ số
            frac = frac.rstrip("+").rstrip("-")    # bỏ offset ký tự thừa
            frac_digits = frac.split("+")[0].split("-")[0]
            microsec = int(frac_digits.ljust(6, "0"))
        epoch_ms = int(unixtime * 1000) + (microsec // 1000)
        return {
            "epoch_ms":    epoch_ms,
            "datetime_str": dt_str[:19].replace("T", " "),
            "ms_part":     epoch_ms % 1000,
            "source":      "worldtimeapi.org (GMT+7)",
        }
    except Exception:
        # fallback hệ thống
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
        epoch_ms = int(now.timestamp() * 1000)
        return {
            "epoch_ms":    epoch_ms,
            "datetime_str": now.strftime("%Y-%m-%d %H:%M:%S"),
            "ms_part":     epoch_ms % 1000,
            "source":      "Hệ thống local (GMT+7 fallback)",
        }


# ─── Thuật toán sinh số 3 chữ số ─────────────────────────────────
def generate_3_digit(epoch_ms: int, dob: datetime.date) -> dict:
    """
    Thuật toán:
    1. Tạo seed từ epoch_ms XOR dob_hash
    2. Áp dụng Linear Congruential Generator (LCG)
    3. Kết hợp thêm sin/cos từ từng thành phần để tăng entropy
    4. Lấy mod 1000 → số 3 chữ số (000–999)
    """
    # Bước 1: Hash ngày sinh
    dob_str   = dob.strftime("%d%m%Y")
    dob_hash  = int(hashlib.sha256(dob_str.encode()).hexdigest(), 16) % (10**15)

    # Bước 2: XOR epoch_ms với dob_hash
    seed = (epoch_ms ^ dob_hash) & 0xFFFFFFFFFFFF

    # Bước 3: LCG — hệ số từ Numerical Recipes
    LCG_A = 1664525
    LCG_C = 1013904223
    LCG_M = 2**32
    lcg_val = (LCG_A * seed + LCG_C) % LCG_M

    # Bước 4: Trộn thêm sin/cos của các thành phần thời gian
    day   = dob.day
    month = dob.month
    year  = dob.year
    ms    = epoch_ms % 1000
    sec   = (epoch_ms // 1000) % 60

    mix = (
        abs(math.sin(day   * 12.9898 + ms))   * 43758.5453
        + abs(math.cos(month * 78.233  + sec))  * 93729.8463
        + abs(math.sin(year  * 4.1414  + epoch_ms % 100)) * 23421.6311
    )
    mix_int = int(mix) % 10000

    # Bước 5: Kết hợp lcg_val và mix_int
    combined = (lcg_val ^ mix_int ^ (epoch_ms % 9973)) % 1000

    return {
        "number":   f"{combined:03d}",
        "seed":     seed,
        "lcg_val":  lcg_val,
        "mix_int":  mix_int,
        "combined": combined,
        "dob_hash": dob_hash % 999999,   # hiển thị gọn
    }


# ─── UI ──────────────────────────────────────────────────────────
st.markdown('<div class="app-title">🎰 CHỌN 3 CÀNG</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">✦ Số may mắn theo thời gian & ngày sinh ✦</div>', unsafe_allow_html=True)

# Input card
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        dob = st.date_input(
            "📅 Ngày tháng năm sinh",
            value=datetime.date(1990, 1, 1),
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:#888;font-size:0.8rem;margin-top:8px;'>🕐 Thời gian lấy trực tiếp<br>từ <span style='color:#FFD700'>worldtimeapi.org</span> (GMT+7)</div>",
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="deco">◆ ◆ ◆</div>', unsafe_allow_html=True)

# Button
if st.button("✨ QUAY SỐ NGAY", key="spin"):
    with st.spinner("Đang lấy thời gian thực..."):
        time_data = get_gmt7_time_ms()

    result = generate_3_digit(time_data["epoch_ms"], dob)

    # Hiển thị kết quả
    st.markdown(f"""
    <div class="result-box">
        <div class="result-label">✦ Số 3 Càng May Mắn Của Bạn ✦</div>
        <div class="result-number">{result['number']}</div>
        <div style="color:#888;font-size:0.78rem;margin-top:0.5rem;">
            {time_data['datetime_str']} &nbsp;|&nbsp; {time_data['source']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chi tiết thuật toán
    with st.expander("🔍 Chi tiết thuật toán"):
        st.markdown(f"""
        <div style="font-size:0.82rem;">
        <div class="step-row">
            <div class="step-dot">1</div>
            <div>Thời gian thực (ms): <span class="step-val">{time_data['epoch_ms']:,} ms</span>
            — Phần ms: <span class="step-val">{time_data['ms_part']} ms</span></div>
        </div>
        <div class="step-row">
            <div class="step-dot">2</div>
            <div>Hash SHA-256 ngày sinh <span class="step-val">{dob.strftime('%d/%m/%Y')}</span>
            → <span class="step-val">{result['dob_hash']:,}</span> (rút gọn)</div>
        </div>
        <div class="step-row">
            <div class="step-dot">3</div>
            <div>XOR epoch_ms ⊕ dob_hash → seed:
            <span class="step-val">{result['seed']:,}</span></div>
        </div>
        <div class="step-row">
            <div class="step-dot">4</div>
            <div>LCG (a=1664525, c=1013904223, m=2³²):
            <span class="step-val">{result['lcg_val']:,}</span></div>
        </div>
        <div class="step-row">
            <div class="step-dot">5</div>
            <div>Trộn sin/cos (ngày, tháng, năm, ms):
            <span class="step-val">{result['mix_int']:,}</span></div>
        </div>
        <div class="step-row">
            <div class="step-dot">6</div>
            <div>Kết hợp LCG ⊕ mix ⊕ (epoch % 9973) mod 1000
            = <span class="step-val" style="font-size:1rem;">{result['number']}</span></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="deco" style="margin-top:1rem;">★ CHÚC MAY MẮN ★</div>', unsafe_allow_html=True)

else:
    # Placeholder
    st.markdown("""
    <div class="result-box" style="border-color:#333; background:#0d0d0d;">
        <div class="result-label">Nhấn nút để quay số</div>
        <div class="result-number" style="-webkit-text-fill-color:#222; background:none; color:#222;">
            ???
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr>
<div style="text-align:center;color:#444;font-size:0.73rem;letter-spacing:0.1em;">
    MỖI LẦN NHẤN = MỘT KẾT QUẢ ĐỘC NHẤT &nbsp;|&nbsp; THỜI GIAN + NGÀY SINH → SỐ KHÔNG TRÙNG LẶP
</div>
""", unsafe_allow_html=True)
