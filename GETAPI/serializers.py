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
    khach_hang = serializers.CharField(max_length=12)
    danh_sach_ghe = serializers.ListField(child=serializers.CharField(max_length=5))
    diem_don = serializers.CharField(max_length=500, required=False, allow_blank=True)
    diem_tra = serializers.CharField(max_length=500, required=False, allow_blank=True)
    tong_tien = serializers.DecimalField(max_digits=19, decimal_places=4)

    def validate(self, attrs):
        # 1. Kiểm tra chuyến xe
        try:
            chuyen_xe = ChuyenXe.objects.get(ChuyenXeID=attrs['chuyen_xe'])
            attrs['chuyen_xe_obj'] = chuyen_xe
        except ChuyenXe.DoesNotExist:
            raise serializers.ValidationError("Chuyến xe không tồn tại.")
        
        # 2. Kiểm tra khách hàng
        try:
            user_auth = User_Authentication.objects.get(SoDienThoai=attrs['khach_hang'])
            if not user_auth.KhachHang:
                raise serializers.ValidationError("Tài khoản này chưa có thông tin Khách Hàng.")
            attrs['khach_hang_obj'] = user_auth.KhachHang
            attrs['so_dien_thoai'] = user_auth.SoDienThoai
        except User_Authentication.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy khách hàng với số điện thoại này.")
            
        # 3. Kiểm tra ghế có tồn tại và còn trống hay không
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
        tong_tien = validated_data['tong_tien']
        so_dien_thoai = validated_data['so_dien_thoai']
        
        with transaction.atomic():
            # 1. Tạo VeID duy nhất: VE00001, VE00002...
            last_ve = Ve.objects.all().order_by('VeID').last()
            if not last_ve:
                ve_id = 'VE00001'
            else:
                last_id = last_ve.VeID
                try:
                    last_num = int(last_id[2:]) # Cắt bỏ chữ VE
                    ve_id = f"VE{last_num + 1:05d}"
                except ValueError:
                    ve_id = f"VE{Ve.objects.count() + 1:05d}"
                    
            # Kiểm tra tránh trùng lặp do concurrency (mặc dù hiếm khi dùng transaction level này)
            while Ve.objects.filter(VeID=ve_id).exists():
                last_num += 1
                ve_id = f"VE{last_num:05d}"

            # 2. Tạo một đối tượng Vé duy nhất
            ve = Ve.objects.create(
                VeID=ve_id,
                KhachHang=khach_hang,
                ChuyenXe=chuyen_xe,
                SoDienThoai=so_dien_thoai,
                TongTien=tong_tien,
                TrangThaiThanhToan="Chưa thanh toán",
                TrangThaiDanhGia="Không có quyền",
                DiemDon=diem_don,
                DiemTra=diem_tra
            )
            
            # 3. Cập nhật tất cả các ghế (GheNgoi) đã chọn: đổi trạng thái và liên kết tới Vé vừa tạo
            for ghe in ghe_objs:
                ghe.trangThai = 'Đã đặt'
                ghe.Ve = ve
                ghe.save()
                
        return ve
