# Phân tích thị trường Sách trực tuyến trên Tiki
> Lab 01 — Thu thập dữ liệu và Trực quan hóa dữ liệu bằng Python  
> VNU-HCMUS, Khoa Công nghệ thông tin

---

## Mục tiêu

Phân tích thị trường sách trực tuyến trên sàn Tiki nhằm:
1. Xác định yếu tố ảnh hưởng đến doanh số sách (giá, discount, rating...)
2. Phân tích thị hiếu theo thể loại và Nhà xuất bản

---

## Cấu trúc dự án

```
lab1/
├── data/
│   ├── raw/                    # Dữ liệu thô sau crawl
│   └── processed/              # Dữ liệu đã làm sạch
├── notebooks/
│   ├── 01_crawl_data.py    # Thu thập dữ liệu từ Tiki API
│   ├── EDA_Preprocessed.ipynb  # Tiền xử lý & Feature 
│       
├── dashboard/
│   ├── app.py  
│   └── tabs/          
├── requirements.txt
├── Group 15.pdf
└── README.md
```

---

## Cách chạy

### 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 2. Thu thập dữ liệu

Mở và chạy toàn bộ cells trong:
```
notebooks/01_crawl_data.py
```

### 3. EDA + Tiền xử lý dữ liệu

```
notebooks/EDA_Preprocessed.ipynb
```

### 4. Chạy Dashboard

```bash
streamlit run dashboard/app.py
```

---

## Nguồn dữ liệu

Dữ liệu được thu thập trực tiếp từ **Tiki Public API** tại thời điểm thực hiện đồ án (04/2026).  
Không sử dụng bất kỳ dataset có sẵn nào từ Kaggle hay GitHub.

**Endpoint sử dụng:**
- Listing: `https://tiki.vn/api/personalish/v1/blocks/listings`
- Chi tiết: `https://tiki.vn/api/v2/products/{product_id}`

---

## Thư viện chính

| Mục đích | Thư viện |
|---|---|
| Crawl dữ liệu | `requests`, `tqdm` |
| Xử lý dữ liệu | `pandas`, `numpy` |
| Trực quan hóa | `plotly`, `seaborn`, `matplotlib` |
| Dashboard | `streamlit` |
| Machine Learning | `scikit-learn` |
