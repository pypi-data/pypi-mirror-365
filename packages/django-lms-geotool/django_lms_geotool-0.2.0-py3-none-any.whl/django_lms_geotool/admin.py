from django.contrib import admin
from .models import AffineMatrix, Anchor
from django.http import JsonResponse
from simpleui.admin import AjaxAdmin
from django.utils.html import format_html
from .tools.matrix import affine_matrix
from import_export.admin import ImportExportModelAdmin


class ChoiceInline(admin.TabularInline):
    model = Anchor
    extra = 0


@admin.register(AffineMatrix)
class AffineMatrixAdmin(AjaxAdmin, ImportExportModelAdmin):
    list_display = ("mapid", "name", "floor", "matrix_html")

    def get_matrix(self, obj):
        if obj.matrix:
            res = f"<span title='{obj.matrix}'>转换矩阵</span>"
            return format_html(res)
        else:
            res = f"<span style='color:red'>暂未转换</span>"
            return format_html(res)

    def matrix_html(self, obj):
        if obj.matrix:
            res = f"<a href='/geotool/matrix?mapid={obj.mapid}'>查看</a>"
            return format_html(res)
        else:
            res = f"<span style='color:red'>暂未转换</span>"
            return format_html(res)

    matrix_html.short_description = '矩阵计算'

    fieldsets = [
        ("地图信息", {"fields": ["mapid", "name", "floor"]}),
    ]

    inlines = [ChoiceInline]

    actions = ('calc_button',)

    def calc_button(self, request, queryset):
        for each in queryset:
            try:
                anchors = each.anchor.all()
                source_data = [[each.origin_x, each.origin_y] for each in anchors]
                target_data = [[each.target_x, each.target_y] for each in anchors]
                matrix_result = affine_matrix(source_data, target_data)
                each.matrix = matrix_result
                each.save()
            except Exception as e:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': f'{e}'
                })

    calc_button.short_description = '矩阵计算'
    calc_button.icon = 'fas fa-circle-play'
    calc_button.type = 'success'
    calc_button.style = 'color:black;'

    calc_button.layer = {
        'title': '矩阵计算',
        'tips': '请确认所有地图都配置了点位信息',
        'confirm_button': '提交',
        'cancel_button': '取消',
        'width': '50%',
        'labelWidth': "80px",
    }

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
