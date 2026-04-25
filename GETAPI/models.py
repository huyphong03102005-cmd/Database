from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

# 1. Bảng Khách Hàng
class KhachHang(models.Model):
    Hovaten = models.CharField(max_length=900, null=True, blank=True)
    KhachHangID = models.CharField(max_length=10, primary_key=True)
    Email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    NgayDangKy = models.DateTimeField(auto_now_add=True)
    AnhDaiDienURL = models.TextField(null=True, blank=True)
    Ngaysinh=models.DateField(null=True, blank=True)
    def __str__(self):
        return self.KhachHangID

# 2. Bảng Nhà Xe:
class Nhaxe(models.Model):
    NhaxeID = models.CharField(max_length=10, primary_key=True)
    Tennhaxe = models.CharField(max_length=200, null=True, blank=True)
    TenNguoiDaiDien = models.CharField(max_length=200, null=True, blank=True)
    Email = models.EmailField(max_length=100, unique=True)
    NgayDangKy = models.DateTimeField(auto_now_add=True)
    AnhDaiDien = models.TextField(null=True, blank=True)
    DiaChiTruSo = models.TextField(max_length=200, null=True, blank=True)
    SoDienThoai = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(regex=r'^0\d{9,}$', message="Số điện thoại phải bắt đầu bằng 0 và có ít nhất 10 số")]
    )

    def __str__(self):
        return self.Tennhaxe or self.NhaxeID

# 3. Bảng Tài Khoản (User Authentication)
class User_Authentication(models.Model):
    UserID = models.CharField(max_length=10, primary_key=True)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True)
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.SET_NULL, null=True, blank=True)
    TenDangNhap = models.CharField(max_length=200, unique=True,null=True,blank=True)
    MatKhau = models.CharField(max_length=200,null=True,blank=True)
    Vaitro = models.CharField(max_length=20)
    SoDienThoai = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(regex=r'^0\d{9,}$', message="Số điện thoại phải bắt đầu bằng 0 và có ít nhất 10 số")]
    )
    def __str__(self):
        return self.TenDangNhap

# 4. Bảng Tài Xế
class Taixe(models.Model):
    TaixeID = models.CharField(max_length=10, primary_key=True)
    HinhAnhURL = models.CharField(max_length=255, null=True, blank=True)
    SoBangLai = models.CharField(max_length=20, unique=True)
    soCCCD = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{12}$', message="CCCD phải có đúng 12 chữ số")]
    )
    LoaiBangLai = models.CharField(max_length=20, null=True, blank=True)
    NgayHetHanBangLai = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.TaixeID

# 5. Bảng Chi Tiết Tài Xế (Trung gian Nhà xe - Tài xế)
class CHITIETTAIXE(models.Model):
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    Taixe = models.ForeignKey(Taixe, on_delete=models.CASCADE)
    HoTen = models.CharField(max_length=200, null=True, blank=True)
    Tennhaxe = models.CharField(max_length=200, null=True, blank=True)
    NgayBatDau = models.DateTimeField(null=True, blank=True)
    NgayKetThuc = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('Nhaxe', 'Taixe')

# 6. Bảng Loại Xe
class Loaixe(models.Model):
    LoaixeID = models.CharField(max_length=10, primary_key=True)
    NgayCapNhatGia = models.DateField(null=True, blank=True)
    SoCho = models.IntegerField(validators=[MinValueValidator(1)])
    SoDoGheNgoiURL = models.CharField(max_length=255, null=True, blank=True)
    GiaVe = models.DecimalField(max_digits=19, decimal_places=4) # Thay cho MONEY

    def __str__(self):
        return self.LoaixeID

# 7. Bảng Chi Tiết Loại Xe (Trung gian Nhà xe - Loại xe)
class CHITIETLOAIXE(models.Model):
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    Loaixe = models.ForeignKey(Loaixe, on_delete=models.CASCADE)
    TenLoaiXe = models.CharField(max_length=50, null=True, blank=True)
    Tennhaxe = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('Nhaxe', 'Loaixe')

# 8. Bảng Xe
class Xe(models.Model):
    XeID = models.CharField(max_length=10, primary_key=True)
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    Loaixe = models.ForeignKey(Loaixe, on_delete=models.CASCADE)
    TrangThai = models.CharField(max_length=20, null=True, blank=True)
    SoGhe = models.IntegerField(null=True, blank=True)
    BienSoXe = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.BienSoXe

# 9. Bảng Tuyến Xe:
class TuyenXe(models.Model):
    TRANG_THAI_CHOICES = [
        ('Đang hoạt động', 'Đang hoạt động'),
        ('Bảo trì', 'Bảo trì'),
        ('Ngưng hoạt động', 'Ngưng hoạt động'),
    ]
    tuyenXeID = models.CharField(max_length=10, primary_key=True)
    nhaXe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    tenTuyen = models.CharField(max_length=500, null=True, blank=True)
    diemDi = models.CharField(max_length=500, default='Đà Nẵng')
    diemDen = models.CharField(max_length=500, default='Huế')
    QuangDuong = models.CharField(max_length=100, null=True, blank=True)
    ThoiGian = models.CharField(max_length=100, null=True, blank=True)
    TrangThai = models.CharField(max_length=50, choices=TRANG_THAI_CHOICES, default='Đang hoạt động')
    DiemTrungGian = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.tenTuyen or self.tuyenXeID

# 10. Bảng Chuyến Xe
class ChuyenXe(models.Model):
    ChuyenXeID = models.CharField(max_length=10, primary_key=True)
    Xe = models.ForeignKey(Xe, on_delete=models.SET_NULL, null=True, blank=True)
    TuyenXe = models.ForeignKey(TuyenXe, on_delete=models.CASCADE)
    Taixe = models.ForeignKey(Taixe, on_delete=models.CASCADE, null=True, blank=True)
    NgayKhoiHanh = models.DateField(null=True, blank=True)
    GioDi = models.TimeField(null=True, blank=True)
    GioDen = models.TimeField(null=True, blank=True)
    TrangThai = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.ChuyenXeID

# 11. Bảng Ghế Ngồi
class GheNgoi(models.Model):
    gheID = models.CharField(max_length=10, primary_key=True)
    ChuyenXe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE)
    soGhe = models.CharField(max_length=5, null=True, blank=True)
    trangThai = models.CharField(max_length=20, null=True, blank=True)
    # Thêm khoá vé cho ghế, theo yêu cầu "gán mã vé vừa tạo vào ghế đó"
    Ve = models.ForeignKey('Ve', on_delete=models.SET_NULL, null=True, blank=True, related_name='ghe_ngoi_ve')

    def __str__(self):
        return f"{self.soGhe} - {self.ChuyenXe.ChuyenXeID}"

# 12. Bảng Vé
class Ve(models.Model):
    TRANG_THAI_DANH_GIA_CHOICES = [
        ('Không có quyền', 'Không có quyền'),
        ('Chờ đánh giá', 'Chờ đánh giá'),
        ('Đã đánh giá', 'Đã đánh giá'),
    ]
    TRANG_THAI_THANH_TOAN_CHOICES = [
        ('Chưa thanh toán', 'Chưa thanh toán'),
        ('Đã thanh toán', 'Đã thanh toán'),
    ]
    VeID = models.CharField(max_length=10, primary_key=True)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    ChuyenXe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE)
    Ghe = models.ForeignKey(GheNgoi, on_delete=models.CASCADE)
    SoDienThoai = models.CharField(
        max_length=12,
        validators=[RegexValidator(regex=r'^0\d{9,}$', message="Số điện thoại phải bắt đầu bằng 0 và có ít nhất 10 số")]
    )
    NgayDat = models.DateTimeField(auto_now_add=True)
    GiaVe = models.DecimalField(max_digits=19, decimal_places=4)
    TrangThaiThanhToan = models.CharField(max_length=20, choices=TRANG_THAI_THANH_TOAN_CHOICES, default='Chưa thanh toán')
    TrangThaiDanhGia = models.CharField(max_length=50, choices=TRANG_THAI_DANH_GIA_CHOICES, default='Không có quyền')
    TrangThai = models.CharField(max_length=50, default='Hiện tại')
    DiemDon = models.CharField(max_length=500, null=True, blank=True)
    DiemTra = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.VeID

# 13. Bảng Thanh Toán
class ThanhToan(models.Model):
    ThanhToanID = models.CharField(max_length=10, primary_key=True)
    Ve = models.OneToOneField(Ve, on_delete=models.CASCADE)
    SoTien = models.DecimalField(max_digits=19, decimal_places=4)
    PhuongThucTT = models.CharField(max_length=20, null=True, blank=True)
    NgayThanhToan = models.DateTimeField(auto_now_add=True)
    MaGiaoDich = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.ThanhToanID

# 14. Bảng Đánh Giá
class DanhGia(models.Model):
    DanhGiaID = models.CharField(max_length=10, primary_key=True)
    Ve = models.OneToOneField(Ve, on_delete=models.CASCADE)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    Diemso = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Nhanxet = models.TextField(max_length=500, null=True, blank=True)
    NgayDanhGia = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Review {self.DanhGiaID} - {self.Diemso}"
