from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    KhachHang, Nhaxe, User_Authentication, Taixe, CHITIETTAIXE, 
    Loaixe, CHITIETLOAIXE, Xe, TuyenXe, ChuyenXe, GheNgoi, Ve, ThanhToan, DanhGia
)
from .serializers import (
    KhachHangSerializer, NhaxeSerializer, UserAuthenticationSerializer, 
    TaixeSerializer, ChiTietTaiXeSerializer, LoaixeSerializer, 
    ChiTietLoaiXeSerializer, XeSerializer, TuyenXeSerializer, 
    ChuyenXeSerializer, GheNgoiSerializer, VeSerializer, 
    ThanhToanSerializer, DanhGiaSerializer, DatVeSerializer
)

class DanhSachVeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        khach_hang_id = request.query_params.get('khach_hang_id')
        trang_thai = request.query_params.get('trang_thai')

        if not khach_hang_id:
            return Response({"error": "Thiếu tham số khach_hang_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Truy vấn vé theo khách hàng
        queryset = Ve.objects.filter(KhachHang__KhachHangID=khach_hang_id)

        # Nếu có truyền trạng thái thì lọc thêm
        if trang_thai:
            queryset = queryset.filter(TrangThai=trang_thai)

        # Sắp xếp vé mới nhất lên đầu
        queryset = queryset.order_by('-NgayDat')

        serializer = VeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DatVeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DatVeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Tạo vé thông qua hàm create trong Serializer
                ve = serializer.save()
                
                # Format kết quả
                ve_serializer = VeSerializer(ve)
                return Response({
                    "message": "Đặt vé thành công.",
                    "data": ve_serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Nếu có lỗi khi lưu (ở block transaction.atomic)
                return Response({
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
