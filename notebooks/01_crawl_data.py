# %% [markdown]
# # Bước 1: Thu thập dữ liệu Sách từ Tiki API
# 
# **Mục tiêu:** Thu thập tối thiểu 5.000 sản phẩm sách từ các danh mục khác nhau trên Tiki
# thông qua Public API (không cần đăng nhập).
#
# **Chiến lược 2 bước:**
# - Bước A: Lấy danh sách `product_id` từ API danh mục
# - Bước B: Lấy thông tin chi tiết từng sản phẩm qua API detail
#
# **Thư viện sử dụng:** `requests`, `pandas`, `time`, `json`, `tqdm`

# %% [markdown]
# ## 0. Import thư viện

# %%
import requests
import pandas as pd
import numpy as np
import time
import json
import os
import random
from datetime import datetime
from tqdm import tqdm  # pip install tqdm nếu chưa có

# Tắt cảnh báo SSL không cần thiết
import warnings
warnings.filterwarnings("ignore")

print("✅ Import thư viện thành công")
print(f"📅 Thời điểm bắt đầu crawl: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# %% [markdown]
# ## 1. Cấu hình chung

# %%
# =====================================================================
# CẤU HÌNH CRAWL
# =====================================================================

# Đường dẫn lưu file (tính từ thư mục lab1 - nơi chạy script)
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent  # lab1/
RAW_DATA_PATH = str(BASE_DIR / "data" / "raw" / "tiki_books_raw.csv")
CHECKPOINT_PATH = str(BASE_DIR / "data" / "raw" / "product_ids_checkpoint.json")

# Headers giả lập trình duyệt thật - giúp tránh bị block
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://tiki.vn/",
    "Origin": "https://tiki.vn",
    "Connection": "keep-alive",
}

# Delay giữa các request (giây) - để không bị block IP
DELAY_BETWEEN_REQUESTS = (0.5, 1.5)  # Random trong khoảng này
DELAY_BETWEEN_CATEGORIES = (2, 4)

# Số trang tối đa mỗi danh mục khi lấy ID
MAX_PAGES_PER_CATEGORY = 50  # 40 sản phẩm/trang × 50 trang = 2.000 ID/danh mục

# =====================================================================
# DANH MỤC SÁCH TRÊN TIKI - ID cập nhật 2024
# Lấy từ URL khi duyệt tiki.vn (phần c{ID} trong URL)
# =====================================================================
BOOK_CATEGORIES = {
    # === SÁCH TIẾNG VIỆT ===
    "Sách Văn Học":              839,
    "Sách Kinh Tế":              833,
    "Sách Tâm Lý - Kỹ Năng":   868,
    "Sách Thiếu Nhi":            850,
    "Manga - Truyện Tranh":      1084,
    "Sách Giáo Khoa - Tham Khảo": 873,

    # === ENGLISH BOOKS ===
    "English - Fiction":          110,
    "English - Business & Economics": 111,
    "English - Children's Books": 112,
    "English - Self-Help":        113,
}

# Dùng để tự động xác định ngôn ngữ của từng danh mục
ENGLISH_CATEGORIES = {"English - Fiction", "English - Business & Economics",
                       "English - Children's Books", "English - Self-Help"}

print(f"\nÔ Số danh mục sẽ crawl: {len(BOOK_CATEGORIES)}")
vi_cats  = [n for n in BOOK_CATEGORIES if n not in ENGLISH_CATEGORIES]
eng_cats = [n for n in BOOK_CATEGORIES if n in ENGLISH_CATEGORIES]
print(f"   Sách Tiếng Việt ({len(vi_cats)} danh mục): {vi_cats}")
print(f"   English Books  ({len(eng_cats)} danh mục): {eng_cats}")
print(f"   Ước tính ID: {len(BOOK_CATEGORIES)} x {MAX_PAGES_PER_CATEGORY} trang x 40 sp = {len(BOOK_CATEGORIES)*MAX_PAGES_PER_CATEGORY*40:,} IDs")

# %% [markdown]
# ## 2. Các hàm tiện ích

# %%
def safe_get(url: str, params: dict = None, retries: int = 3) -> dict | None:
    """
    Gọi GET request an toàn với cơ chế retry.
    
    Args:
        url: URL cần gọi
        params: Dict các tham số query string
        retries: Số lần thử lại nếu thất bại
    
    Returns:
        Dict JSON hoặc None nếu thất bại
    """
    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=15,
                verify=True
            )
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                # Rate limit - chờ lâu hơn
                wait_time = 10 + attempt * 5
                print(f"   ⚠️  Rate limit (429). Chờ {wait_time}s...")
                time.sleep(wait_time)
            elif resp.status_code in [403, 404]:
                return None  # Không retry nếu bị từ chối hoặc không tồn tại
            else:
                print(f"   ⚠️  HTTP {resp.status_code} - Thử lại ({attempt+1}/{retries})")
                time.sleep(2 ** attempt)
        except requests.exceptions.Timeout:
            print(f"   ⏳ Timeout - Thử lại ({attempt+1}/{retries})")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error - Thử lại ({attempt+1}/{retries})")
            time.sleep(3)
        except Exception as e:
            print(f"   ❌ Lỗi không mong đợi: {e}")
            return None
    return None


def random_delay(delay_range: tuple = None):
    """Tạo delay ngẫu nhiên để tránh bị phát hiện là bot."""
    if delay_range is None:
        delay_range = DELAY_BETWEEN_REQUESTS  # Lấy từ biến toàn cục khi gọi hàm
    delay = random.uniform(*delay_range)
    time.sleep(delay)


print("✅ Định nghĩa hàm tiện ích thành công")

# %% [markdown]
# ## 3. Bước A — Thu thập danh sách Product ID theo danh mục

# %%
def get_product_ids_from_category(category_id: int, category_name: str, max_pages: int = None) -> list[int]:
    """
    Lấy tất cả product_id từ một danh mục sách trên Tiki.
    Tự động chọn urlKey phù hợp cho sách Tiếng Việt và Tiếng Anh.
    """
    BASE_URL = "https://tiki.vn/api/personalish/v1/blocks/listings"

    if max_pages is None:
        max_pages = MAX_PAGES_PER_CATEGORY

    # Tự động chọn urlKey theo ngôn ngữ danh mục
    is_english = category_name in ENGLISH_CATEGORIES
    url_key    = "english-books" if is_english else "nha-sach-tiki"
    lang_label = "🇬🇧 English" if is_english else "🇻🇳 Tiếng Việt"

    all_ids = []
    print(f"\n📂 [{lang_label}] {category_name} (ID={category_id}, urlKey={url_key})")

    for page in range(1, max_pages + 1):
        params = {
            "limit":        40,
            "include":      "advertisement",
            "aggregations": 2,
            "category":     category_id,
            "page":         page,
            "urlKey":       url_key,
        }

        data = safe_get(BASE_URL, params=params)

        if data is None:
            print(f"   ⚠️  Không lấy được trang {page}. Dừng danh mục này.")
            break

        items = data.get("data", [])

        if not items:
            print(f"   ✅ Hết sản phẩm tại trang {page}. Tổng: {len(all_ids)} ID")
            break

        page_ids = [item["id"] for item in items if "id" in item]
        all_ids.extend(page_ids)
        print(f"   📄 Trang {page:02d}: +{len(page_ids)} IDs → Tổng: {len(all_ids)}")

        random_delay(DELAY_BETWEEN_REQUESTS)

    unique_ids = list(set(all_ids))
    print(f"   🔹 Sau lọc trùng: {len(unique_ids)} IDs (bỏ {len(all_ids)-len(unique_ids)} trùng)")
    return unique_ids


# %%
# Chạy thu thập ID từ tất cả danh mục
# Nếu đã có checkpoint, tiếp tục từ chỗ dừng

os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)

all_product_ids = {}  # {category_name: [product_ids]}

if os.path.exists(CHECKPOINT_PATH):
    print(f"📂 Tìm thấy checkpoint tại {CHECKPOINT_PATH}")
    print("   → Load lại danh sách ID đã thu thập trước đó...")
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        all_product_ids = json.load(f)
    total_loaded = sum(len(v) for v in all_product_ids.values())
    print(f"✅ Đã load {total_loaded} product IDs từ {len(all_product_ids)} danh mục")
else:
    print("🚀 Bắt đầu thu thập product IDs từ các danh mục...")

# Chỉ crawl những danh mục chưa có trong checkpoint
remaining_categories = {k: v for k, v in BOOK_CATEGORIES.items() if k not in all_product_ids}
print(f"📋 Danh mục cần crawl: {list(remaining_categories.keys())}")

for cat_name, cat_id in remaining_categories.items():
    ids = get_product_ids_from_category(cat_id, cat_name)
    all_product_ids[cat_name] = ids
    
    # Lưu checkpoint ngay sau mỗi danh mục
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_product_ids, f, ensure_ascii=False)
    print(f"   💾 Checkpoint đã lưu: {sum(len(v) for v in all_product_ids.values())} IDs tổng cộng")
    
    random_delay(DELAY_BETWEEN_CATEGORIES)

print("\n" + "="*60)
print("📊 TỔNG KẾT THU THẬP ID:")
total_ids = 0
for cat_name, ids in all_product_ids.items():
    print(f"   {cat_name}: {len(ids)} IDs")
    total_ids += len(ids)
print(f"   ──────────────────────")
print(f"   TỔNG CỘNG: {total_ids} product IDs")
print(f"   💾 Checkpoint lưu tại: {CHECKPOINT_PATH}")

# %% [markdown]
# ## 4. Bước B — Thu thập chi tiết từng sản phẩm

# %%
def extract_product_detail(data: dict, category_name: str) -> dict | None:
    """
    Trích xuất các trường cần thiết từ JSON chi tiết sản phẩm Tiki.
    Phiên bản v2: fallback đa cấp cho author_name và publisher_name
    vì cấu trúc JSON Tiki API đã thay đổi.

    Fallback author_name  : top-level → data['authors'] list → specifications
    Fallback publisher_name: top-level → specifications (nhiều code)
    """
    if not data or "id" not in data:
        return None

    try:
        # ── Thông tin cơ bản ─────────────────────────────────────────
        product_id = data.get("id")
        name       = data.get("name", "").strip()

        # ── Giá ──────────────────────────────────────────────────────
        price         = data.get("price", 0)
        list_price    = data.get("list_price", price)
        discount_rate = data.get("discount_rate", 0)
        if discount_rate == 0 and list_price > 0 and price < list_price:
            discount_rate = round((1 - price / list_price) * 100, 1)

        # ── Đánh giá ─────────────────────────────────────────────────
        rating_average = data.get("rating_average", 0)
        review_count   = data.get("review_count", 0)

        # ── Doanh số ─────────────────────────────────────────────────
        qty_sold_obj  = data.get("quantity_sold", {})
        quantity_sold = (
            qty_sold_obj.get("value", 0) if isinstance(qty_sold_obj, dict)
            else int(qty_sold_obj) if isinstance(qty_sold_obj, (int, float))
            else 0
        )

        # all_time_quantity_sold (tổng doanh số lịch sử)
        all_time_obj  = data.get("all_time_quantity_sold", {})
        all_time_sold = (
            all_time_obj.get("value", 0) if isinstance(all_time_obj, dict)
            else int(all_time_obj) if isinstance(all_time_obj, (int, float))
            else 0
        )
        if all_time_sold == 0:
            all_time_sold = quantity_sold

        # ── Người bán (Seller) ────────────────────────────────────────
        seller_obj  = data.get("current_seller", {}) or {}
        seller_name = seller_obj.get("name", "")
        is_tiki_now = seller_obj.get("is_tiki_now", False)
        seller_type = "Tiki Trading" if ("tiki" in seller_name.lower()
                                          or is_tiki_now) else "Merchant"

        # ── Specifications helper ─────────────────────────────────────
        specs = data.get("specifications", [])

        def get_spec(codes: list) -> str:
            """Tìm giá trị attribute trong specifications theo danh sách code."""
            for spec_group in specs:
                for attr in spec_group.get("attributes", []):
                    if attr.get("code") in codes:
                        val = str(attr.get("value", "")).strip()
                        if val:
                            return val
            return ""

        # ── TÁC GIẢ — Fallback 3 cấp ────────────────────────────────
        # Cấp 1: Trường ngoài cùng (cấu trúc cũ)
        author_name = data.get("author_name") or ""

        # Cấp 2: Trong list authors (cấu trúc mới Tiki API)
        if not author_name:
            authors = data.get("authors", [])
            if isinstance(authors, list) and len(authors) > 0:
                names = [a.get("name", "") for a in authors if a.get("name")]
                author_name = ", ".join(names) if names else ""

        # Cấp 3: Trong specifications
        if not author_name:
            author_name = get_spec(["author", "tac_gia", "tac-gia",
                                    "author_name", "manufacturer"])

        author_name = author_name if author_name else "Nhiều tác giả"

        # ── NHÀ XUẤT BẢN — Fallback 2 cấp ───────────────────────────
        # Cấp 1: Trường ngoài cùng
        publisher_name = data.get("publisher_name") or ""

        # Cấp 2: Trong specifications (nhiều code khả năng)
        if not publisher_name:
            publisher_name = get_spec(["publisher", "nha_xuat_ban", "brand",
                                       "publisher_vn", "nha-xuat-ban",
                                       "nxb", "publishing_house"])

        publisher_name = publisher_name if publisher_name else "Đang cập nhật"

        # ── Thông tin vật lý sách ────────────────────────────────────
        cover_type    = get_spec(["cover_type", "loai_bia", "book_cover",
                                  "loai-bia", "bia"])
        num_pages_str = get_spec(["number_of_pages", "so_trang", "pages",
                                  "so-trang", "page_count"])
        pub_date      = get_spec(["date_publication", "publication_date",
                                  "ngay_xuat_ban", "ngay-xuat-ban"])

        try:
            num_pages = int("".join(filter(str.isdigit, num_pages_str))) if num_pages_str else 0
        except Exception:
            num_pages = 0

        # ── Hình ảnh ─────────────────────────────────────────────────
        images      = data.get("images", [])
        image_count = len(images) if isinstance(images, list) else 0
        thumbnail   = data.get("thumbnail_url", "")

        # ── Mô tả (dùng cho Word Cloud) ───────────────────────────────
        short_description = (data.get("short_description") or "").strip()[:500]

        # ── Thể loại ─────────────────────────────────────────────────
        breadcrumbs     = data.get("breadcrumbs", [])
        actual_category = (breadcrumbs[-2].get("name", category_name)
                           if breadcrumbs and len(breadcrumbs) >= 2
                           else category_name)

        # ── Tình trạng kho & URL ──────────────────────────────────────
        inventory_status = data.get("inventory_status", "unknown")
        url_path         = data.get("url_path", "")
        product_url      = f"https://tiki.vn/{url_path}" if url_path else ""

        return {
            "product_id":        product_id,
            "name":              name,
            "price":             price,
            "list_price":        list_price,
            "discount_rate":     discount_rate,
            "rating_average":    rating_average,
            "review_count":      review_count,
            "quantity_sold":     quantity_sold,
            "all_time_sold":     all_time_sold,
            "seller_name":       seller_name,
            "seller_type":       seller_type,
            "author_name":       author_name,
            "publisher_name":    publisher_name,
            "cover_type":        cover_type,
            "num_pages":         num_pages,
            "pub_date":          pub_date,
            "image_count":       image_count,
            "thumbnail_url":     thumbnail,
            "short_description": short_description,
            "category_name":     actual_category,
            "crawl_category":    category_name,
            "book_language":     "English" if category_name in ENGLISH_CATEGORIES else "Vietnamese",
            "inventory_status":  inventory_status,
            "product_url":       product_url,
            "crawl_time":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        print(f"   ⚠️  Lỗi parse sản phẩm {data.get('id', '?')}: {e}")
        return None



def crawl_product_detail(product_id: int, category_name: str) -> dict | None:
    """Gọi API Tiki để lấy chi tiết một sản phẩm."""
    url  = f"https://tiki.vn/api/v2/products/{product_id}"
    data = safe_get(url)
    if data is None:
        return None
    return extract_product_detail(data, category_name)


print("✅ Định nghĩa hàm crawl chi tiết thành công (v2 — fallback đa cấp)")
print("   author_name    : top-level → authors list → specifications")
print("   publisher_name : top-level → specifications (7 code khả năng)")

# %% [markdown]
# ## 4b. TEST — Kiểm tra 5 sản phẩm trước khi crawl toàn bộ

# %%
# =====================================================================
# TEST NHANH: Lấy 5 sản phẩm đầu tiên từ checkpoint để xác nhận
# author_name và publisher_name đã có dữ liệu thực sự.
# Chỉ chạy cell này SAU khi đã load all_product_ids từ checkpoint.
# =====================================================================

test_pairs = []
for cat_name, ids in all_product_ids.items():
    for pid in ids[:5]:
        test_pairs.append((pid, cat_name))
    if len(test_pairs) >= 5:
        break

print(f"🧪 TEST với {len(test_pairs)} sản phẩm đầu tiên...\n")

test_results = []
for pid, cat in test_pairs:
    url  = f"https://tiki.vn/api/v2/products/{pid}"
    raw  = safe_get(url)
    if raw:
        record = extract_product_detail(raw, cat)
        if record:
            test_results.append(record)
            print(f"  ID {pid}:")
            print(f"    name           : {record['name'][:55]}")
            print(f"    author_name    : {record['author_name']}")
            print(f"    publisher_name : {record['publisher_name']}")
            print(f"    cover_type     : {record['cover_type'] or '(trống)'}")
            print()
    time.sleep(1)

print("=" * 60)
print("📊 Tổng kết TEST:")
df_test = pd.DataFrame(test_results)
if not df_test.empty:
    n_author_missing    = df_test['author_name'].eq('Nhiều tác giả').sum()
    n_pub_missing       = df_test['publisher_name'].eq('Đang cập nhật').sum()
    print(f"  author_name    placeholder : {n_author_missing}/{len(df_test)}")
    print(f"  publisher_name placeholder : {n_pub_missing}/{len(df_test)}")
    if n_author_missing < len(df_test) or n_pub_missing < len(df_test):
        print("\n✅ Hàm hoạt động đúng — có dữ liệu thực! Tiếp tục crawl toàn bộ.")
    else:
        print("\n⚠️  Vẫn còn nhiều placeholder — gửi output này để debug thêm.")

# %%
# Tạo danh sách tất cả (product_id, category_name) để crawl chi tiết
all_pairs = []
for cat_name, ids in all_product_ids.items():
    for pid in ids:
        all_pairs.append((pid, cat_name))

# Xáo trộn để không crawl tuần tự cùng danh mục (giảm nguy cơ bị block)
random.shuffle(all_pairs)

print(f"📋 Tổng số sản phẩm cần crawl chi tiết: {len(all_pairs)}")

# Kiểm tra xem đã có dữ liệu chưa (tiếp tục nếu bị gián đoạn)
existing_records = []
crawled_ids = set()

if os.path.exists(RAW_DATA_PATH):
    df_existing = pd.read_csv(RAW_DATA_PATH, encoding="utf-8-sig")
    existing_records = df_existing.to_dict("records")
    crawled_ids = set(df_existing["product_id"].astype(int).tolist())
    print(f"📂 Tìm thấy {len(crawled_ids)} sản phẩm đã crawl trước đó → Bỏ qua và tiếp tục")
else:
    print("🆕 Bắt đầu crawl mới từ đầu")

# Lọc ra những ID chưa crawl
remaining_pairs = [(pid, cat) for pid, cat in all_pairs if pid not in crawled_ids]
print(f"🔄 Số sản phẩm còn lại cần crawl: {len(remaining_pairs)}")

# %% [markdown]
# ## 5. Vòng lặp crawl chính

# %%
# =====================================================================
# VÒNG LẶP CRAWL CHI TIẾT SẢN PHẨM
# =====================================================================
SAVE_EVERY = 100  # Lưu file mỗi N sản phẩm

successful = 0
failed = 0
records = list(existing_records)  # Bắt đầu từ dữ liệu đã có

print(f"\n🚀 Bắt đầu crawl chi tiết {len(remaining_pairs)} sản phẩm...")
print(f"   Lưu checkpoint mỗi {SAVE_EVERY} sản phẩm")
print("="*60)

for i, (product_id, category_name) in enumerate(tqdm(remaining_pairs, desc="Crawling")):
    
    detail = crawl_product_detail(product_id, category_name)
    
    if detail is not None:
        records.append(detail)
        successful += 1
    else:
        failed += 1
    
    # Lưu file mỗi SAVE_EVERY sản phẩm
    if (i + 1) % SAVE_EVERY == 0:
        df_temp = pd.DataFrame(records)
        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        df_temp.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8-sig")
        tqdm.write(f"   💾 [{i+1}/{len(remaining_pairs)}] Đã lưu {len(records)} bản ghi | Thành công: {successful} | Thất bại: {failed}")
    
    # Delay ngẫu nhiên
    random_delay(DELAY_BETWEEN_REQUESTS)

# Lưu lần cuối
df_raw = pd.DataFrame(records)
os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
df_raw.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8-sig")

print("\n" + "="*60)
print("🎉 CRAWL HOÀN TẤT!")
print(f"   ✅ Thành công:  {successful} sản phẩm")
print(f"   ❌ Thất bại:    {failed} sản phẩm")
print(f"   📊 Tổng bản ghi: {len(df_raw)}")
print(f"   💾 Đã lưu tại:  {RAW_DATA_PATH}")

# %% [markdown]
# ## 6. Kiểm tra sơ bộ dữ liệu thô

# %%
# Load lại file vừa lưu để kiểm tra
df_raw = pd.read_csv(RAW_DATA_PATH, encoding="utf-8-sig")

print("=" * 60)
print("📊 TỔNG QUAN DỮ LIỆU THÔ:")
print("=" * 60)
print(f"  Số hàng:    {df_raw.shape[0]:,}")
print(f"  Số cột:     {df_raw.shape[1]}")
print(f"  Các cột:    {list(df_raw.columns)}")

# %%
print("\n📋 5 dòng đầu:")
df_raw.head()

# %%
print("\n📋 Thông tin kiểu dữ liệu:")
df_raw.info()

# %%
print("\n📋 Thống kê mô tả các cột số:")
df_raw.describe()

# %%
print("\n📋 Số lượng sản phẩm theo danh mục:")
df_raw["crawl_category"].value_counts()

# %%
print("\n📋 Tỷ lệ giá trị thiếu:")
missing = df_raw.isnull().sum()
missing_pct = (missing / len(df_raw) * 100).round(2)
pd.DataFrame({"Thiếu": missing, "Tỷ lệ (%)": missing_pct})[missing > 0]

# %%
# Kiểm tra đủ 5000 dòng chưa
target_rows = 5000
current_rows = len(df_raw)

if current_rows >= target_rows:
    print(f"\n✅ ĐẠT YÊU CẦU: {current_rows:,} dòng ≥ {target_rows:,} dòng yêu cầu")
else:
    deficit = target_rows - current_rows
    print(f"\n⚠️  CHƯA ĐỦ: {current_rows:,} dòng. Cần thêm {deficit:,} dòng nữa.")
    print("   → Hãy thêm danh mục hoặc tăng MAX_PAGES_PER_CATEGORY và chạy lại")

# %%
print("\n✅ Bước 1 (Thu thập dữ liệu) hoàn thành!")
print(f"📁 File thô lưu tại: {RAW_DATA_PATH}")
print("→ Chuyển sang Notebook 02_preprocessing.ipynb để làm sạch dữ liệu")
