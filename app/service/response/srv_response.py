# ruff : noqa
from pathlib import Path
from typing import Any

from app.mlogg.log_utils import timeit, logger


SAMPLEDATA = (
    Path(__file__).resolve().parent.parent.parent.parent / "example_response_small.json"
)

EXCLUDE_PRODUCTNAME = ["Nonton", "productB"]


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
            if any(
                re.match(rf"^{re.escape(f)}", pname, re.IGNORECASE)
                for f in EXCLUDE_PRODUCTNAME
            ):
                continue
            filtered_paket.append(p)
        data["paket"] = filtered_paket
        self.logger.bind(func="filter_productByName").info(
            f"Filtered product count: {len(filtered_paket)}"
        )
        return json.dumps(data)

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
        return f"{metadata}&to=[{to}]&message={message}"


def main():
    import json

    # Example usage, replace with actual loading if needed
    with open(SAMPLEDATA, "r", encoding="utf-8") as f:
        example_response = f.read()

    tracker = ResponseTracker()

    # Step 1: hitung char sebelum filter
    char_before, need_toparse = tracker.count_responsechar(
        example_response, threshold=1000
    )
    print(f"Character count in response: {char_before}")
    print(f"Need to parse: {need_toparse}")
    print(f"Sample data path: {SAMPLEDATA}")

    # Step 2: filter produk by name (awalan, regex, case-insensitive)
    filtered_response = tracker.filter_productbyname_if_beginig_with(example_response)

    # Step 3: hitung ulang char dan count setelah filter
    char_after, _ = tracker.count_responsechar(filtered_response, threshold=1000)

    data_before = json.loads(example_response)
    data_after = json.loads(filtered_response)
    count_before = len(data_before.get("paket", []))
    count_after = len(data_after.get("paket", []))

    # Step 4: final response
    final_json = tracker.final_response(
        filtered_response, char_before, char_after, count_before, count_after
    )
    print(f"Final JSON response: {final_json}")


if __name__ == "__main__":
    main()
