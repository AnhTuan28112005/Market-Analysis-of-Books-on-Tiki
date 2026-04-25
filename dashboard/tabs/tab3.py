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
            font-size: 1.8rem !important;
            font-weight: 750 !important;
            color: #00A699 !important;
            margin: 28px auto 12px auto !important;
            padding: 12px 16px !important;
            padding-bottom: 8px !important;
            border-bottom: 3px solid #00A699 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: fit-content !important;
            max-width: 90% !important;
            letter-spacing: -0.3px !important;
            text-align: center !important;
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
        st.markdown('<div class="custom-subheader">Ngưỡng Bão hòa Hình ảnh Sản phẩm</div>', unsafe_allow_html=True)
        
        # ====== CONTOUR DENSITY PLOT (2D KDE) ======
        import plotly.graph_objects as go
        from scipy.stats import gaussian_kde
        
        # Lọc dữ liệu hợp lệ
        df_contour = df.dropna(subset=['image_count', 'quantity_sold']).copy()
        df_contour = df_contour[(df_contour['quantity_sold'] > 0) & (df_contour['image_count'] > 0)]
        
        # Log-transform doanh số (phân bố lệch phải mạnh)
        df_contour['log_sales'] = np.log1p(df_contour['quantity_sold'])
        
        x_data = df_contour['image_count'].values
        y_data = df_contour['log_sales'].values
        
        # Tính 2D KDE
        try:
            xy = np.vstack([x_data, y_data])
            kde = gaussian_kde(xy, bw_method=0.3)
            
            # Tạo lưới điểm
            x_grid = np.linspace(x_data.min(), min(x_data.max(), 20), 80)
            y_grid = np.linspace(y_data.min(), y_data.max(), 80)
            X, Y = np.meshgrid(x_grid, y_grid)
            positions = np.vstack([X.ravel(), Y.ravel()])
            Z = np.reshape(kde(positions), X.shape)
            
            fig11 = go.Figure()
            
            # Contour heatmap (filled)
            fig11.add_trace(go.Contour(
                x=x_grid,
                y=y_grid,
                z=Z,
                colorscale='Viridis',
                contours=dict(
                    showlabels=False,
                    coloring='heatmap'
                ),
                colorbar=dict(
                    title='Mật độ',
                    titleside='right',
                    titlefont=dict(size=11)
                ),
                hovertemplate='Số ảnh: %{x:.0f}<br>Log Doanh số: %{y:.2f}<br>Mật độ: %{z:.4f}<extra></extra>'
            ))
            
            # Thêm đường xu hướng trung vị theo số lượng ảnh
            trend_data = df_contour.groupby('image_count')['log_sales'].median().reset_index()
            trend_data = trend_data[trend_data['image_count'] <= 20]  # Giới hạn để dễ nhìn
            
            fig11.add_trace(go.Scatter(
                x=trend_data['image_count'],
                y=trend_data['log_sales'],
                mode='lines+markers',
                line=dict(color='#FF4444', width=3, dash='dot'),
                marker=dict(size=7, color='#FF4444', line=dict(width=1.5, color='white')),
                name='Trung vị Doanh số',
                hovertemplate='Số ảnh: %{x:.0f}<br>Doanh số trung vị: %{customdata:.0f}<extra>Trung vị</extra>',
                customdata=np.expm1(trend_data['log_sales'])
            ))
            
            # Chuyển trục y từ log về giá trị thực
            tick_vals_real = [10, 50, 100, 500, 1000, 5000]
            tick_vals_log = [np.log1p(v) for v in tick_vals_real]
            tick_labels = [str(v) for v in tick_vals_real]
            
            fig11.update_layout(
                xaxis=dict(
                    title='Số lượng Hình ảnh (Image Count)',
                    showgrid=False,
                    dtick=2
                ),
                yaxis=dict(
                    title='Doanh số bán (Quantity Sold)',
                    tickvals=tick_vals_log,
                    ticktext=tick_labels,
                    showgrid=False
                ),
                margin=dict(t=10, l=10, r=10, b=10),
                legend=dict(
                    yanchor="top", y=0.99, xanchor="right", x=0.99,
                    bgcolor='rgba(255,255,255,0.85)',
                    bordercolor='#E5E7EB',
                    borderwidth=1
                ),
                height=420
            )
            
            st.plotly_chart(fig11, use_container_width=True)
        except Exception:
            st.info("Không đủ dữ liệu để vẽ Contour Plot.")
        
        st.caption("Contour Density Plot: Vùng sáng (vàng) là nơi tập trung nhiều sản phẩm nhất. Đường đỏ đứt nét chỉ ra trung vị doanh số — khi đường này bắt đầu phẳng, đó là ngưỡng bão hòa hình ảnh.")

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
