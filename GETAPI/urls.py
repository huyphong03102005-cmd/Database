from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    KhachHangViewSet, NhaxeViewSet, UserAuthenticationViewSet, 
    TaixeViewSet, ChiTietTaiXeViewSet, LoaixeViewSet, 
    ChiTietLoaiXeViewSet, XeViewSet, TuyenXeViewSet, 
    ChuyenXeViewSet, GheNgoiViewSet, VeViewSet, 
    ThanhToanViewSet, DanhGiaViewSet, DatVeAPIView, DanhSachVeAPIView
)

router = DefaultRouter()
router.register(r'khachhang', KhachHangViewSet)
router.register(r'nhaxe', NhaxeViewSet)
router.register(r'user-auth', UserAuthenticationViewSet)
router.register(r'taixe', TaixeViewSet)
router.register(r'chitiettaixe', ChiTietTaiXeViewSet)
router.register(r'loaixe', LoaixeViewSet)
router.register(r'chitietloaixe', ChiTietLoaiXeViewSet)
router.register(r'xe', XeViewSet)
router.register(r'tuyenxe', TuyenXeViewSet)
router.register(r'chuyenxe', ChuyenXeViewSet)
router.register(r'ghengoi', GheNgoiViewSet)
router.register(r've', VeViewSet)
router.register(r'thanhtoan', ThanhToanViewSet)
router.register(r'danhgia', DanhGiaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dat-ve/', DatVeAPIView.as_view(), name='dat_ve_api'),
    path('ve/danh-sach/', DanhSachVeAPIView.as_view(), name='danh_sach_ve_api'),
]
