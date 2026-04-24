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
    st.markdown("## 📚 Đặc điểm Sản phẩm & Hệ sinh thái Người bán")
    st.markdown("*Phân tích đặc điểm vật lý (Bìa, Hình ảnh chất lượng) cùng cuộc chiến giữa đại lý chính hãng (Tiki Trading) và nhà bán hàng bên thứ 3 (Merchant).*")
    
    st.divider()

    # ==========================================
    # KHỐI 1: TIKI TRADING VS MERCHANT & BÌA SÁCH
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Sức mạnh: Tiki Trading vs Merchant")
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
        st.subheader("Thị hiếu Bìa Sách: Cứng vs Mềm")
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
        st.subheader("Tương quan Hình ảnh và Doanh số theo Loại người bán")
        
        # 1. Nhóm số lượng ảnh 
        bins = [0, 1, 3, 5, 100]
        labels = ['1 ảnh', '2-3 ảnh', '4-5 ảnh', '6+ ảnh']
        df['image_grp'] = pd.cut(df['image_count'], bins=bins, labels=labels)
        
        # 2. Tạo bảng phân tích chéo, tính trung vị doanh số
        heatmap_data = df.pivot_table(
            index='seller_type', 
            columns='image_grp', 
            values='quantity_sold', 
            aggfunc='median'
        ).fillna(0)
        
        # 3. Vẽ Heatmap bằng Plotly
        fig = px.imshow(
            heatmap_data,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='Viridis',
            labels=dict(x="Số lượng ảnh", y="Loại người bán", color="Doanh số trung vị")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Heatmap: Việc đầu tư nhiều hình ảnh có mang lại hiệu ứng tăng doanh số đồng đều giữa Tiki Trading và Merchant không?")

    with row2_col2:
        st.subheader("Trí tuệ Nhân tạo: Yếu tố Quyết định Doanh số")
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
