from __future__ import annotations

import csv
import io
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Dữ liệu dưới đây là dữ liệu MÔ PHỎNG để minh họa ID3, không phải hồ sơ bệnh nhân.
PROFILES = {
    "diabetes": {
        "title": "Tiểu đường",
        "description": "Đường huyết, BMI, huyết áp, khát nước và mệt mỏi.",
        "target": "Kết quả",
        "attributes": [
            {"name": "Đường huyết", "values": ["Bình thường", "Cao", "Rất cao"]},
            {"name": "BMI", "values": ["Bình thường", "Thừa cân", "Béo phì"]},
            {"name": "Huyết áp", "values": ["Bình thường", "Cao"]},
            {"name": "Khát nước", "values": ["Không", "Thỉnh thoảng", "Thường xuyên"]},
            {"name": "Mệt mỏi", "values": ["Không", "Nhẹ", "Nhiều"]},
        ],
        "rows": [
            ["Cao","Béo phì","Cao","Thường xuyên","Nhiều","Tiểu đường"],
            ["Rất cao","Thừa cân","Cao","Thường xuyên","Nhiều","Tiểu đường"],
            ["Cao","Thừa cân","Bình thường","Thường xuyên","Nhiều","Tiểu đường"],
            ["Rất cao","Béo phì","Cao","Thỉnh thoảng","Nhiều","Tiểu đường"],
            ["Bình thường","Bình thường","Bình thường","Không","Không","Không bệnh"],
            ["Bình thường","Thừa cân","Bình thường","Không","Nhẹ","Không bệnh"],
            ["Cao","Bình thường","Bình thường","Thỉnh thoảng","Nhẹ","Tiền tiểu đường"],
            ["Bình thường","Béo phì","Cao","Không","Nhẹ","Tăng huyết áp"],
            ["Cao","Béo phì","Cao","Không","Nhiều","Tăng huyết áp"],
            ["Bình thường","Thừa cân","Cao","Thỉnh thoảng","Nhẹ","Tăng huyết áp"],
            ["Rất cao","Béo phì","Bình thường","Thường xuyên","Nhiều","Tiểu đường"],
            ["Bình thường","Bình thường","Cao","Không","Không","Tăng huyết áp"],
            ["Cao","Thừa cân","Cao","Thường xuyên","Nhẹ","Tiểu đường"],
            ["Bình thường","Bình thường","Bình thường","Thỉnh thoảng","Không","Không bệnh"],
            ["Cao","Béo phì","Bình thường","Thỉnh thoảng","Nhiều","Tiền tiểu đường"],
            ["Rất cao","Thừa cân","Cao","Thường xuyên","Nhẹ","Tiểu đường"],
            ["Bình thường","Béo phì","Bình thường","Không","Nhẹ","Không bệnh"],
            ["Cao","Bình thường","Cao","Không","Nhẹ","Tăng huyết áp"],
        ],
    },
    "hypertension": {
        "title": "Tăng huyết áp",
        "description": "Mức huyết áp, nhóm tuổi, BMI, vận động và tiền sử gia đình.",
        "target": "Kết quả",
        "attributes": [
            {"name":"Mức huyết áp đo được","values":["Bình thường","Tăng nhẹ","Tăng cao"]},
            {"name":"Nhóm tuổi","values":["Dưới 40","40–59","Từ 60"]},
            {"name":"BMI","values":["Bình thường","Thừa cân","Béo phì"]},
            {"name":"Vận động","values":["Thường xuyên","Đôi khi","Ít vận động"]},
            {"name":"Tiền sử gia đình","values":["Không rõ/Không","Có"]},
        ],
        "rows": [
            ["Tăng cao","Từ 60","Béo phì","Ít vận động","Có","Tăng huyết áp"],
            ["Tăng cao","40–59","Thừa cân","Ít vận động","Có","Tăng huyết áp"],
            ["Tăng nhẹ","40–59","Béo phì","Đôi khi","Có","Tăng huyết áp"],
            ["Tăng cao","Dưới 40","Bình thường","Thường xuyên","Không rõ/Không","Cần kiểm tra"],
            ["Bình thường","Dưới 40","Bình thường","Thường xuyên","Không rõ/Không","Chưa ghi nhận nguy cơ"],
            ["Bình thường","40–59","Thừa cân","Đôi khi","Không rõ/Không","Chưa ghi nhận nguy cơ"],
            ["Tăng nhẹ","Từ 60","Bình thường","Đôi khi","Có","Cần kiểm tra"],
            ["Tăng cao","Từ 60","Bình thường","Ít vận động","Không rõ/Không","Tăng huyết áp"],
            ["Bình thường","Từ 60","Béo phì","Ít vận động","Có","Cần kiểm tra"],
            ["Tăng nhẹ","Dưới 40","Bình thường","Thường xuyên","Không rõ/Không","Chưa ghi nhận nguy cơ"],
            ["Tăng cao","40–59","Béo phì","Ít vận động","Có","Tăng huyết áp"],
            ["Tăng nhẹ","40–59","Thừa cân","Đôi khi","Không rõ/Không","Cần kiểm tra"],
        ],
    },
    "heart": {
        "title": "Nguy cơ bệnh tim mạch",
        "description": "Kiểu đau ngực, huyết áp, cholesterol, đường huyết và nhịp tim nghỉ.",
        "target": "Kết quả",
        "attributes": [
            {"name":"Kiểu đau ngực","values":["Không đau","Đau khi gắng sức","Đau không điển hình"]},
            {"name":"Huyết áp","values":["Bình thường","Cao"]},
            {"name":"Cholesterol","values":["Bình thường","Cao"]},
            {"name":"Đường huyết lúc đói","values":["Bình thường","Cao"]},
            {"name":"Nhịp tim nghỉ","values":["Bình thường","Nhanh"]},
        ],
        "rows": [
            ["Đau khi gắng sức","Cao","Cao","Cao","Nhanh","Nguy cơ cao - cần khám"],
            ["Đau khi gắng sức","Cao","Cao","Bình thường","Nhanh","Nguy cơ cao - cần khám"],
            ["Đau không điển hình","Cao","Cao","Cao","Bình thường","Cần đánh giá thêm"],
            ["Không đau","Bình thường","Bình thường","Bình thường","Bình thường","Chưa ghi nhận nguy cơ từ mẫu"],
            ["Không đau","Cao","Bình thường","Bình thường","Bình thường","Cần đánh giá thêm"],
            ["Đau không điển hình","Bình thường","Cao","Bình thường","Nhanh","Cần đánh giá thêm"],
            ["Đau khi gắng sức","Bình thường","Cao","Cao","Nhanh","Nguy cơ cao - cần khám"],
            ["Không đau","Bình thường","Cao","Bình thường","Bình thường","Cần đánh giá thêm"],
            ["Đau không điển hình","Cao","Bình thường","Cao","Nhanh","Cần đánh giá thêm"],
            ["Không đau","Bình thường","Bình thường","Cao","Bình thường","Cần đánh giá thêm"],
            ["Đau khi gắng sức","Cao","Bình thường","Cao","Nhanh","Nguy cơ cao - cần khám"],
            ["Không đau","Bình thường","Bình thường","Bình thường","Nhanh","Chưa ghi nhận nguy cơ từ mẫu"],
        ],
    },
    "dengue": {
        "title": "Sốt xuất huyết",
        "description": "Nhiệt độ, số ngày sốt, đau cơ/khớp, phát ban và dấu hiệu cảnh báo.",
        "target": "Kết quả",
        "attributes": [
            {"name":"Nhiệt độ","values":["Không sốt","Sốt vừa","Sốt cao"]},
            {"name":"Số ngày sốt","values":["1–2 ngày","3–4 ngày","Từ 5 ngày"]},
            {"name":"Đau cơ/khớp","values":["Không","Có"]},
            {"name":"Phát ban/chấm xuất huyết","values":["Không","Phát ban","Chấm xuất huyết"]},
            {"name":"Dấu hiệu cảnh báo","values":["Không thấy","Đau bụng/nôn nhiều/chảy máu hoặc lừ đừ"]},
        ],
        "rows": [
            ["Sốt cao","1–2 ngày","Có","Phát ban","Không thấy","Nghi ngờ - cần khám"],
            ["Sốt cao","3–4 ngày","Có","Chấm xuất huyết","Không thấy","Nghi ngờ - cần khám"],
            ["Sốt vừa","3–4 ngày","Có","Phát ban","Không thấy","Nghi ngờ - cần khám"],
            ["Sốt cao","Từ 5 ngày","Có","Chấm xuất huyết","Đau bụng/nôn nhiều/chảy máu hoặc lừ đừ","Dấu hiệu cảnh báo - khám ngay"],
            ["Sốt vừa","Từ 5 ngày","Có","Không","Đau bụng/nôn nhiều/chảy máu hoặc lừ đừ","Dấu hiệu cảnh báo - khám ngay"],
            ["Không sốt","1–2 ngày","Không","Không","Không thấy","Chưa ghi nhận dấu hiệu từ mẫu"],
            ["Sốt vừa","1–2 ngày","Không","Không","Không thấy","Chưa ghi nhận dấu hiệu từ mẫu"],
            ["Sốt cao","3–4 ngày","Có","Không","Đau bụng/nôn nhiều/chảy máu hoặc lừ đừ","Dấu hiệu cảnh báo - khám ngay"],
            ["Sốt vừa","3–4 ngày","Có","Chấm xuất huyết","Đau bụng/nôn nhiều/chảy máu hoặc lừ đừ","Dấu hiệu cảnh báo - khám ngay"],
            ["Sốt cao","1–2 ngày","Có","Không","Không thấy","Nghi ngờ - cần khám"],
            ["Sốt vừa","1–2 ngày","Không","Phát ban","Không thấy","Cần theo dõi/đánh giá"],
            ["Không sốt","Từ 5 ngày","Không","Không","Không thấy","Cần đánh giá nguyên nhân khác"],
        ],
    },
    "anemia": {
        "title": "Thiếu máu",
        "description": "Hemoglobin, mệt mỏi, da/niêm mạc nhợt, chóng mặt và khó thở khi gắng sức.",
        "target": "Kết quả",
        "attributes": [
            {"name":"Hemoglobin xét nghiệm","values":["Trong ngưỡng tham chiếu","Giảm nhẹ","Giảm nhiều"]},
            {"name":"Mệt mỏi","values":["Không","Có"]},
            {"name":"Da/niêm mạc nhợt","values":["Không","Có"]},
            {"name":"Chóng mặt","values":["Không","Thỉnh thoảng","Thường xuyên"]},
            {"name":"Khó thở khi gắng sức","values":["Không","Có"]},
        ],
        "rows": [
            ["Giảm nhiều","Có","Có","Thường xuyên","Có","Mẫu gợi ý thiếu máu - cần khám"],
            ["Giảm nhẹ","Có","Có","Thỉnh thoảng","Không","Mẫu gợi ý thiếu máu - cần khám"],
            ["Giảm nhiều","Có","Không","Thường xuyên","Có","Mẫu gợi ý thiếu máu - cần khám"],
            ["Trong ngưỡng tham chiếu","Không","Không","Không","Không","Chưa ghi nhận dấu hiệu từ mẫu"],
            ["Trong ngưỡng tham chiếu","Có","Không","Thỉnh thoảng","Không","Cần đánh giá nguyên nhân khác"],
            ["Giảm nhẹ","Có","Không","Thỉnh thoảng","Có","Mẫu gợi ý thiếu máu - cần khám"],
            ["Trong ngưỡng tham chiếu","Không","Có","Không","Không","Cần đánh giá thêm"],
            ["Giảm nhiều","Có","Có","Thường xuyên","Có","Mẫu gợi ý thiếu máu - cần khám"],
            ["Giảm nhẹ","Không","Có","Thỉnh thoảng","Không","Cần đánh giá thêm"],
            ["Trong ngưỡng tham chiếu","Có","Không","Không","Có","Cần đánh giá nguyên nhân khác"],
            ["Giảm nhẹ","Có","Có","Thường xuyên","Có","Mẫu gợi ý thiếu máu - cần khám"],
            ["Trong ngưỡng tham chiếu","Không","Không","Thỉnh thoảng","Không","Chưa ghi nhận dấu hiệu từ mẫu"],
        ],
    },
}


def entropy(rows: list[dict[str, str]], target: str) -> float:
    """Entropy(S) = -Σ p(c) log2 p(c)."""
    if not rows:
        return 0.0
    counts = Counter(row[target] for row in rows)
    total = len(rows)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def information_gain(rows: list[dict[str, str]], attribute: str, target: str) -> float:
    """Gain(S,A) = Entropy(S) - Σ(|Sv|/|S|) Entropy(Sv)."""
    if not rows:
        return 0.0
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row[attribute]].append(row)
    remainder = sum(
        len(group) / len(rows) * entropy(group, target)
        for group in groups.values()
    )
    return entropy(rows, target) - remainder


def majority_class(rows: list[dict[str, str]], target: str) -> str:
    return Counter(row[target] for row in rows).most_common(1)[0][0]


@dataclass
class TreeNode:
    attribute: str | None = None
    label: str | None = None
    majority: str | None = None
    gain: float | None = None
    samples: int = 0
    children: dict[str, "TreeNode"] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        return self.attribute is None


class ID3:
    """Cài đặt ID3 đệ quy theo mã giả trong tài liệu học tập."""

    def __init__(self, target: str):
        self.target = target
        self.root: TreeNode | None = None
        self.attributes: list[str] = []
        self.root_gains: dict[str, float] = {}

    def fit(self, rows: list[dict[str, str]], attributes: list[str]) -> "ID3":
        if not rows:
            raise ValueError("Tập dữ liệu huấn luyện không được rỗng.")
        if len(attributes) != 5:
            raise ValueError("Ứng dụng yêu cầu đúng 5 thuộc tính đầu vào.")
        required = attributes + [self.target]
        for i, row in enumerate(rows, start=1):
            for col in required:
                if col not in row or str(row[col]).strip() == "":
                    raise ValueError(f"Dòng {i} thiếu giá trị ở cột '{col}'.")
        self.attributes = attributes[:]
        self.root_gains = {
            a: information_gain(rows, a, self.target) for a in attributes
        }
        self.root = self._build(rows, attributes[:])
        return self

    def _build(self, rows: list[dict[str, str]], available: list[str]) -> TreeNode:
        if not rows:
            return TreeNode(label="Chưa xác định")
        majority = majority_class(rows, self.target)
        labels = {r[self.target] for r in rows}
        if len(labels) == 1:
            return TreeNode(label=next(iter(labels)), majority=majority, samples=len(rows))
        if not available:
            return TreeNode(label=majority, majority=majority, samples=len(rows))

        gains = {a: information_gain(rows, a, self.target) for a in available}
        best = max(available, key=lambda a: gains[a])
        node = TreeNode(
            attribute=best, majority=majority,
            gain=gains[best], samples=len(rows)
        )
        remaining = [a for a in available if a != best]
        for value in sorted({r[best] for r in rows}):
            subset = [r for r in rows if r[best] == value]
            node.children[value] = self._build(subset, remaining)
        return node

    def predict(self, sample: dict[str, str]) -> tuple[str, list[str]]:
        if self.root is None:
            raise RuntimeError("Mô hình chưa được huấn luyện.")
        node = self.root
        path = []
        while not node.is_leaf:
            value = sample.get(node.attribute or "", "")
            path.append({"attribute": node.attribute, "value": value})
            child = node.children.get(value)
            if child is None:
                return node.majority or "Chưa xác định", path
            node = child
        return node.label or "Chưa xác định", path

    def as_dict(self, node: TreeNode | None = None) -> dict[str, Any]:
        node = node or self.root
        if node is None:
            return {}
        if node.is_leaf:
            return {"type": "leaf", "label": node.label, "samples": node.samples}
        return {
            "type": "node", "attribute": node.attribute,
            "gain": node.gain, "samples": node.samples,
            "children": {v: self.as_dict(ch) for v, ch in node.children.items()}
        }


def rows_to_dicts(attributes: list[str], target: str, rows: list[list[str]]) -> list[dict[str, str]]:
    result = []
    for index, row in enumerate(rows, start=1):
        if len(row) != 6:
            raise ValueError(f"Mẫu số {index} phải có 5 thuộc tính và 1 nhãn kết quả.")
        item = dict(zip(attributes + [target], [str(x).strip() for x in row]))
        if any(not value for value in item.values()):
            raise ValueError(f"Mẫu số {index} có ô trống.")
        result.append(item)
    return result


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/profiles")
def get_profiles():
    return jsonify([
        {"id": key, "title": value["title"], "description": value["description"]}
        for key, value in PROFILES.items()
    ])


@app.get("/api/profile/<profile_id>")
def get_profile(profile_id: str):
    profile = PROFILES.get(profile_id)
    if not profile:
        return jsonify({"error": "Không tìm thấy bộ bệnh."}), 404
    return jsonify(profile)


@app.post("/api/train-predict")
def train_predict():
    try:
        payload = request.get_json(force=True)
        attributes = payload["attributes"]
        target = payload.get("target", "Kết quả")
        rows = rows_to_dicts(attributes, target, payload["rows"])
        model = ID3(target).fit(rows, attributes)
        sample = payload.get("sample", {})
        prediction, path = model.predict(sample)
        return jsonify({
            "prediction": prediction,
            "path": path,
            "tree": model.as_dict(),
            "entropy": entropy(rows, target),
            "root_gains": model.root_gains,
            "sample_count": len(rows),
            "class_count": len({r[target] for r in rows}),
        })
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/import-csv")
def import_csv():
    """Đọc CSV được gửi lên; yêu cầu đúng 6 cột (5 thuộc tính + nhãn)."""
    try:
        payload = request.get_json(force=True)
        content = payload["content"]
        reader = csv.reader(io.StringIO(content))
        records = list(reader)
        if len(records) < 2:
            raise ValueError("CSV phải có dòng tiêu đề và ít nhất một mẫu.")
        header = [x.strip() for x in records[0]]
        if len(header) != 6:
            raise ValueError("CSV phải có đúng 6 cột: 5 thuộc tính và 1 cột kết quả.")
        data = [[x.strip() for x in row] for row in records[1:] if row]
        for i, row in enumerate(data, 1):
            if len(row) != 6 or any(not v for v in row):
                raise ValueError(f"Dòng dữ liệu {i} không đủ 6 giá trị hoặc có ô trống.")
        return jsonify({"header": header, "rows": data})
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
