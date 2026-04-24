import streamlit as st
import pandas as pd
import os
from tabs.tab1 import render_tab1
from tabs.tab2 import render_tab2
from tabs.tab3 import render_tab3
from tabs.tab4 import render_tab4

# Cấu hình website
st.set_page_config(page_title="Tiki Book Analytics", page_icon="📚", layout="wide")

# Tiêm CSS để ép giao diện nằm giữa và dãn đều Tab
st.markdown("""
<style>
    /* ========== ANIMATIONS ========== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-5px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* ========== THEME COLOR ========== */
    :root {
        --primary-color: #0066FF;        /* Xanh dương Tiki */
        --secondary-color: #00A699;      /* Xanh lục nhẹ */
        --success-color: #52C41A;        /* Xanh lá thành công */
        --warning-color: #FF7A45;        /* Cam cảnh báo */
        --info-color: #1890FF;           /* Xanh info */
        --bg-light: #F5F7FA;             /* Nền sáng */
        --text-primary: #1A1A1A;         /* Text đậm */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 12px rgba(0, 102, 255, 0.2);
    }

    /* Căn giữa Tiêu đề dự án */
    .title-center {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 30px 0 45px 0;
        padding: 20px;
        color: #0066FF;
        letter-spacing: -0.5px;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .title-center::before {
        content: '📚 ';
        margin-right: 10px;
        font-size: 3rem;
    }
    
    /* ========== TAB STYLING (Button Style) ========== */
    /* Container của tabs */
    [data-baseweb="tab-list"] {
        background-color: #F5F7FA !important;
        border-radius: 12px !important;
        padding: 8px !important;
        gap: 8px !important;
        margin-bottom: 32px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Ép các Tab (Option) giãn đều ra 100% màn hình, giống button */
    button[data-baseweb="tab"] {
        flex: 1 !important;
        text-align: center !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        background-color: white !important;
        color: #666666 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 4px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Hover effect cho tab */
    button[data-baseweb="tab"]:hover {
        background-color: #E8F0FF !important;
        color: #0066FF !important;
        box-shadow: 0 2px 6px rgba(0, 102, 255, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Tab active (selected) */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0066FF 0%, #00A699 100%) !important;
        color: white !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(0) !important;
    }

    /* Căn giữa các tiêu đề H2 (Tên của từng Tab) và H3 (Tiêu đề biểu đồ) */
    h1, h2, h3 {
        text-align: center !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        animation: slideIn 0.4s ease-out !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        margin-top: 35px !important;
        margin-bottom: 12px !important;
        color: #0066FF !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        color: #1A1A1A !important;
        margin-top: 25px !important;
    }
    
    /* Căn giữa văn bản diễn giải in nghiêng dưới H2 */
    p > em {
        display: block;
        text-align: center !important;
        color: #999999 !important;
        font-size: 0.95rem !important;
        margin-top: 8px !important;
        line-height: 1.5 !important;
    }
    
    /* ========== METRIC STYLING ========== */
    /* Căn giữa toàn bộ khối Số liệu KPI (st.metric) */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%) !important;
        padding: 24px 18px !important;
        border-radius: 12px !important;
        border-left: 4px solid #0066FF !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 14px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s ease !important;
        animation: fadeInUp 0.5s ease-out !important;
    }
    
    /* Hover effect metrics */
    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
        border-left-color: #00A699 !important;
    }
    
    /* Label styling */
    [data-testid="stMetricLabel"] {
        width: 100% !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stMetricLabel"] > div {
        color: #666666 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        text-align: center !important;
        line-height: 1.5 !important;
        font-weight: 500 !important;
    }
    
    /* Value styling */
    [data-testid="stMetricValue"] {
        width: 100% !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stMetricValue"] > div {
        color: #0066FF !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        text-align: center !important;
        line-height: 1.3 !important;
        letter-spacing: -0.3px !important;
    }
    
    /* Delta styling */
    [data-testid="stMetricDelta"] {
        width: 100% !important;
        text-align: center !important;
    }
    
    /* ========== CARD STYLING ========== */
    /* Container styling */
    [data-testid="stVerticalBlockContainer"] {
        gap: 24px !important;
    }
    
    /* Chart container */
    [data-testid="stPlotlyContainer"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 20px !important;
        background-color: #FFFFFF !important;
        box-shadow: var(--shadow-sm) !important;
        animation: fadeInUp 0.5s ease-out !important;
    }
    
    /* ========== SIDEBAR STYLING ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
        padding: 20px !important;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #0066FF !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        margin: 20px 0 12px 0 !important;
        letter-spacing: -0.3px !important;
        padding-bottom: 12px !important;
        border-bottom: 2px solid #E5E7EB !important;
    }
    
    /* Sidebar markdown text */
    [data-testid="stSidebar"] p {
        font-size: 0.88rem !important;
        line-height: 1.5 !important;
        color: #666666 !important;
        margin-bottom: 14px !important;
        padding-bottom: 0 !important;
    }
    
    /* ========== FILTER SECTION GROUPING ========== */
    /* Container cho mỗi filter group */
    [data-testid="stSidebar"] > div > div > div:not(:first-child) {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 14px 14px !important;
        margin-bottom: 12px !important;
        border: 1px solid #E8EDF5 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] > div > div > div:not(:first-child):hover {
        border-color: #D5E8F5 !important;
        box-shadow: 0 2px 6px rgba(0, 102, 255, 0.08) !important;
    }
    
    /* ========== INPUT LABELS ========== */
    [data-testid="stSidebar"] label {
        font-weight: 600 !important;
        color: #0066FF !important;
        font-size: 0.88rem !important;
        margin-bottom: 10px !important;
        display: block !important;
        line-height: 1.3 !important;
        letter-spacing: -0.3px !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid #E8EDF5 !important;
    }
    
    /* Slider styling */
    [data-testid="stSlider"] {
        margin: 12px 0 24px 0 !important;
    }
    
    [data-testid="stSlider"] [data-baseweb="slider"] {
        color: #0066FF !important;
    }
    
    /* Slider container safety */
    [data-testid="stSlider"] > div {
        overflow: visible !important;
    }
    
    /* Slider track container */
    [data-baseweb="slider"] {
        width: 100% !important;
    }
    
    /* Slider thumb (nút kéo) */
    [data-baseweb="slider"] [role="slider"] {
        background-color: #0066FF !important;
        box-shadow: 0 2px 6px rgba(0, 102, 255, 0.3) !important;
        transition: box-shadow 0.2s ease !important;
        width: 18px !important;
        height: 18px !important;
    }
    
    [data-baseweb="slider"] [role="slider"]:hover {
        box-shadow: 0 3px 8px rgba(0, 102, 255, 0.4), 0 0 0 3px rgba(0, 102, 255, 0.15) !important;
    }
    
    /* Slider track (đường nền) */
    [data-baseweb="slider"] > div > div {
        background-color: #E5E7EB !important;
        height: 6px !important;
        border-radius: 3px !important;
    }
    
    /* Slider active track (đường được điền) */
    [data-baseweb="slider"] > div > div > div {
        background: linear-gradient(90deg, #0066FF, #00A699) !important;
        height: 6px !important;
        border-radius: 3px !important;
    }
    
    /* Slider labels (min/max values) */
    [data-testid="stSlider"] span {
        font-size: 0.8rem !important;
        color: #999999 !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px !important;
    }
    
    /* ========== MULTISELECT STYLING ========== */
    [data-testid="stMultiSelect"] {
        margin: 12px 0 16px 0 !important;
    }
    
    /* Multiselect input container */
    [data-testid="stMultiSelect"] [data-baseweb="select"] {
        border-radius: 8px !important;
        border: 2px solid #E5E7EB !important;
        background-color: #FAFBFC !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="select"]:hover {
        border-color: #0066FF !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0, 102, 255, 0.1) !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
        border-color: #0066FF !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.12) !important;
        background-color: #FFFFFF !important;
    }
    
    /* Multiselect tags (pills) */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #E8F0FF !important;
        color: #0066FF !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 6px 10px !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0, 102, 255, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="tag"]:hover {
        background-color: #D5E8FF !important;
        box-shadow: 0 2px 6px rgba(0, 102, 255, 0.15) !important;
    }
    
    /* "Tất cả" tag - PRIORITY HIGHLIGHT */
    [data-testid="stMultiSelect"] [data-baseweb="tag"]:first-child {
        background: linear-gradient(135deg, #0066FF, #00A699) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(0, 102, 255, 0.25) !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="tag"]:first-child:hover {
        box-shadow: 0 3px 10px rgba(0, 102, 255, 0.35) !important;
    }
    
    /* Close button trên tag */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        color: #0066FF !important;
    }
    
    [data-testid="stMultiSelect"] [data-baseweb="tag"]:first-child svg {
        color: white !important;
    }
    
    /* ========== RADIO BUTTON STYLING ========== */
    [data-testid="stRadio"] {
        margin: 12px 0 16px 0 !important;
    }
    
    /* Radio group container */
    [data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
    }
    
    /* Radio label wrapper */
    [data-testid="stRadio"] label {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 7px 10px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        color: #555555 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0 !important;
        user-select: none !important;
        background-color: transparent !important;
    }
    
    /* Radio label hover effect */
    [data-testid="stRadio"] label:hover {
        background-color: #E8F0FF !important;
        color: #0066FF !important;
        transform: translateX(2px) !important;
    }
    
    /* Radio button (circle) - main styling */
    [data-testid="stRadio"] [role="radiogroup"] input[type="radio"] {
        accent-color: #0066FF !important;
        width: 18px !important;
        height: 18px !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Radio button checked state */
    [data-testid="stRadio"] [role="radiogroup"] input[type="radio"]:checked {
        box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 3px #0066FF !important;
    }
    
    /* Radio button focus state */
    [data-testid="stRadio"] [role="radiogroup"] input[type="radio"]:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.15) !important;
    }
    
    /* Radio button focus + checked */
    [data-testid="stRadio"] [role="radiogroup"] input[type="radio"]:focus:checked {
        box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 3px #0066FF, 0 0 0 5px rgba(0, 102, 255, 0.15) !important;
    }
    
    /* "Tất cả" option - ONLY highlight when CHECKED */
    [data-testid="stRadio"] label:first-of-type input[type="radio"]:checked {
        accent-color: #00A699 !important;
    }
    
    [data-testid="stRadio"] label:first-of-type input[type="radio"]:checked ~ span {
        color: #00A699 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stRadio"] label:first-of-type input[type="radio"]:checked + span {
        color: #00A699 !important;
        font-weight: 600 !important;
    }


    
    /* ========== DIVIDER / SEPARATOR ========== */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > hr,
    [data-testid="stSidebar"] hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #D5D8DC, transparent) !important;
        margin: 24px 0 !important;
    }
    

    
    /* ========== SUCCESS MESSAGE ========== */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left: 4px solid #52C41A !important;
        background: linear-gradient(135deg, #F6FFED 0%, #F0FFF0 100%) !important;
        padding: 16px 14px !important;
        margin-top: 20px !important;
        box-shadow: 0 2px 8px rgba(82, 196, 26, 0.15) !important;
        animation: slideIn 0.4s ease-out !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #274916 !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        margin-bottom: 0 !important;
        line-height: 1.5 !important;
    }
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    
    /* ========== SECTION STYLING ========== */
    /* Group spacing giữa các section */
    [data-testid="stSidebar"] > div > div {
        margin-bottom: 8px !important;
    }


    
    /* ========== DIVIDER ========== */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #E5E7EB, transparent) !important;
        margin: 20px 0 !important;
    }
    
    /* ========== ALERT & WARNING ========== */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border-left: 4px solid !important;
        box-shadow: var(--shadow-sm) !important;
        animation: slideIn 0.3s ease-out !important;
    }

</style>
<div class="title-center">Tiki Book Market Analytics</div>
""", unsafe_allow_html=True)

# 1. Đọc dữ liệu sách (Từ file clean bạn vừa làm)
@st.cache_data
def load_data():
    # Sử dụng os.path để tạo đường dẫn tuyệt đối ổn định dù chạy từ thư mục nào
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', 'data', 'processed', 'tiki_books_clean.csv')
    df = pd.read_csv(file_path)
    return df

try:
    df = load_data()
    # Xử lý ngôn ngữ bị rỗng thành Vietnamese mặc định
    df['book_language'] = df['book_language'].fillna('Vietnamese')

    # ==========================================
    # CẤU HÌNH SIDEBAR TƯƠNG TÁC (Rubric 3.5: 5% Điểm)
    # ==========================================
    st.sidebar.markdown("")
    st.sidebar.markdown("## ⚙️ Bộ lọc Khám phá")
    st.sidebar.markdown("Dùng bộ lọc này để tùy biến toàn bộ dữ liệu trên Dashboard.")
    
    # 1. Bộ lọc Thể loại (Multiselect)
    all_cats = ['Tất cả'] + df['crawl_category'].unique().tolist()
    selected_cats = st.sidebar.multiselect("📚 Chọn Danh mục sách:", options=all_cats, default=['Tất cả'])
    
    # 2. Bộ lọc Giá bán (Slider)
    min_price = int(df['price'].min())
    max_price = int(df['price'].max())
    price_range = st.sidebar.slider("💰 Khoảng giá bán (VNĐ):", min_value=min_price, max_value=max_price, value=(min_price, max_price), step=50000)
    
    # 3. Bộ lọc Giảm giá (Slider)
    discount_range = st.sidebar.slider("🏷️ Mức chiết khấu (%):", min_value=0, max_value=100, value=(0, 100), step=5)
    
    # 4. Bộ lọc Ngôn ngữ (Radio)
    languages = ['Tất cả'] + df['book_language'].unique().tolist()
    selected_lang = st.sidebar.radio("🌐 Ngôn ngữ xuất bản:", options=languages)
    
    # === ÁP DỤNG LỌC DỮ LIỆU ===
    # Xử lý logic Thể loại: Nếu có tag "Tất cả" thì lấy hết, ngược lại lọc theo list
    cat_condition = df['crawl_category'].isin(df['crawl_category'].unique()) if 'Tất cả' in selected_cats else df['crawl_category'].isin(selected_cats)
    
    filtered_df = df[
        cat_condition &
        (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
        (df['discount_rate'] >= discount_range[0]) & (df['discount_rate'] <= discount_range[1])
    ]
    if selected_lang != 'Tất cả':
        filtered_df = filtered_df[filtered_df['book_language'] == selected_lang]

    # Hiển thị số lượng sp còn lại
    st.sidebar.divider()
    st.sidebar.success(f"✅ Đang hiển thị: **{len(filtered_df):,}** sản phẩm")

    # ==========================================
    # HIỂN THỊ TABS
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 1. Tổng quan", 
        "📈 2. Động lực Doanh số", 
        "📚 3. Đặc điểm Sản phẩm", 
        "👁️ 4. Accessibility"
    ])

    if filtered_df.empty:
        st.warning("Cảnh báo: Không có sản phẩm nào thỏa mãn bộ lọc hiện tại. Vui lòng nới lỏng điều kiện bên thanh Sidebar!")
    else:
        # Gọi hiển thị 3 Tab với biến dữ liệu ĐÃ LỌC (filtered_df)
        with tab1:
            render_tab1(filtered_df)

        with tab2:
            render_tab2(filtered_df)

        with tab3:
            render_tab3(filtered_df)

        with tab4:
            render_tab4(filtered_df)

except Exception as e:
    st.error(f"Lỗi khi đọc file dữ liệu: {e}")
    st.warning("Vui lòng đảm bảo bạn đã chạy xong file 02_preprocessing.ipynb và lưu file tiki_books_clean.csv thành công!")
