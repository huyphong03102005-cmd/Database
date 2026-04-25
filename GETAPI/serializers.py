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

    TenNhaXe = serializers.CharField(
        source='TuyenXe.nhaXe.Tennhaxe',
        read_only=True
    )

    TenTuyen = serializers.CharField(
        source='TuyenXe.tenTuyen',
        read_only=True
    )

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
