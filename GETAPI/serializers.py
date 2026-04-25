from rest_framework import serializers
from .models import (
    KhachHang, Nhaxe, User_Authentication, Taixe, CHITIETTAIXE, 
    Loaixe, CHITIETLOAIXE, Xe, TuyenXe, ChuyenXe, GheNgoi, Ve, ThanhToan, DanhGia
)
from django.db import transaction

class KhachHangSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhachHang
        fields = '__all__'

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

# Trong serializers.py của project Django
class ChuyenXeSerializer(serializers.ModelSerializer):
    # Lấy tên từ các bảng liên quan (Related Fields)
    TenNhaXe = serializers.CharField(source='TuyenXe.nhaXe.Tennhaxe', read_only=True)
    TenTuyen = serializers.CharField(source='TuyenXe.tenTuyen', read_only=True)
    
    # Sử dụng SerializerMethodField để xử lý an toàn trường hợp Xe là NULL
    GiaVe = serializers.SerializerMethodField()
    LoaiXe = serializers.SerializerMethodField()
    SoChoTrong = serializers.SerializerMethodField()

    class Meta:
        model = ChuyenXe
        # Đảm bảo các tên trường ở đây KHỚP với @SerializedName trong Android
        fields = ['ChuyenXeID', 'NgayKhoiHanh', 'GioDi', 'GioDen',
                  'TenNhaXe', 'GiaVe', 'LoaiXe', 'TenTuyen', 'SoChoTrong']
    
    def get_GiaVe(self, obj):
        if obj.Xe and getattr(obj.Xe, 'loaiXeID', None):
            return obj.Xe.loaiXeID.GiaVe
        elif obj.Xe and getattr(obj.Xe, 'Loaixe', None):
            return obj.Xe.Loaixe.GiaVe
        return None # Trả về null nếu không có Xe hoặc Loaixe

    def get_LoaiXe(self, obj):
        if obj.Xe and getattr(obj.Xe, 'loaiXeID', None):
            return obj.Xe.loaiXeID.LoaixeID
        elif obj.Xe and getattr(obj.Xe, 'Loaixe', None):
             return obj.Xe.Loaixe.LoaixeID
        return None # Trả về null nếu không có Xe hoặc Loaixe

    def get_SoChoTrong(self, obj):
        so_ghe = getattr(obj.Xe, 'soGhe', None) or getattr(obj.Xe, 'SoGhe', None)
        if obj.Xe and so_ghe:
            ve_da_dat = Ve.objects.filter(ChuyenXe=obj).count()
            return so_ghe - ve_da_dat
        return 0 # Trả về 0 nếu không có thông tin về xe

class GheNgoiSerializer(serializers.ModelSerializer):
    class Meta:
        model = GheNgoi
        fields = '__all__'

class VeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ve
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
    chuyen_xe = serializers.CharField(max_length=10)
    khach_hang = serializers.CharField(max_length=12) # Số điện thoại
    danh_sach_ghe = serializers.ListField(
        child=serializers.CharField(max_length=5)
    )
    diem_don = serializers.CharField(max_length=500, required=False, allow_blank=True)
    diem_tra = serializers.CharField(max_length=500, required=False, allow_blank=True)
    tong_tien = serializers.DecimalField(max_digits=19, decimal_places=4)

    def validate(self, attrs):
        # 1. Kiểm tra chuyến xe tồn tại
        try:
            chuyen_xe = ChuyenXe.objects.get(ChuyenXeID=attrs['chuyen_xe'])
            attrs['chuyen_xe_obj'] = chuyen_xe
        except ChuyenXe.DoesNotExist:
            raise serializers.ValidationError("Chuyến xe không tồn tại.")
        
        # 2. Kiểm tra khách hàng tồn tại qua SDT trong User_Authentication
        try:
            user_auth = User_Authentication.objects.get(SoDienThoai=attrs['khach_hang'])
            if not user_auth.KhachHang:
                raise serializers.ValidationError("Tài khoản này chưa có thông tin Khách Hàng.")
            attrs['khach_hang_obj'] = user_auth.KhachHang
            attrs['so_dien_thoai'] = user_auth.SoDienThoai
        except User_Authentication.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy khách hàng với số điện thoại này.")
            
        # 3. Kiểm tra danh sách ghế
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
        chuyen_xe = validated_data['chuyen_xe_obj']
        khach_hang = validated_data['khach_hang_obj']
        ghe_objs = validated_data['ghe_objs']
        diem_don = validated_data.get('diem_don', '')
        diem_tra = validated_data.get('diem_tra', '')
        gia_ve = validated_data['tong_tien'] / len(ghe_objs)
        so_dien_thoai = validated_data['so_dien_thoai']
        
        danh_sach_ve_tao = []
        
        with transaction.atomic():
            for ghe in ghe_objs:
                # Tự động tạo VeID: lấy số lượng vé hiện có + 1
                total_ve = Ve.objects.count()
                ve_id = f"VE{total_ve + 1:04d}" # VD: VE0001, VE0002...
                # Đảm bảo VeID là duy nhất trong trường hợp request đồng thời
                while Ve.objects.filter(VeID=ve_id).exists():
                    total_ve += 1
                    ve_id = f"VE{total_ve + 1:04d}"
                
                # Tạo vé mới
                ve = Ve.objects.create(
                    VeID=ve_id,
                    KhachHang=khach_hang,
                    ChuyenXe=chuyen_xe,
                    Ghe=ghe,
                    SoDienThoai=so_dien_thoai,
                    GiaVe=gia_ve,
                    TrangThai="Hiện tại",
                    TrangThaiThanhToan="Chưa thanh toán",
                    TrangThaiDanhGia="Không có quyền",
                    DiemDon=diem_don,
                    DiemTra=diem_tra
                )
                
                # Cập nhật trạng thái ghế
                ghe.trangThai = 'Đã đặt'
                ghe.Ve = ve
                ghe.save()
                
                danh_sach_ve_tao.append(ve)
                
        return danh_sach_ve_tao
