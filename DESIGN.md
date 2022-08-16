# Giới thiệu

## Mục đích của công cụ này

Công cụ dùng để gán nhãn cho kết quả OCR.

- Gán nhãn dữ liệu với nhãn là quan hệ giữa hai thực thể trong một tập hợp.
- Gán nhãn phân lớp theo dạng phi tuyến sử dụng đồ thị

## Worlflow và các chức năng (dự tính) được hỗ trợ trong công cụ

1. Mở công cụ
2. Import dữ liệu chưa gán nhãn
2. Import dữ liệu đã gán nhãn
3. Relation
	- Tạo relation text2text hoặc label2text
		- import danh sách label
		- thêm label
		- xóa label
	- Xóa relation
	- Đổi tên relation (phụ)
4. Gán nhãn
5. Chuyển qua bản ghi tiếp theo (hoặc ngược lại)
6. Export dữ liệu

## Format dữ liệu

File đầu vào có dạng jsonl và không tương thích với kiểu dữ liệu jsonl cũ (SPADE type 1).
Mỗi json có dạng từ điển. Các khóa trong file là:

- `texts: List[Int]` (bắt buộc): danh sách các văn bản trong mỗi hộp mà OCR được
- `bboxes: List[Polygon | XYXY]` (bắt buộc): danh sách các bounding box tương ứng với mỗi hộp văn bản
- `format: String` (bắt buộc): format của bounding box, sẽ quyết định bounding box được đọc như thế nào
- `relations: List[Relation]` (tùy chọn): nếu không có khóa này, không import label

Một `Relation` có cấu trúc:

- `name: String` (bắt buộc): tên của relation
- `type: Label2Text | Text2Text` (bắt buộc): loại của relation
	- `Label2Text`: quan hệ với label được import từ file text (lưu trong trường `label`)
	- `Text2Text`: quan hệ giữa các box với nhau
- `label: List[String] | Nothing` (tùy chọn\*): bắt buộc trong trường hợp relation là `Label2Text`, là `Nothing` trong trường hợp `Text2Text`
- `relation: Array[Bool, 2]` (bắt buộc): Ma trận có dạng ma trận kề biểu diễn quan hệ nối giữa label sang text hoặc text sang text, tùy vào `type`.

Các kiểu dữ liệu đại số sẽ được lưu thành string trong json. Trong file jsonl, mỗi đoạn json nằm trên một dòng.


# Workflow

## Bắt đầu

## Import dữ liệu
## Tạo relation text2text hoặc label2text
## Import danh sách label
## Thêm label
## Xóa label
## Xóa relation
## Đổi tên relation (phụ)
## Gán nhãn
## Chuyển qua bản ghi tiếp theo (hoặc ngược lại)
## Export dữ liệu
