import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

@st.cache_data
def get_feature_importance(df):
    """Huấn luyện nhanh mô hình Random Forest để lấy Feature Importance"""
    features = ['price', 'discount_rate', 'rating_average', 'review_count', 'image_count']
    
    # Chuẩn bị dữ liệu sạch cho ML
    df_ml = df.dropna(subset=features + ['quantity_sold', 'cover_type', 'crawl_category']).copy()
    
    # Mã hóa biến phân loại bằng LabelEncoder
    le = LabelEncoder()
    df_ml['cover_enc'] = le.fit_transform(df_ml['cover_type'].astype(str))
    df_ml['cat_enc'] = le.fit_transform(df_ml['crawl_category'].astype(str))
    
    X = df_ml[features + ['cover_enc', 'cat_enc']]
    y = df_ml['quantity_sold']
    
    # Huấn luyện mô hình siêu tốc (50 cây)
    rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    # Xuất kết quả
    fi = pd.DataFrame({
        'Yếu tố (Feature)': ['Giá bán (Price)', 'Chiết khấu (Discount)', 'Điểm Đánh giá (Rating)', 
                             'Số lượt đánh giá (Review)', 'Số lượng Hình ảnh', 'Loại Bìa', 'Danh mục'],
        'Độ quan trọng (%)': rf.feature_importances_ * 100
    }).sort_values(by='Độ quan trọng (%)', ascending=True)
    
    return fi

def render_tab3(df):
    # Custom styled header
    st.markdown("""
    <style>
        .custom-header {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0066FF;
            padding: 10px 0;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0, 102, 255, 0.15);
        }
        .custom-subheader {
            font-size: 1.8rem;
            font-weight: 750;
            color: #00A699;
            margin: 28px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 3px solid #00A699;
            display: inline-block;
            letter-spacing: -0.3px;
        }
        .kpi-description {
            font-size: 1.05rem;
            color: #555555;
            font-style: italic;
            margin: 8px 0 20px 0;
            line-height: 1.6;
            letter-spacing: -0.2px;
        }
    </style>
    <div class="custom-header">📚 Đặc điểm Sản phẩm & Hệ sinh thái Người bán</div>
    <div class="kpi-description">
    🏢 Phân tích đặc điểm vật lý (Bìa, Hình ảnh chất lượng) cùng cuộc chiến giữa đại lý chính hãng (Tiki Trading) và nhà bán hàng bên thứ 3 (Merchant).
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # ==========================================
    # KHỐI 1: TIKI TRADING VS MERCHANT & BÌA SÁCH
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown('<div class="custom-subheader">Sức mạnh: Tiki Trading vs Merchant</div>', unsafe_allow_html=True)
        # Phân loại seller
        df['seller_group'] = df['seller_name'].apply(lambda x: 'Tiki Trading' if str(x).strip().lower() == 'tiki trading' else 'Merchant')
        
        # Chọn ra 5 chỉ số đếm sức mạnh
        metrics = ['quantity_sold', 'discount_rate', 'rating_average', 'review_count', 'image_count']
        seller_stats = df.groupby('seller_group')[metrics].mean()
        
        # Chuẩn hóa Min-Max Scale về thang điểm 100 (Bên nào to nhất thì lấy mốc 100, bên kia tỷ lệ theo)
        for col in metrics:
            max_val = seller_stats[col].max()
            seller_stats[col] = (seller_stats[col] / max_val) * 100 if max_val > 0 else 0
            
        # Xử lý Melt ép dọc dữ liệu để vẽ Radar Plot
        df_radar = seller_stats.reset_index().melt(id_vars='seller_group', var_name='Chỉ số', value_name='Điểm sức mạnh')
        
        # Chuyển đổi tên trục tiếng Anh sang Tiếng Việt cho sinh động
        metric_names = {
            'quantity_sold': 'Thực lực Doanh số', 
            'discount_rate': 'Độ bạo chi (Giảm giá)', 
            'rating_average': 'Chất lượng (Rating)', 
            'review_count': 'Sức hút (Review)', 
            'image_count': 'Đầu tư Hình ảnh'
        }
        df_radar['Chỉ số'] = df_radar['Chỉ số'].map(metric_names)
        
        # Vẽ biểu đồ lưới Radar
        fig9 = px.line_polar(
            df_radar, 
            r='Điểm sức mạnh', 
            theta='Chỉ số', 
            color='seller_group', 
            line_close=True,
            color_discrete_map={'Tiki Trading': '#1f77b4', 'Merchant': '#ff7f0e'},
            labels={'seller_group': 'Thực thể bán hàng'}
        )
        fig9.update_traces(fill='toself', opacity=0.6) # Đổ màu nửa trong suốt giống UI game
        fig9.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])), 
            margin=dict(t=30, l=30, r=30, b=30)
        )
        st.plotly_chart(fig9, use_container_width=True)
        st.caption("Biểu đồ Mạng nhện (Radar Chart): Trực quan hóa 5 'Hệ số sức mạnh' từ trung bình thang 100. Chứng minh liệu Tiki Trading có thực sự áo đảo dân thường ở mọi mặt trận?")

    with row1_col2:
        st.markdown('<div class="custom-subheader">Thị hiếu Bìa Sách: Cứng vs Mềm</div>', unsafe_allow_html=True)
        # Chuẩn hóa tên loại bìa cho gọn
        df['cover_clean'] = df['cover_type'].astype(str).str.lower()
        def clean_cover(c):
            if 'cứng' in c: return 'Bìa cứng'
            if 'mềm' in c: return 'Bìa mềm'
            return 'Loại Bìa Khác'
        
        df['cover_group'] = df['cover_clean'].apply(clean_cover)
        
        # Vẽ violin plot kết hợp box
        fig10 = px.violin(
            df[df['cover_group'] != 'Loại Bìa Khác'], # Chỉ so Cứng và Mềm
            x='cover_group',
            y='price',
            color='cover_group',
            box=True, # Hiển thị boxplot bên trong
            points="all", # Hiển thị các chấm dữ liệu
            color_discrete_sequence=['#ff7f0e', '#2ca02c'],
            labels={'cover_group': 'Loại Bìa', 'price': 'Giá bán (VNĐ)'}
        )
        fig10.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig10, use_container_width=True)
        st.caption("Violin Plot: Thể hiện độ chênh lệch giá và sự phân tán giá giữa việc xuất bản sách bìa cứng nâng cao chất lượng và sách bìa mềm.")

    st.markdown("---")

    # ==========================================
    # KHỐI 2: HÌNH ẢNH MÔ TẢ & MACHINE LEARNING
    # ==========================================
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown('<div class="custom-subheader">Giá trị của việc đầu tư Hình ảnh</div>', unsafe_allow_html=True)
        
        # 1. Gom nhóm (Binning) lượng hình ảnh thành các bậc trải nghiệm
        def group_image(x):
            if x <= 1: return '1 ảnh (Cơ bản)'
            elif x <= 3: return '2-3 ảnh (Đầy đủ)'
            elif x <= 5: return '4-5 ảnh (Chi tiết)'
            else: return '6+ ảnh (Chuyên nghiệp)'
            
        df['image_group'] = df['image_count'].apply(group_image)
        
        # Đảm bảo thứ tự hiển thị đúng logic từ ít đến nhiều
        order = ['1 ảnh (Cơ bản)', '2-3 ảnh (Đầy đủ)', '4-5 ảnh (Chi tiết)', '6+ ảnh (Chuyên nghiệp)']
        
        # 2. Tính toán Doanh số trung vị
        img_stats = df.groupby('image_group')['quantity_sold'].median().reset_index()
        img_stats['image_group'] = pd.Categorical(img_stats['image_group'], categories=order, ordered=True)
        img_stats = img_stats.sort_values('image_group')
        
        # Chuẩn bị danh sách màu: Cột "2-3 ảnh" màu xanh đậm nổi bật, các cột còn lại xanh nhạt đồng đều
        img_stats['Màu nổi bật'] = img_stats['image_group'].apply(
            lambda x: '#113b7a' if '2-3 ảnh' in str(x) else '#7cb3d6'
        )
        
        # 3. Vẽ biểu đồ Bar Chart
        fig11 = px.bar(
            img_stats,
            x='image_group',
            y='quantity_sold',
            text_auto=True, # Hiển thị thẳng con số lên cột
            color='Màu nổi bật',
            color_discrete_map="identity", # Ép Plotly đọc mã HEX trực tiếp
            labels={'image_group': 'Mức độ đầu tư Hình ảnh', 'quantity_sold': 'Doanh số Trung vị'}
        )
        fig11.update_traces(textposition='outside')
        fig11.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig11, use_container_width=True)
        st.caption("Biểu đồ Cột (Binning): Trả lời chính xác câu hỏi 'Nếu tôi bổ sung thêm hình ảnh, doanh số chốt đơn sẽ tăng trưởng bao nhiêu %?'")

    with row2_col2:
        st.markdown('<div class="custom-subheader">Trí tuệ Nhân tạo: Yếu tố Quyết định Doanh số</div>', unsafe_allow_html=True)
        # Chạy hàm ML đã build sẵn
        fi_df = get_feature_importance(df)
        
        fig12 = px.bar(
            fi_df,
            x='Độ quan trọng (%)',
            y='Yếu tố (Feature)',
            orientation='h',
            text_auto='.1f',
            color='Độ quan trọng (%)',
            color_continuous_scale='Magma'
        )
        fig12.update_layout(yaxis_title="", margin=dict(t=0, l=0, r=0, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig12, use_container_width=True)
        st.caption("Kết quả chạy trực tiếp mô hình **RandomForest Regressor**. Chứng minh toán học yếu tố nào thao túng hành vi mua hàng mạnh nhất.")
