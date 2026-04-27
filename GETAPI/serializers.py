from rest_framework import serializers
from .models import (
    KhachHang, Nhaxe, User_Authentication, Taixe, CHITIETTAIXE, 
    Loaixe, CHITIETLOAIXE, Xe, TuyenXe, ChuyenXe, GheNgoi, Ve, VeHuy, ThanhToan, DanhGia
)
from django.db import transaction
from django.utils import timezone
from datetime import datetime, date, time

class KhachHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhachHang
        fields = '__all__'
        
    def create(self, validated_data):
        total_kh = KhachHang.objects.count()
        kh_id = f"KH{total_kh + 1:05d}"
        while KhachHang.objects.filter(KhachHangID=kh_id).exists():
            total_kh += 1
            kh_id = f"KH{total_kh + 1:05d}"
        validated_data['KhachHangID'] = kh_id
        return super().create(validated_data)

class NhaxeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nhaxe
        fields = '__all__'

class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Authentication
        fields = '__all__'

class TaixeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taixe
        fields = '__all__'

class ChiTietTaiXeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CHITIETTAIXE
        fields = '__all__'

class LoaixeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loaixe
        fields = '__all__'

class ChiTietLoaiXeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CHITIETLOAIXE
        fields = '__all__'

class XeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Xe
        fields = '__all__'

class TuyenXeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuyenXe
        fields = '__all__'

class ChuyenXeSerializer(serializers.ModelSerializer):
    # Các trường để ghi (Write)
    Xe = serializers.PrimaryKeyRelatedField(queryset=Xe.objects.all(), required=False)
    TuyenXe = serializers.PrimaryKeyRelatedField(queryset=TuyenXe.objects.all(), required=False)
    Taixe = serializers.PrimaryKeyRelatedField(queryset=Taixe.objects.all(), allow_null=True, required=False)

    # Các trường bổ sung để đọc (Read-only cho Android hiển thị)
    TenNhaXe = serializers.CharField(source='TuyenXe.nhaXe.Tennhaxe', read_only=True)
    TenTuyen = serializers.CharField(source='TuyenXe.tenTuyen', read_only=True)
    GiaVe = serializers.SerializerMethodField()
    LoaiXe = serializers.SerializerMethodField()
    SoChoTrong = serializers.SerializerMethodField()

    class Meta:
        model = ChuyenXe
        fields = [
            'ChuyenXeID', 'Xe', 'TuyenXe', 'Taixe',
            'NgayKhoiHanh', 'GioDi', 'GioDen', 'TrangThai',
            'TenNhaXe', 'GiaVe', 'LoaiXe', 'TenTuyen', 'SoChoTrong'
        ]

    def get_GiaVe(self, obj):
        if obj.Xe and obj.Xe.Loaixe:
            return obj.Xe.Loaixe.GiaVe
        return None

    def get_LoaiXe(self, obj):
        if obj.Xe and obj.Xe.Loaixe:
            return obj.Xe.Loaixe.LoaixeID
        return None

    def get_SoChoTrong(self, obj):
        if obj.Xe and obj.Xe.SoGhe:
            ve_da_dat = Ve.objects.filter(ChuyenXe=obj).count()
            return obj.Xe.SoGhe - ve_da_dat
        return 0

    def to_internal_value(self, data):
        # Đồng bộ với Android: Nếu Android gửi 'LoaiXe' (thực chất là XeID) 
        # và 'TenTuyen' (thực chất là TuyenXeID)
        if 'LoaiXe' in data and not data.get('Xe'):
            data['Xe'] = data['LoaiXe']
        if 'TenTuyen' in data and not data.get('TuyenXe'):
            # Tìm TuyenXe theo tên hoặc ID nếu Android gửi TenTuyen
            tuyen = TuyenXe.objects.filter(tenTuyen=data['TenTuyen']).first()
            if tuyen:
                data['TuyenXe'] = tuyen.tuyenXeID
            else:
                data['TuyenXe'] = data['TenTuyen'] # Giả định đó là ID
        return super().to_internal_value(data)

class GheNgoiSerializer(serializers.ModelSerializer):
    class Meta:
        model = GheNgoi
        fields = '__all__'

class VeSerializer(serializers.ModelSerializer):
    TenTuyen = serializers.CharField(source='ChuyenXe.TuyenXe.tenTuyen', read_only=True)
    TenNhaXe = serializers.CharField(source='ChuyenXe.TuyenXe.nhaXe.Tennhaxe', read_only=True)
    NgayKhoiHanh = serializers.DateField(source='ChuyenXe.NgayKhoiHanh', read_only=True)
    GioDi = serializers.TimeField(source='ChuyenXe.GioDi', read_only=True)
    GiaVe = serializers.SerializerMethodField()
    
    DanhSachGhe = serializers.SerializerMethodField()
    SoLuongGhe = serializers.SerializerMethodField()
    # TrangThaiVe = serializers.SerializerMethodField() # Removed dynamic status calculation

    class Meta:
        model = Ve
        fields = [
            'VeID', 'KhachHang', 'ChuyenXe', 'SoDienThoai', 'TongTien', 
            'TrangThaiThanhToan', 'TrangThaiDanhGia', 'DiemDon', 'DiemTra', 'NgayDat',
            'TenTuyen', 'TenNhaXe', 'NgayKhoiHanh', 'GioDi', 
            'DanhSachGhe', 'SoLuongGhe', 'TrangThai', 'GiaVe' # Replaced TrangThaiVe with TrangThai, Added GiaVe
        ]
        
    def get_GiaVe(self, obj):
        if obj.ChuyenXe and obj.ChuyenXe.Xe and obj.ChuyenXe.Xe.Loaixe:
            return obj.ChuyenXe.Xe.Loaixe.GiaVe
        return None

    def get_DanhSachGhe(self, obj):
        # Truy vấn tất cả các ghế thuộc về vé này
        ghes = GheNgoi.objects.filter(Ve=obj)
        return [ghe.soGhe for ghe in ghes if ghe.soGhe]
        
    def get_SoLuongGhe(self, obj):
        return GheNgoi.objects.filter(Ve=obj).count()

class VeHuySerializer(serializers.ModelSerializer):
    class Meta:
        model = VeHuy
        fields = '__all__'

class ThanhToanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanhToan
        fields = '__all__'

class DanhGiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DanhGia
        fields = '__all__'

class DatVeSerializer(serializers.Serializer):
    ve_id = serializers.CharField(max_length=50) # Nhận VeID từ Android truyền lên
    chuyen_xe = serializers.CharField(max_length=10)
    khach_hang = serializers.CharField(max_length=12)
    danh_sach_ghe = serializers.ListField(child=serializers.CharField(max_length=5))
    diem_don = serializers.CharField(max_length=500, required=False, allow_blank=True)
    diem_tra = serializers.CharField(max_length=500, required=False, allow_blank=True)
    tong_tien = serializers.DecimalField(max_digits=19, decimal_places=4)

    def validate(self, attrs):
        # 1. Kiểm tra VeID đã tồn tại chưa
        if Ve.objects.filter(VeID=attrs['ve_id']).exists():
            raise serializers.ValidationError("Mã vé này đã tồn tại trong hệ thống.")
            
        # 2. Kiểm tra chuyến xe
        try:
            chuyen_xe = ChuyenXe.objects.get(ChuyenXeID=attrs['chuyen_xe'])
            attrs['chuyen_xe_obj'] = chuyen_xe
        except ChuyenXe.DoesNotExist:
            raise serializers.ValidationError("Chuyến xe không tồn tại.")
        
        # 3. Kiểm tra khách hàng
        try:
            user_auth = User_Authentication.objects.get(SoDienThoai=attrs['khach_hang'])
            if not user_auth.KhachHang:
                raise serializers.ValidationError("Tài khoản này chưa có thông tin Khách Hàng.")
            attrs['khach_hang_obj'] = user_auth.KhachHang
            attrs['so_dien_thoai'] = user_auth.SoDienThoai
        except User_Authentication.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy khách hàng với số điện thoại này.")
            
        # 4. Kiểm tra ghế có tồn tại và còn trống hay không
        danh_sach_ghe = attrs['danh_sach_ghe']
        ghe_objs = []
        for so_ghe in danh_sach_ghe:
            try:
                ghe = GheNgoi.objects.get(ChuyenXe=chuyen_xe, soGhe=so_ghe)
                if ghe.trangThai == 'Đã đặt':
                    raise serializers.ValidationError(f"Ghế {so_ghe} đã có người đặt.")
                ghe_objs.append(ghe)
            except GheNgoi.DoesNotExist:
                raise serializers.ValidationError(f"Ghế {so_ghe} không tồn tại trên chuyến xe này.")
        
        attrs['ghe_objs'] = ghe_objs
        return attrs

    def create(self, validated_data):
        ve_id = validated_data['ve_id']
        chuyen_xe = validated_data['chuyen_xe_obj']
        khach_hang = validated_data['khach_hang_obj']
        ghe_objs = validated_data['ghe_objs']
        diem_don = validated_data.get('diem_don', '')
        diem_tra = validated_data.get('diem_tra', '')
        tong_tien = validated_data['tong_tien']
        so_dien_thoai = validated_data['so_dien_thoai']
        
        with transaction.atomic():
            # 1. Tạo một đối tượng Vé duy nhất với ID lấy từ app Android
            ve = Ve.objects.create(
                VeID=ve_id,
                KhachHang=khach_hang,
                ChuyenXe=chuyen_xe,
                SoDienThoai=so_dien_thoai,
                TongTien=tong_tien,
                TrangThaiThanhToan="Chưa thanh toán",
                TrangThaiDanhGia="Không có quyền",
                TrangThai="Đã đặt", # Thiết lập trạng thái mặc định
                DiemDon=diem_don,
                DiemTra=diem_tra
            )
            
            # 2. Cập nhật tất cả các ghế (GheNgoi) đã chọn: đổi trạng thái và liên kết tới Vé vừa tạo
            for ghe in ghe_objs:
                ghe.trangThai = 'Đã đặt'
                ghe.Ve = ve
                ghe.save()
                
        return ve

class HuyVeSerializer(serializers.Serializer):
    ve_id = serializers.CharField(max_length=50)

    def validate_ve_id(self, value):
        try:
            ve = Ve.objects.get(VeID=value)
            return ve
        except Ve.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy vé với ID này.")

    def save(self):
        ve = self.validated_data['ve_id']
        with transaction.atomic():
            # 1. Tách Ghế và Chuyến để sinh ID hủy rút gọn
            seat_part = ve.VeID.split("CX")[0] if "CX" in ve.VeID else "G"
            trip_num = "".join(filter(str.isdigit, ve.ChuyenXe.ChuyenXeID))[-4:] # Lấy 4 số cuối
            prefix = f"H{seat_part}{trip_num}"
            
            # Đếm số lần hủy để tránh trùng ID trong bảng VeHuy
            cancel_count = VeHuy.objects.filter(VeHuyID__startswith=prefix).count()
            new_id = f"{prefix}{cancel_count + 1}"[:10] # Đảm bảo max 10 ký tự

            # 2. Tạo bản ghi VeHuy (Lưu chuỗi ghế comma-separated)
            ghes = GheNgoi.objects.filter(Ve=ve)
            danh_sach_ghe_str = ", ".join([g.soGhe for g in ghes if g.soGhe])
            
            VeHuy.objects.create(
                VeHuyID=new_id,
                KhachHang=ve.KhachHang,
                ChuyenXe=ve.ChuyenXe,
                SoDienThoai=ve.SoDienThoai,
                NgayDat=ve.NgayDat,
                TongTien=ve.TongTien,
                TrangThaiThanhToan=ve.TrangThaiThanhToan,
                TrangThaiDanhGia=ve.TrangThaiDanhGia,
                TrangThai="Đã hủy",
                DiemDon=ve.DiemDon,
                DiemTra=ve.DiemTra,
                DanhSachGhe=danh_sach_ghe_str,
                SoLuongGhe=ghes.count()
            )

            # 3. Giải phóng ghế trong bảng ghengoi
            ghes.update(trangThai='Còn trống', Ve=None)

            # 4. Xóa vé cũ để giải phóng ID Ghế+Chuyến
            ve.delete()
        return {"message": "Success"}
