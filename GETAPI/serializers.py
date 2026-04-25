from rest_framework import serializers
from .models import (
    KhachHang, Nhaxe, User_Authentication, Taixe, CHITIETTAIXE, 
    Loaixe, CHITIETLOAIXE, Xe, TuyenXe, ChuyenXe, GheNgoi, Ve, ThanhToan, DanhGia
)

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
    TenNhaXe = serializers.CharField(source='TuyenXe.nhaXe.tenNhaXe', read_only=True)
    GiaVe = serializers.CharField(source='Xe.Loaixe.giaVe', read_only=True)
    LoaiXe = serializers.CharField(source='Xe.Loaixe.tenLoai', read_only=True)
    TenTuyen = serializers.CharField(source='TuyenXe.tenTuyen', read_only=True)
    # tính số chỗ trống bằng tổng chỗ - vé đã đặt
    SoChoTrong = serializers.IntegerField(default=10, read_only=True)

    class Meta:
        model = ChuyenXe
        # Đảm bảo các tên trường ở đây KHỚP với @SerializedName trong Android
        fields = ['ChuyenXeID', 'NgayKhoiHanh', 'GioDi', 'GioDen',
                  'TenNhaXe', 'GiaVe', 'LoaiXe', 'TenTuyen', 'SoChoTrong']

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
