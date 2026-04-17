import streamlit as st
import pandas as pd
from tabs.tab1 import render_tab1
from tabs.tab2 import render_tab2
from tabs.tab3 import render_tab3

# Cấu hình website
st.set_page_config(page_title="Tiki Book Analytics", page_icon="📚", layout="wide")

# Tiêm CSS để ép giao diện nằm giữa và dãn đều Tab
st.markdown("""
<style>
    /* Căn giữa Tiêu đề dự án */
    .title-center {
        text-align: center;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 30px;
    }
    
    /* Ép các Tab (Option) giãn đều ra 100% màn hình, không bị lệch trái */
    button[data-baseweb="tab"] {
        flex: 1 !important; 
        text-align: center !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }

    /* Căn giữa các tiêu đề H2 (Tên của từng Tab) và H3 (Tiêu đề biểu đồ) */
    h2, h3 {
        text-align: center !important;
    }
    
    /* Căn giữa văn bản diễn giải in nghiêng dưới H2 */
    p > em {
        display: block;
        text-align: center !important;
    }
    
    /* Căn giữa toàn bộ khối Số liệu KPI (st.metric) */
    [data-testid="stMetric"] {
        text-align: center !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Căn giữa Label và Value bên trong KPI */
    [data-testid="stMetricLabel"] > div, 
    [data-testid="stMetricValue"] > div {
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }
</style>
<div class="title-center">📚 Tiki Book Market Analytics</div>
""", unsafe_allow_html=True)

# 1. Đọc dữ liệu sách (Từ file clean bạn vừa làm)
@st.cache_data
def load_data():
    # Kiểm tra đường dẫn chính xác (lên 1 cấp thư mục, vào data/processed)
    df = pd.read_csv('../data/processed/tiki_books_clean.csv')
    return df

try:
    df = load_data()
    # Xử lý ngôn ngữ bị rỗng thành Vietnamese mặc định
    df['book_language'] = df['book_language'].fillna('Vietnamese')

    # ==========================================
    # CẤU HÌNH SIDEBAR TƯƠNG TÁC (Rubric 3.5: 5% Điểm)
    # ==========================================
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

except Exception as e:
    st.error(f"Lỗi khi đọc file dữ liệu: {e}")
    st.warning("Vui lòng đảm bảo bạn đã chạy xong file 02_preprocessing.ipynb và lưu file tiki_books_clean.csv thành công!")
