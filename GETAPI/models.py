from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# 1. Bảng Khách Hàng
class KhachHang(models.Model):
    KhachHangID = models.CharField(max_length=10, primary_key=True, blank=True)  # Để blank=True cho phép tự sinh
    Hovaten = models.CharField(max_length=900, null=True, blank=True)
    Email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    NgayDangKy = models.DateTimeField(auto_now_add=True)
    AnhDaiDienURL = models.TextField(null=True, blank=True)
    Ngaysinh = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Danh sách Khách hàng'

    def save(self, *args, **kwargs):
        if not self.KhachHangID:
            # Tạo tự động KhachHangID với cú pháp KH00001, KH00002...
            last_kh = KhachHang.objects.all().order_by('KhachHangID').last()
            if not last_kh:
                self.KhachHangID = 'KH00001'
            else:
                last_id = last_kh.KhachHangID
                try:
                    last_num = int(last_id[2:])  # Lấy phần số sau chữ 'KH'
                    new_num = last_num + 1
                    self.KhachHangID = f'KH{new_num:05d}'
                except ValueError:
                    # Fallback nếu vì lý do nào đó ID cũ không đúng format
                    self.KhachHangID = 'KH00001'
        super(KhachHang, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.KhachHangID) if self.KhachHangID else "Chưa có ID"


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

    class Meta:
        verbose_name = 'Nhà xe'
        verbose_name_plural = 'Danh sách Nhà xe'

    def __str__(self):
        return str(self.Tennhaxe) if self.Tennhaxe else str(self.NhaxeID)


# 3. Bảng Tài Khoản (User Authentication)
class UserAuthentication(models.Model):
    UserID = models.CharField(max_length=10, primary_key=True)
    Taixe = models.ForeignKey('Taixe', on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True)
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.SET_NULL, null=True, blank=True)
    TenDangNhap = models.CharField(max_length=200, unique=True, null=True, blank=True)
    MatKhau = models.CharField(max_length=200, null=True, blank=True)
    Vaitro = models.CharField(max_length=20)
    SoDienThoai = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(regex=r'^0\d{9,}$', message="Số điện thoại phải bắt đầu bằng 0 và có ít nhất 10 số")]
    )

    class Meta:
        verbose_name = 'Tài khoản User'
        verbose_name_plural = 'Danh sách Tài khoản User'
        db_table = 'GETAPI_user_authentication'

    def __str__(self):
        return str(self.TenDangNhap) if self.TenDangNhap else str(self.UserID)

# Để tương thích ngược với code cũ trong project
User_Authentication = UserAuthentication

# 4. Bảng Tài Xế
class Taixe(models.Model):
    TaixeID = models.CharField(max_length=10, primary_key=True)
    HinhAnhURL = models.TextField(null=True, blank=True) # Đổi sang TextField
    SoBangLai = models.CharField(max_length=20, unique=True)
    soCCCD = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{12}$', message="CCCD phải có đúng 12 chữ số")]
    )
    LoaiBangLai = models.CharField(max_length=20, null=True, blank=True)
    NgayHetHanBangLai = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tài xế'
        verbose_name_plural = 'Danh sách Tài xế'

    def __str__(self):
        return str(self.TaixeID)


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
        verbose_name = 'Chi tiết Tài xế'
        verbose_name_plural = 'Danh sách Chi tiết Tài xế'

    def __str__(self):
        return f"{self.Nhaxe} - {self.Taixe}"


# 6. Bảng Loại Xe
class Loaixe(models.Model):
    LoaixeID = models.CharField(max_length=10, primary_key=True)
    NgayCapNhatGia = models.DateField(null=True, blank=True)
    SoCho = models.IntegerField(validators=[MinValueValidator(1)])
    SoDoGheNgoiURL = models.CharField(max_length=255, null=True, blank=True)
    GiaVe = models.IntegerField() # Đổi sang IntegerField thay cho DecimalField

    class Meta:
        verbose_name = 'Loại xe'
        verbose_name_plural = 'Danh sách Loại xe'

    def __str__(self):
        return str(self.LoaixeID)


# 7. Bảng Chi Tiết Loại Xe (Trung gian Nhà xe - Loại xe)
class CHITIETLOAIXE(models.Model):
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    Loaixe = models.ForeignKey(Loaixe, on_delete=models.CASCADE)
    TenLoaiXe = models.CharField(max_length=50, null=True, blank=True)
    Tennhaxe = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('Nhaxe', 'Loaixe')
        verbose_name = 'Chi tiết Loại xe'
        verbose_name_plural = 'Danh sách Chi tiết Loại xe'

    def __str__(self):
        return f"{self.Nhaxe} - {self.Loaixe}"


# 8. Bảng Xe
class Xe(models.Model):
    XeID = models.CharField(max_length=10, primary_key=True)
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE)
    Loaixe = models.ForeignKey(Loaixe, on_delete=models.CASCADE)
    TrangThai = models.CharField(max_length=20, null=True, blank=True)
    SoGhe = models.IntegerField(null=True, blank=True)
    BienSoXe = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = 'Xe'
        verbose_name_plural = 'Danh sách Xe'

    def __str__(self):
        return str(self.BienSoXe) if self.BienSoXe else str(self.XeID)


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

    class Meta:
        verbose_name = 'Tuyến xe'
        verbose_name_plural = 'Danh sách Tuyến xe'

    def __str__(self):
        return str(self.tenTuyen) if self.tenTuyen else str(self.tuyenXeID)


# 10. Bảng Chuyến Xe
class ChuyenXe(models.Model):
    ChuyenXeID = models.CharField(max_length=10, primary_key=True)
    Xe = models.ForeignKey(Xe, on_delete=models.SET_NULL, null=True, blank=True)
    TuyenXe = models.ForeignKey(TuyenXe, on_delete=models.CASCADE)
    Taixe = models.ForeignKey(Taixe, on_delete=models.CASCADE, null=True, blank=True)
    NgayKhoiHanh = models.DateField(null=True, blank=True)
    GioDi = models.TimeField(null=True, blank=True)
    GioDen = models.TimeField(null=True, blank=True)
    # Thiết lập trạng thái mặc định là "Chưa hoàn thành"
    TrangThai = models.CharField(max_length=50, null=True, blank=True, default='Chưa hoàn thành')

    class Meta:
        verbose_name = 'Chuyến xe'
        verbose_name_plural = 'Danh sách Chuyến xe'

    def __str__(self):
        return str(self.ChuyenXeID)


# 11. Bảng Ghế Ngồi
class GheNgoi(models.Model):
    TRANG_THAI_GHE_CHOICES = [
        ('Còn trống', 'Còn trống'),
        ('Đang chọn', 'Đang chọn'),
        ('Đã đặt', 'Đã đặt'),
    ]
    gheID = models.CharField(max_length=10, primary_key=True)
    ChuyenXe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE)
    soGhe = models.CharField(max_length=5, null=True, blank=True)
    trangThai = models.CharField(max_length=20, choices=TRANG_THAI_GHE_CHOICES, default='Còn trống')
    # Thêm khoá vé cho ghế, theo yêu cầu "gán mã vé vừa tạo vào ghế đó"
    Ve = models.ForeignKey('Ve', on_delete=models.SET_NULL, null=True, blank=True, related_name='ghe_ngoi_ve')

    class Meta:
        verbose_name = 'Ghế ngồi'
        verbose_name_plural = 'Danh sách Ghế ngồi'

    def __str__(self):
        return f"{self.soGhe} - {self.ChuyenXe.ChuyenXeID}"


# 12. Bảng Vé
class Ve(models.Model):
    TRANG_THAI_DAN_GIA_CHOICES = [
        ('Không có quyền', 'Không có quyền'),
        ('Chờ đánh giá', 'Chờ đánh giá'),
        ('Đã đánh giá', 'Đã đánh giá'),
    ]
    TRANG_THAI_THANH_TOAN_CHOICES = [
        ('Chưa thanh toán', 'Chưa thanh toán'),
        ('Đã thanh toán', 'Đã thanh toán'),
    ]
    TRANG_THAI_VE_CHOICES = [
        ('Đã đặt', 'Đã đặt'),
        ('Đã đi', 'Đã đi'),
        ('Đã hủy', 'Đã hủy'),
    ]
    VeID = models.CharField(max_length=10, primary_key=True)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    ChuyenXe = models.ForeignKey(ChuyenXe, on_delete=models.CASCADE)
    SoDienThoai = models.CharField(
        max_length=12,
        validators=[RegexValidator(regex=r'^0\d{9,}$', message="Số điện thoại phải bắt đầu bằng 0 và có ít nhất 10 số")]
    )
    NgayDat = models.DateTimeField(auto_now_add=True)
    TongTien = models.DecimalField(max_digits=19, decimal_places=4)
    TrangThaiThanhToan = models.CharField(max_length=20, choices=TRANG_THAI_THANH_TOAN_CHOICES,
                                          default='Chưa thanh toán')
    TrangThaiDanhGia = models.CharField(max_length=50, choices=TRANG_THAI_DAN_GIA_CHOICES, default='Không có quyền')
    TrangThai = models.CharField(max_length=50, choices=TRANG_THAI_VE_CHOICES, default='Đã đặt')
    DiemDon = models.CharField(max_length=500, null=True, blank=True)
    DiemTra = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = 'Vé'
        verbose_name_plural = 'Danh sách Vé'

    def __str__(self):
        return str(self.VeID)

# 12.1. Bảng Vé Hủy
class VeHuy(models.Model):
    TRANG_THAI_DAN_GIA_CHOICES = [
        ('Không có quyền', 'Không có quyền'),
        ('Chờ đánh giá', 'Chờ đánh giá'),
        ('Đã đánh giá', 'Đã đánh giá'),
    ]
    TRANG_THAI_THANH_TOAN_CHOICES = [
        ('Chưa thanh toán', 'Chưa thanh toán'),
        ('Đã thanh toán', 'Đã thanh toán'),
        ('Đã hoàn tiền', 'Đã hoàn tiền'),
    ]
    TRANG_THAI_VE_CHOICES = [
        ('Đã hủy', 'Đã hủy'),
    ]
    VeHuyID = models.CharField(max_length=10, primary_key=True)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True)
    ChuyenXe = models.ForeignKey(ChuyenXe, on_delete=models.SET_NULL, null=True, blank=True)
    SoDienThoai = models.CharField(max_length=12, null=True, blank=True)
    NgayDat = models.DateTimeField(null=True, blank=True)
    TongTien = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    TrangThaiThanhToan = models.CharField(max_length=20, choices=TRANG_THAI_THANH_TOAN_CHOICES, default='Chưa thanh toán')
    TrangThaiDanhGia = models.CharField(max_length=50, choices=TRANG_THAI_DAN_GIA_CHOICES, default='Không có quyền')
    TrangThai = models.CharField(max_length=50, choices=TRANG_THAI_VE_CHOICES, default='Đã hủy')
    DiemDon = models.CharField(max_length=500, null=True, blank=True)
    DiemTra = models.CharField(max_length=500, null=True, blank=True)

    # Trường mới cho vé hủy
    ThoiGianHuy = models.DateTimeField(auto_now_add=True)
    DanhSachGhe = models.CharField(max_length=500, null=True, blank=True)
    SoLuongGhe = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Vé hủy'
        verbose_name_plural = 'Danh sách Vé hủy'

    def __str__(self):
        return str(self.VeHuyID)
    
@receiver(post_save, sender=Ve)
def handle_trang_thai_danh_gia(sender, instance, **kwargs):
    # 1. Nếu vé vừa hoàn thành (Đã đi) -> Cho phép đánh giá nếu còn hạn
    if instance.TrangThai == 'Đã đi' and instance.TrangThaiDanhGia == 'Không có quyền':
        # Kiểm tra nếu chưa quá 7 ngày kể từ lúc kết thúc
        is_expired = False
        if hasattr(instance.ChuyenXe, 'NgayKhoiHanh') and instance.ChuyenXe.NgayKhoiHanh:
            if (timezone.now().date() - instance.ChuyenXe.NgayKhoiHanh).days >= 7:
                is_expired = True

        if not is_expired:
            Ve.objects.filter(pk=instance.pk).update(TrangThaiDanhGia='Chờ đánh giá')

    # 2. Nếu đang 'Chờ đánh giá' mà đã quá 7 ngày -> Ẩn (Không có quyền)
    if instance.TrangThaiDanhGia == 'Chờ đánh giá' and hasattr(instance.ChuyenXe, 'NgayKhoiHanh') and instance.ChuyenXe.NgayKhoiHanh:
        if (timezone.now().date() - instance.ChuyenXe.NgayKhoiHanh).days >= 7:
            Ve.objects.filter(pk=instance.pk).update(TrangThaiDanhGia='Không có quyền')

# 13. Bảng Thanh Toán
class ThanhToan(models.Model):
    ThanhToanID = models.CharField(max_length=10, primary_key=True)
    Ve = models.OneToOneField(Ve, on_delete=models.CASCADE)
    SoTien = models.DecimalField(max_digits=19, decimal_places=4)
    PhuongThucTT = models.CharField(max_length=20, null=True, blank=True)
    NgayThanhToan = models.DateTimeField(auto_now_add=True)
    MaGiaoDich = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Danh sách Thanh toán'

    def __str__(self):
        return str(self.ThanhToanID)


# 14. Bảng Đánh Giá
class DanhGia(models.Model):
    DanhGiaID = models.CharField(max_length=10, primary_key=True)
    Ve = models.OneToOneField(Ve, on_delete=models.CASCADE)
    KhachHang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    Diemso = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    Nhanxet = models.TextField(max_length=500, null=True, blank=True)
    NgayDanhGia = models.DateTimeField(auto_now_add=True)
    Nhaxe = models.ForeignKey(Nhaxe, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Danh sách Đánh giá'

    def __str__(self):
        return f"Review {self.DanhGiaID} - {self.Diemso}"

@receiver(post_save, sender=DanhGia)
def update_rating_nhaxe(sender, instance, created, **kwargs):
    if created:
        try:
            nhaxe = instance.Ve.ChuyenXe.TuyenXe.nhaXe

            # Cập nhật điểm cho nhà xe (giả sử bảng Nhaxe có trường rating_count, rating_sum)
            if hasattr(nhaxe, 'rating_count') and hasattr(nhaxe, 'rating_sum'):
                nhaxe.rating_count += 1
                nhaxe.rating_sum += instance.Diemso
                nhaxe.save()
        except Exception:
            pass

        # Cập nhật trạng thái vé (KHÔNG dùng save để tránh loop)
        Ve.objects.filter(pk=instance.Ve.pk).update(
            TrangThaiDanhGia='Đã đánh giá'
        )

# ==================== SIGNALS (Tự động tạo ghế) ====================
@receiver(post_save, sender=ChuyenXe)
def auto_create_seats(sender, instance, created, **kwargs):
    if created:  # Chỉ chạy khi tạo chuyến xe MỚI
        try:
            # 1. Lấy số chỗ từ Loại Xe (thông qua đối tượng Xe liên kết)
            if instance.Xe and instance.Xe.Loaixe:
                num_seats = instance.Xe.Loaixe.SoCho

                # 2. Quy tắc đặt đầu mã ghế
                prefix = "G"
                if num_seats == 4:
                    prefix = "A"
                elif num_seats == 7:
                    prefix = "B"
                elif num_seats == 9:
                    prefix = "C"

                # 3. Tạo danh sách ghế
                seats_to_create = []
                for i in range(1, num_seats + 1):
                    # Mã ghế: A1, A2... hoặc G01, G02...
                    ma_ghe = f"{prefix}{i}" if num_seats < 10 else f"{prefix}{i:02d}"
                    # gheID = CX00001A1
                    ghe_id = f"{instance.ChuyenXeID}{ma_ghe}"

                    seats_to_create.append(GheNgoi(
                        gheID=ghe_id,
                        ChuyenXe=instance,
                        soGhe=ma_ghe,
                        trangThai="Còn trống"
                    ))

                # 4. Lưu hàng loạt vào DB
                GheNgoi.objects.bulk_create(seats_to_create)
                print(f"==> Đã tự động tạo {num_seats} ghế cho chuyến {instance.ChuyenXeID}")
            else:
                print(f"==> Không tìm thấy thông tin Xe/LoaiXe để tạo ghế cho chuyến {instance.ChuyenXeID}")

        except Exception as e:
            print(f"==> Lỗi tự tạo ghế: {e}")
