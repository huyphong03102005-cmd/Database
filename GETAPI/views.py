from rest_framework import viewsets
from .models import (
    KhachHang, Nhaxe, User_Authentication, Taixe, CHITIETTAIXE, 
    Loaixe, CHITIETLOAIXE, Xe, TuyenXe, ChuyenXe, GheNgoi, Ve, ThanhToan, DanhGia
)
from .serializers import (
    KhachHangSerializer, NhaxeSerializer, UserAuthenticationSerializer, 
    TaixeSerializer, ChiTietTaiXeSerializer, LoaixeSerializer, 
    ChiTietLoaiXeSerializer, XeSerializer, TuyenXeSerializer, 
    ChuyenXeSerializer, GheNgoiSerializer, VeSerializer, 
    ThanhToanSerializer, DanhGiaSerializer
)

class KhachHangViewSet(viewsets.ModelViewSet):
    queryset = KhachHang.objects.all()
    serializer_class = KhachHangSerializer

class NhaxeViewSet(viewsets.ModelViewSet):
    queryset = Nhaxe.objects.all()
    serializer_class = NhaxeSerializer

class UserAuthenticationViewSet(viewsets.ModelViewSet):
    queryset = User_Authentication.objects.all()
    serializer_class = UserAuthenticationSerializer

class TaixeViewSet(viewsets.ModelViewSet):
    queryset = Taixe.objects.all()
    serializer_class = TaixeSerializer

class ChiTietTaiXeViewSet(viewsets.ModelViewSet):
    queryset = CHITIETTAIXE.objects.all()
    serializer_class = ChiTietTaiXeSerializer

class LoaixeViewSet(viewsets.ModelViewSet):
    queryset = Loaixe.objects.all()
    serializer_class = LoaixeSerializer

class ChiTietLoaiXeViewSet(viewsets.ModelViewSet):
    queryset = CHITIETLOAIXE.objects.all()
    serializer_class = ChiTietLoaiXeSerializer

class XeViewSet(viewsets.ModelViewSet):
    queryset = Xe.objects.all()
    serializer_class = XeSerializer

class TuyenXeViewSet(viewsets.ModelViewSet):
    queryset = TuyenXe.objects.all()
    serializer_class = TuyenXeSerializer

class ChuyenXeViewSet(viewsets.ModelViewSet):
    queryset = ChuyenXe.objects.all()
    serializer_class = ChuyenXeSerializer

class GheNgoiViewSet(viewsets.ModelViewSet):
    queryset = GheNgoi.objects.all()
    serializer_class = GheNgoiSerializer

class VeViewSet(viewsets.ModelViewSet):
    queryset = Ve.objects.all()
    serializer_class = VeSerializer

class ThanhToanViewSet(viewsets.ModelViewSet):
    queryset = ThanhToan.objects.all()
    serializer_class = ThanhToanSerializer

class DanhGiaViewSet(viewsets.ModelViewSet):
    queryset = DanhGia.objects.all()
    serializer_class = DanhGiaSerializer
