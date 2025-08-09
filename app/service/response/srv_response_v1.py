# ruff : noqa
from pathlib import Path
from typing import Any

from app.mlogg.log_utils import timeit, logger


SAMPLEDATA = (
    Path(__file__).resolve().parent.parent.parent.parent / "example_response.json"
)

EXCLUDE_PRODUCTNAME = ["GIGAMAX", "NONTON"]
REMOVE_QUOTAWORDS = []


class ResponseTracker:
    """
    Kelas untuk tracking dan memproses response JSON produk.
    - Melakukan tracking jumlah karakter dan jumlah produk.
    - Logging menggunakan loguru dengan context (bind)
    """

    def __init__(self, logger_instance=None):
        """
        Inisialisasi tracker dan logger.
        Logger bisa di-contextualize dengan loguru.bind.
        """
        self.logger = logger_instance or logger
        self.total_char = 0
        self.total_product = 0

    @timeit
    def count_responsechar(self, response: Any, threshold: int) -> tuple[int, bool]:
        """
        Hitung jumlah karakter pada response JSON.
        Logging dengan context 'count_responsechar'.
        Return: (jumlah karakter, apakah perlu parsing)
        """
        self.total_char = len(str(response))
        need_toparse = self.total_char > threshold
        self.logger.bind(func="count_responsechar").info(
            f"total_char={self.total_char}, need_toparse={need_toparse}"
        )
        return self.total_char, need_toparse

    @timeit
    def clean_quota_metadata(self, quota: str) -> str:
        """
        Membersihkan metadata dari field quota.
        Mengambil hanya deskripsi setelah '/' dari setiap item quota.

        Input: "DATA National/Internet 30 Days 12 GB Nasional, Local Data/Kuota Lokal Internet 30 Days 43 GB"
        Output: "Internet 30 Days 12 GB Nasional,Kuota Lokal Internet 30 Days 43 GB"
        """
        import re

        # Split by comma untuk mendapatkan setiap item quota
        items = quota.split(",")
        cleaned_items = []

        for item in items:
            item = item.strip()
            if "/" in item:
                # Ambil bagian setelah '/' sebagai deskripsi
                description = item.split("/", 1)[1].strip()
                cleaned_items.append(description)
            elif item:  # Jika tidak ada '/', tetap ambil item asli (jika tidak kosong)
                cleaned_items.append(item)

        self.logger.bind(func="clean_quota_metadata").info(
            f"Cleaned quota items: {len(cleaned_items)}"
        )
        return ",".join(cleaned_items)

    @timeit
    def optimize_quota_format(self, quota: str) -> str:
        """
        Mengoptimalkan format quota untuk mengurangi panjang karakter.

        Patterns yang dioptimalkan:
        - "X Days" → "XD"
        - "X GB" → "XGB", "X MB" → "XMB"
        - "Internet" → "Net"
        - "Nasional" → "Nas"
        - "minute" → "min"
        - "day" → "d"
        - "Internet Lokal" → "Lokal"

        Input: "Internet 7 Days 7 GB Nasional,Internet Lokal 7 Days 16 GB"
        Output: "Net 7D 7GB Nas,Lokal 7D 16GB"
        """
        import re

        # Optimization patterns
        optimizations = [
            # Duration patterns - harus diurutkan dari yang paling spesifik
            (r"\b(\d+)\s+Days\b", r"\1D"),
            (r"\b(\d+)\s+Day\b", r"\1D"),
            # Size patterns
            (r"\b(\d+(?:\.\d+)?)\s+GB\b", r"\1GB"),
            (r"\b(\d+(?:\.\d+)?)\s+MB\b", r"\1MB"),
            # Word replacements
            (r"\bInternet Lokal\b", "Lokal"),  # Harus sebelum "Internet"
            (r"\bInternet\b", "Net"),
            (r"\bNasional\b", "Nas"),
            (r"\bminute\b", "min"),
            (r"\bday\b", "d"),
            # Space normalization
            (r"\s+", " "),  # Multiple spaces to single space
        ]

        optimized = quota
        for pattern, replacement in optimizations:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)

        # Clean up extra spaces and commas
        optimized = re.sub(r"\s*,\s*", ",", optimized.strip())

        self.logger.bind(func="optimize_quota_format").info(
            f"Quota optimized: {len(quota)} → {len(optimized)} chars"
        )
        return optimized

    @timeit
    def apply_quota_optimization(self, response: Any) -> Any:
        """
        Menerapkan optimisasi quota pada seluruh response JSON.
        Mengubah field quota di setiap produk dengan optimisasi.

        Return: response JSON string dengan quota yang sudah dioptimasi
        """
        import json

        data = json.loads(response)
        paket = data.get("paket", [])

        # Optimasi quota untuk setiap produk
        for p in paket:
            original_quota = str(p.get("quota", ""))
            cleaned_quota = self.clean_quota_metadata(original_quota)
            optimized_quota = self.optimize_quota_format(cleaned_quota)
            p["quota"] = optimized_quota

        self.logger.bind(func="apply_quota_optimization").info(
            f"Applied quota optimization to {len(paket)} products"
        )

        return json.dumps(data)

    @timeit
    def check_duplicate_productid(self, response: Any) -> dict:
        """
        Check apakah ada duplicate productId di dalam response.
        Return dictionary dengan info duplikasi.

        Return format:
        {
            "has_duplicates": bool,
            "total_products": int,
            "unique_products": int,
            "duplicate_ids": [list of duplicate productIds],
            "duplicate_details": {productId: count}
        }
        """
        import json
        from collections import Counter

        data = json.loads(response)
        paket = data.get("paket", [])

        # Ambil semua productId
        product_ids = [p.get("productId", "") for p in paket]

        # Hitung kemunculan setiap productId
        id_counts = Counter(product_ids)

        # Cari yang duplicate (count > 1)
        duplicate_ids = [pid for pid, count in id_counts.items() if count > 1]
        duplicate_details = {
            pid: count for pid, count in id_counts.items() if count > 1
        }

        result = {
            "has_duplicates": len(duplicate_ids) > 0,
            "total_products": len(product_ids),
            "unique_products": len(set(product_ids)),
            "duplicate_ids": duplicate_ids,
            "duplicate_details": duplicate_details,
        }

        self.logger.bind(func="check_duplicate_productid").info(
            f"Duplicate check: has_duplicates={result['has_duplicates']}, "
            f"total={result['total_products']}, unique={result['unique_products']}"
        )

        return result

    @timeit
    def filter_productbyname_if_beginig_with(self, response: Any) -> Any:
        """
        Buang produk yang ProductName diawali salah satu prefix di EXCLUDE_PRODUCTNAME (case-insensitive, regex).
        Produk lain tetap diproses.
        """
        import json
        import re

        data = json.loads(response)
        paket = data.get("paket", [])
        filtered_paket = []
        for p in paket:
            pname = str(p.get("productName", ""))
            # Jika diawali salah satu prefix, produk DIBUANG
            # Skip jika prefix kosong untuk menghindari match semua string
            if any(
                re.match(rf"^{re.escape(f)}", pname, re.IGNORECASE)
                for f in EXCLUDE_PRODUCTNAME
                if f.strip()  # Hanya gunakan prefix yang tidak kosong
            ):
                continue
            filtered_paket.append(p)
        data["paket"] = filtered_paket
        self.logger.bind(func="filter_productByName").info(
            f"Filtered product count: {len(filtered_paket)}"
        )
        return json.dumps(data)

    @timeit
    def save_analysis_output(
        self,
        original_data: dict,
        optimized_data: dict,
        analysis_stats: dict,
        output_dir: str = "output",
    ) -> None:
        """
        Simpan hasil analisis ke file JSON dan TXT untuk analisis lebih lanjut.

        Args:
            original_data: Data JSON asli
            optimized_data: Data JSON setelah optimisasi
            analysis_stats: Statistik analisis
            output_dir: Directory untuk menyimpan output
        """
        import json
        from pathlib import Path
        from datetime import datetime

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Save detailed analysis to JSON
        analysis_result = {
            "timestamp": timestamp,
            "analysis_stats": analysis_stats,
            "original_data": original_data,
            "optimized_data": optimized_data,
            "quota_comparison": [],
        }

        # Compare quota by quota untuk analisis detail
        original_paket = original_data.get("paket", [])
        optimized_paket = optimized_data.get("paket", [])

        for i, (orig, opt) in enumerate(zip(original_paket, optimized_paket)):
            quota_analysis = {
                "index": i,
                "product_id": orig.get("productId", ""),
                "product_name": orig.get("productName", ""),
                "quota_original": str(orig.get("quota", "")),
                "quota_optimized": str(opt.get("quota", "")),
                "quota_char_before": len(str(orig.get("quota", ""))),
                "quota_char_after": len(str(opt.get("quota", ""))),
                "quota_savings": len(str(orig.get("quota", "")))
                - len(str(opt.get("quota", ""))),
                "savings_percentage": round(
                    (len(str(orig.get("quota", ""))) - len(str(opt.get("quota", ""))))
                    / max(len(str(orig.get("quota", ""))), 1)
                    * 100,
                    2,
                ),
            }
            analysis_result["quota_comparison"].append(quota_analysis)

        # Save JSON analysis
        json_file = output_path / f"quota_analysis_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        # 2. Save summary to TXT
        txt_file = output_path / f"quota_summary_{timestamp}.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("QUOTA OPTIMIZATION ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {timestamp}\n\n")

            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 20 + "\n")
            for key, value in analysis_stats.items():
                f.write(f"{key}: {value}\n")

            f.write(f"\nTOP 10 BIGGEST QUOTA SAVINGS:\n")
            f.write("-" * 30 + "\n")
            sorted_savings = sorted(
                analysis_result["quota_comparison"],
                key=lambda x: x["quota_savings"],
                reverse=True,
            )[:10]

            for item in sorted_savings:
                f.write(f"\nProduct: {item['product_name'][:50]}...\n")
                f.write(f"  Original:  {item['quota_original']}\n")
                f.write(f"  Optimized: {item['quota_optimized']}\n")
                f.write(
                    f"  Savings:   {item['quota_savings']} chars ({item['savings_percentage']}%)\n"
                )

            f.write(f"\nALL QUOTA OPTIMIZATIONS:\n")
            f.write("-" * 25 + "\n")
            for item in analysis_result["quota_comparison"]:
                if item["quota_savings"] > 0:
                    f.write(
                        f"{item['index'] + 1:3d}. {item['product_name'][:40]:<40} | "
                    )
                    f.write(
                        f"{item['quota_char_before']:3d}→{item['quota_char_after']:3d} | "
                    )
                    f.write(
                        f"Save: {item['quota_savings']:2d} ({item['savings_percentage']:5.1f}%)\n"
                    )

        self.logger.bind(func="save_analysis_output").info(
            f"Analysis saved to: {json_file} and {txt_file}"
        )

        print(f"\n📊 Analysis files saved:")
        print(f"   JSON: {json_file}")
        print(f"   TXT:  {txt_file}")

    @timeit
    def final_response(
        self,
        response_json: str,
        char_before: int,
        char_after: int,
        count_before: int,
        count_after: int,
    ) -> str:
        """
        Build final response string sesuai format:
        metadata=section char before { } - after is {} and count before {} - after {}&to=[to]&message=#productid|productname(quota)|total#...

        Output productName dan quota tetap original casing.
        Logging dengan context 'final_response'.
        """
        import json

        data = json.loads(response_json)
        to = data.get("to", "")
        paket = data.get("paket", [])
        self.total_product = len(paket)
        self.logger.bind(func="final_response").info(
            f"total_product={self.total_product}"
        )
        # Format message: #productid|productname(quota)|total#...
        message = "#" + "#".join(
            f"{p.get('productId', '')}|{str(p.get('productName', ''))}({str(p.get('quota', ''))})|{p.get('total_', '')}"
            for p in paket
        )
        metadata = f"metadata=section char before {{{char_before}}} - after is {{{char_after}}} and count before {{{count_before}}} - after {{{count_after}}}"
        return f"{metadata}&to={to}&message={message}"


def main():
    import json

    # Example usage, replace with actual loading if needed
    with open(SAMPLEDATA, "r", encoding="utf-8") as f:
        example_response = f.read()

    tracker = ResponseTracker()

    # Step 1: hitung char sebelum filter
    char_before, need_toparse = tracker.count_responsechar(
        example_response, threshold=7000
    )
    print(f"Character count in response: {char_before}")
    print(f"Need to parse: {need_toparse}")
    print(f"Sample data path: {SAMPLEDATA}")

    # Demo quota optimization
    sample_quota = "Internet 7 Days 7 GB Nasional, Internet Lokal 7 Days 16 GB"
    print(f"\n--- Quota Optimization Demo ---")
    print(f"Original: {sample_quota}")

    cleaned = tracker.clean_quota_metadata(sample_quota)
    print(f"Cleaned:  {cleaned}")

    optimized = tracker.optimize_quota_format(cleaned)
    print(f"Optimized: {optimized}")
    print(
        f"Reduction: {len(sample_quota)} → {len(optimized)} chars ({len(sample_quota) - len(optimized)} saved)"
    )

    # Step 2: filter produk by name (awalan, regex, case-insensitive)
    filtered_response = tracker.filter_productbyname_if_beginig_with(example_response)

    # Step 2.5: check duplicate productId
    duplicate_info = tracker.check_duplicate_productid(filtered_response)
    print(f"\nDuplicate check: {duplicate_info}")

    # Step 3: apply quota optimization to actual data
    optimized_response = tracker.apply_quota_optimization(filtered_response)

    # Analisis efek optimisasi quota pada total response
    print(f"\n--- Character Count Analysis ---")
    data_original = json.loads(example_response)
    data_filtered = json.loads(filtered_response)  # Data setelah filtering
    data_optimized = json.loads(optimized_response)

    # Hitung total karakter quota sebelum optimisasi (dari data yang sudah difilter)
    quota_chars_before = sum(
        len(str(p.get("quota", ""))) for p in data_filtered.get("paket", [])
    )

    # Hitung total karakter quota setelah optimisasi (dari data yang sudah dioptimasi)
    quota_chars_after = sum(
        len(str(p.get("quota", ""))) for p in data_optimized.get("paket", [])
    )

    print(f"Total quota characters before optimization: {quota_chars_before}")
    print(f"Total quota characters after optimization: {quota_chars_after}")
    print(f"Quota optimization savings: {quota_chars_before - quota_chars_after} chars")

    # Step 4: konsistensi pengukuran - gunakan json.dumps untuk keduanya
    original_normalized = json.dumps(
        data_filtered, separators=(",", ":")
    )  # Gunakan data filtered
    optimized_normalized = json.dumps(data_optimized, separators=(",", ":"))

    char_before_normalized = len(original_normalized)
    char_after_normalized = len(optimized_normalized)

    count_before = len(data_filtered.get("paket", []))  # Count dari data filtered
    count_after = len(data_optimized.get("paket", []))

    print(
        f"Normalized char count - before: {char_before_normalized}, after: {char_after_normalized}"
    )
    print(f"Product count - before: {count_before}, after: {count_after}")
    print(
        f"Total response savings: {char_before_normalized - char_after_normalized} chars"
    )

    # Step 5: save analysis output to files
    analysis_stats = {
        "total_products": count_before,
        "filtered_products": count_after,
        "char_before_optimization": char_before_normalized,
        "char_after_optimization": char_after_normalized,
        "total_char_savings": char_before_normalized - char_after_normalized,
        "quota_char_before": quota_chars_before,
        "quota_char_after": quota_chars_after,
        "quota_char_savings": quota_chars_before - quota_chars_after,
        "optimization_percentage": round(
            (char_before_normalized - char_after_normalized)
            / char_before_normalized
            * 100,
            2,
        ),
    }

    tracker.save_analysis_output(
        original_data=data_filtered,  # Gunakan data yang sudah difilter
        optimized_data=data_optimized,
        analysis_stats=analysis_stats,
    )

    # Step 6: final response (menggunakan data yang sudah dioptimasi)
    final_json = tracker.final_response(
        optimized_response,
        char_before_normalized,
        char_after_normalized,
        count_before,
        count_after,
    )
    print(f"\nFinal JSON response: {final_json[:200]}...")  # Show first 200 chars


if __name__ == "__main__":
    main()
