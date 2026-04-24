import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def render_tab2(df):
    st.markdown("## 📈 Động lực Doanh số & Hiệu quả Marketing")
    st.markdown("*Đi sâu phân tích hành vi mua sắm: Sự tác động của mức Giảm giá đến Doanh thu và góc độ Chất lượng sản phẩm thực tế.*")
    
    st.divider()

    # ==========================================
    # KHỐI 1: ROW 1 (Ngưỡng Giảm giá & Giá vs Chất lượng)
    # ==========================================
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Mức giảm giá nào thực sự kéo được doanh số mạnh nhất?")
        
        bins = [0, 10, 20, 30, 40, 50, 60, 100]
        labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '>60%']
        df['discount_bin'] = pd.cut(df['discount_rate'], bins=bins, labels=labels, include_lowest=True)
        ridge_df = df[df['discount_bin'].notna()].copy()

        x_limit = min(ridge_df['quantity_sold'].quantile(0.98), ridge_df['quantity_sold'].max())
        x_grid = np.linspace(0, x_limit, 120)

        group_data = []
        for label in labels:
            group = ridge_df[ridge_df['discount_bin'] == label]['quantity_sold']
            if len(group) < 20:
                continue
            counts, edges = np.histogram(group.clip(upper=x_limit), bins=x_grid, density=True)
            smooth_counts = pd.Series(counts).rolling(7, min_periods=1, center=True).mean().to_numpy()
            group_data.append((label, smooth_counts, edges[:-1]))

        if group_data:
            global_max = max(d.max() for _, d, _ in group_data if len(d) > 0)
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            fig = go.Figure()
            for idx, (label, counts, x_vals) in enumerate(group_data):
                offset = idx * 0.9
                densities = counts / global_max * 0.8
                baseline = np.full_like(x_vals, offset)
                top_line = baseline + densities
                color = colors[idx % len(colors)]

                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=baseline,
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=top_line,
                    mode='lines',
                    fill='tonexty',
                    fillcolor=color,
                    line=dict(color='rgba(0,0,0,0.7)', width=1),
                    name=label,
                    hovertemplate='<b>%s</b><br>Doanh số: %%{x:.0f}<br>Mật độ tương đối: %%{y:.3f}<extra></extra>' % label
                ))

            fig.update_layout(
                margin=dict(t=60, l=30, r=20, b=40),
                legend_title_text='Discount',
                hovermode='x',
                yaxis=dict(
                    tickmode='array',
                    tickvals=[i * 0.9 for i in range(len(group_data))],
                    ticktext=[label for label, _, _ in group_data],
                    title='Dải giảm giá (%)'
                ),
                xaxis=dict(title='Doanh số (Số lượng bán)', range=[0, x_limit]),
                plot_bgcolor='#f8f9fb'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Không đủ dữ liệu để hiển thị biểu đồ phần trăm giảm giá.")

        st.caption("Độ tập trung doanh số cao ở discount thấp, còn discount sâu thì phân bổ dài hơn và ít ế hơn.")

    with row1_col2:
        st.subheader("Hàng 'Sale Sốc' có kém chất lượng?")
        
        # LỌC QUAN TRỌNG: Chỉ lấy sách đã có người đánh giá (Tránh nhiễu điểm 0)
        df_rating = df[df['review_count'] > 0].copy()
        
        fig6 = px.scatter(
            df_rating,
            x='discount_rate',
            y='rating_average',
            opacity=0.3, # Làm mờ các điểm để dễ nhìn đường line
            color_discrete_sequence=['#1f77b4'],
            labels={'discount_rate': 'Tỷ lệ Giảm giá (%)', 'rating_average': 'Điểm Đánh giá (Rating)'}
        )

        if len(df_rating) >= 2:
            slope, intercept = np.polyfit(df_rating['discount_rate'], df_rating['rating_average'], 1)
            x_range = np.linspace(df_rating['discount_rate'].min(), df_rating['discount_rate'].max(), 100)
            y_line = slope * x_range + intercept
            fig6.add_trace(
                go.Scatter(
                    x=x_range,
                    y=y_line,
                    mode='lines',
                    line=dict(color='red', dash='dash'),
                    name='Trendline'
                )
            )
            fig6.update_layout(showlegend=False)

        fig6.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig6, use_container_width=True)
        st.caption("Scatter Plot với Đường xu hướng đỏ: Phân tích xem có phải nhà bán thường xuyên xả hàng giảm giá là sản phẩm kém chất lượng (Rating thấp) hay không?")

    st.markdown("---")

    # ==========================================
    # KHỐI 2: ROW 2 (Tương quan & Tiềm năng ẩn)
    # ==========================================
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Ma trận Tương quan Đa biến")
        
        # Tính toán ma trận tương quan Spearman (chống outlier tốt hơn Pearson)
        corr_cols = ['price', 'discount_rate', 'rating_average', 'review_count', 'image_count', 'quantity_sold']
        corr_matrix = df[corr_cols].corr(method='spearman')
        
        # Format tên cột cho đẹp
        corr_matrix.columns = ['Giá', 'Giảm giá', 'Rating', 'Review', 'Số hình ảnh', 'Doanh số']
        corr_matrix.index = corr_matrix.columns
        
        fig7 = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            color_continuous_scale='RdBu_r',  # Red to Blue
            zmin=-1, zmax=1
        )
        fig7.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig7, use_container_width=True)
        st.caption("Heatmap: Cho biết giữa số lượng Review, mức độ Giảm giá và điểm Rating, đâu mới là động lực thúc đẩy Sale mạnh nhất.")

    with row2_col2:
        st.subheader("Truy tìm Sách 'Tiềm Năng Ẩn'")
        
        # Thuật toán tìm Tiềm Năng Ẩn đã được tinh chỉnh
        # Sales rất cao (Top 15%) nhưng Review dưới mức trung bình (Bottom 50%)
        p85_sales = df['quantity_sold'].quantile(0.85)
        p50_review = df['review_count'].median() 
        
        df['is_hidden_gem'] = (df['quantity_sold'] >= p85_sales) & (df['review_count'] <= p50_review)
        
        # Chuyển đổi nhãn để vẽ đẹp
        df['Phân loại'] = df['is_hidden_gem'].map({True: 'Tiềm năng Ads (Sales Cao - Ít Review)', False: 'Nhóm Bình thường'})
        
        # Phóng to kích thước các hạt dữ liệu Tiềm Năng để nó đập vào mắt
        df['Kích thước hạt'] = df['is_hidden_gem'].map({True: 15, False: 4})
        
        fig8 = px.scatter(
            df,
            x='review_count',
            y='quantity_sold',
            color='Phân loại',
            size='Kích thước hạt', # Apply kích thước
            hover_name='name',
            opacity=0.7,
            color_discrete_map={'Tiềm năng Ads (Sales Cao - Ít Review)': 'red', 'Nhóm Bình thường': 'lightgray'},
            labels={'review_count': 'Số lượng Review', 'quantity_sold': 'Doanh số thực tế (Sales)'}
        )
        
        # Giới hạn trục & Thêm Padding (khoảng đệm âm) để số 0 không bị dính vào vách lề trái
        max_x = df['review_count'].quantile(0.95)
        max_y = df['quantity_sold'].quantile(0.95)
        
        # X lùi về mức âm 5% của max_x để tạo khoảng trống
        fig8.update_xaxes(range=[-(max_x * 0.05), max_x])
        fig8.update_yaxes(range=[-(max_y * 0.05), max_y])
        
        fig8.update_layout(margin=dict(t=0, l=0, r=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99))
        st.plotly_chart(fig8, use_container_width=True)
        st.caption("Scatter Plot Highlight: Các chấm đỏ bự là sách có nội lực rất tốt nhưng chưa chạy Marketing. Việc nới trục giúp các sản phẩm 0 review hiển thị rõ ràng.")
