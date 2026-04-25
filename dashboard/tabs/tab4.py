import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ======================================================
# BẢNG MÀU CHUẨN COLORBLIND-SAFE (Wong Palette + Viridis)
# ======================================================
# Nguồn: Bang Wong, Nature Methods 8, 441 (2011)
WONG_PALETTE = [
    '#0072B2',  # Blue
    '#E69F00',  # Orange
    '#009E73',  # Bluish Green
    '#CC79A7',  # Reddish Purple
    '#56B4E9',  # Sky Blue
    '#D55E00',  # Vermillion
    '#F0E442',  # Yellow
    '#000000',  # Black
]

# Colorscale liên tục an toàn cho mù màu
CB_CONTINUOUS = 'Cividis'    # Cividis được thiết kế đặc biệt cho colorblind
CB_SEQUENTIAL = 'Viridis'   # Viridis cũng an toàn cho tất cả loại mù màu


def render_tab4(df):
    # Custom styled header
    st.markdown("""
    <style>
        .cb-header {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0072B2;
            padding: 10px 0;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0, 114, 178, 0.15);
        }
        .cb-subheader {
            font-size: 1.8rem !important;
            font-weight: 750 !important;
            color: #009E73 !important;
            margin: 28px auto 12px auto !important;
            padding: 12px 16px !important;
            padding-bottom: 8px !important;
            border-bottom: 3px solid #009E73 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: fit-content !important;
            max-width: 90% !important;
            letter-spacing: -0.3px !important;
            text-align: center !important;
        }
        .cb-description {
            font-size: 1.05rem;
            color: #555555;
            font-style: italic;
            margin: 8px 0 20px 0;
            line-height: 1.6;
            letter-spacing: -0.2px;
        }
        .cb-info-box {
            background: linear-gradient(135deg, #E8F4FD 0%, #F0F7E8 100%);
            border-left: 4px solid #0072B2;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 10px 0 20px 0;
            font-size: 0.92rem;
            color: #333333;
            line-height: 1.5;
        }
    </style>
    <div class="cb-header">👁️ Chế độ Accessibility (Dành cho người mù màu)</div>
    <div class="cb-description">
    ♿ Tab này tái hiện dữ liệu từ Tab 1 bằng bảng màu an toàn cho mọi loại mù màu (Deuteranopia, Protanopia, Tritanopia). 
    Sử dụng <b>Wong Palette</b> + <b>Cividis/Viridis</b> — được khoa học chứng minh phân biệt rõ ràng trên mọi thị lực.
    </div>
    <div class="cb-info-box">
    🔬 <b>Tại sao cần Tab này?</b> Khoảng 8% nam giới và 0.5% nữ giới mắc dạng mù màu. 
    Bảng màu truyền thống (Đỏ-Xanh lá) gần như không thể phân biệt với nhóm Deuteranopia. 
    Tab Accessibility đảm bảo <b>không ai bị bỏ lại phía sau</b> khi đọc dữ liệu.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ==========================================
    # KHỐI 1: KPI CARDS (Giống Tab 1)
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="📚 Tổng số Sách", value=f"{len(df):,}")
    with col2:
        st.metric(label="📈 Tổng Doanh số", value=f"{df['quantity_sold'].sum():,}")
    with col3:
        st.metric(label="💰 Giá trung bình", value=f"{int(df['price'].mean()):,} ₫")
    with col4:
        st.metric(label="⭐ Đánh giá trung bình", value=f"{df['rating_average'].mean():.1f}/5")

    st.markdown("---")

    # ==========================================
    # KHỐI 2: ROW 1 (Treemap & Boxplot - Colorblind Safe)
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        # Biểu đồ 1: Treemap Thị phần doanh số (Cividis scale)
        st.markdown('<div class="cb-subheader">Thị phần Doanh số theo Thể loại</div>', unsafe_allow_html=True)
        df_treemap = df.groupby('crawl_category')['quantity_sold'].sum().reset_index()
        fig1 = px.treemap(
            df_treemap,
            path=['crawl_category'],
            values='quantity_sold',
            color='quantity_sold',
            color_continuous_scale=CB_CONTINUOUS
        )
        fig1.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        fig1.update_traces(
            textfont=dict(size=14, color='white'),
            marker=dict(line=dict(width=2, color='#333333'))  # Viền đậm phân tách rõ ràng
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("🔵 Treemap (Cividis): Diện tích ô = Doanh số. Viền đậm giúp phân biệt các ô kể cả khi không nhận diện được màu.")

    with row1_col2:
        # Biểu đồ 2: Boxplot Phân phối giá (Wong Palette)
        st.markdown('<div class="cb-subheader">Phân phối Giá theo Danh mục</div>', unsafe_allow_html=True)
        df_box = df[df['price'] <= 1_000_000]
        
        categories = df_box['crawl_category'].unique().tolist()
        color_map = {cat: WONG_PALETTE[i % len(WONG_PALETTE)] for i, cat in enumerate(categories)}
        
        fig2 = px.box(
            df_box,
            x='price',
            y='crawl_category',
            color='crawl_category',
            color_discrete_map=color_map,
            labels={'price': 'Giá bán (VNĐ)', 'crawl_category': 'Thể loại'}
        )
        fig2.update_layout(showlegend=False, xaxis_title="Giá bán (VNĐ)", yaxis_title="")
        fig2.update_traces(
            marker=dict(size=4, opacity=0.7),
            line=dict(width=2)  # Đường viền box dày hơn cho dễ đọc
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("🔵 Boxplot (Wong Palette): Mỗi thể loại dùng một màu từ bảng Wong — an toàn cho Deuteranopia & Protanopia.")

    st.markdown("---")

    # ==========================================
    # KHỐI 3: ROW 2 (Top NXB & Donut Chart - Colorblind Safe)
    # ==========================================
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        # Biểu đồ 3: Top 10 NXB (Viridis scale)
        st.markdown('<div class="cb-subheader">Top 10 NXB Uy tín nhất</div>', unsafe_allow_html=True)
        df_nxb = df.dropna(subset=['publisher_name'])
        pub_stats = df_nxb.groupby('publisher_name').agg({
            'product_id': 'count',
            'rating_average': 'median',
            'review_count': 'sum',
            'quantity_sold': 'sum'
        }).reset_index()

        pub_stats = pub_stats[pub_stats['product_id'] >= 10]

        pub_stats['publisher_score'] = (
            pub_stats['rating_average'] *
            np.log1p(pub_stats['review_count']) *
            np.log1p(pub_stats['quantity_sold'])
        )

        top10_nxb = pub_stats.nlargest(10, 'publisher_score').sort_values('publisher_score', ascending=True)

        fig3 = px.bar(
            top10_nxb,
            x='publisher_score',
            y='publisher_name',
            orientation='h',
            text=[f"{x:.1f}" for x in top10_nxb['publisher_score']],
            labels={'publisher_score': 'Điểm uy tín tổng hợp', 'publisher_name': 'Nhà xuất bản'},
            color='publisher_score',
            color_continuous_scale=CB_SEQUENTIAL
        )
        fig3.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=1.5, color='#333333'))  # Viền đen cho thanh bar
        )
        fig3.update_layout(yaxis_title="", margin=dict(l=0, r=0, t=0, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("🔵 Bar Chart (Viridis): Gradient từ tím đậm → vàng sáng. Phân biệt được ngay cả khi in trắng đen.")

    with row2_col2:
        # Biểu đồ 4: Donut Chart Ngôn ngữ (Wong Palette + Pattern)
        st.markdown('<div class="cb-subheader">Sách Tiếng Anh vs Tiếng Việt</div>', unsafe_allow_html=True)
        df['book_language'] = df['book_language'].fillna('Vietnamese')
        df_lang = df.groupby('book_language')['product_id'].count().reset_index()
        df_lang.columns = ['Ngôn ngữ', 'Số lượng']

        # Dùng Wong Blue + Orange (dễ phân biệt nhất cho mù màu)
        cb_lang_colors = {'Vietnamese': '#0072B2', 'English': '#E69F00'}

        fig4 = go.Figure(data=[go.Pie(
            labels=df_lang['Ngôn ngữ'],
            values=df_lang['Số lượng'],
            hole=0.4,
            marker=dict(
                colors=[cb_lang_colors.get(lang, '#56B4E9') for lang in df_lang['Ngôn ngữ']],
                line=dict(color='#333333', width=3)  # Viền đen dày để phân biệt
            ),
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(size=14, color='white'),
            hovertemplate='%{label}: %{value:,} sách (%{percent})<extra></extra>'
        )])
        
        fig4.update_layout(
            showlegend=True,
            legend=dict(
                font=dict(size=13),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#333333',
                borderwidth=1
            ),
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("🔵 Donut Chart (Wong Blue + Orange): Hai màu có độ tương phản cao nhất cho mọi loại mù màu. Viền đen dày hỗ trợ nhận diện.")

    # ==========================================
    # BẢNG THAM CHIẾU MÀU SẮC
    # ==========================================
    st.markdown("---")
    with st.expander("📋 Bảng Tham chiếu Màu sắc Accessibility", expanded=False):
        st.markdown("""
        | Màu | Hex Code | Tên gọi | An toàn cho |
        |:---:|:--------:|:-------:|:-----------:|
        | 🟦 | `#0072B2` | Blue | ✅ Tất cả |
        | 🟧 | `#E69F00` | Orange | ✅ Tất cả |
        | 🟩 | `#009E73` | Bluish Green | ✅ Tất cả |
        | 🟪 | `#CC79A7` | Reddish Purple | ✅ Tất cả |
        | 🔵 | `#56B4E9` | Sky Blue | ✅ Tất cả |
        | 🔴 | `#D55E00` | Vermillion | ✅ Tất cả |
        | 🟡 | `#F0E442` | Yellow | ✅ Tất cả |
        
        **Nguồn**: Bang Wong, *Nature Methods* 8, 441 (2011)  
        **Colorscale liên tục**: Cividis (thiết kế cho colorblind), Viridis (perceptually uniform)
        """)
