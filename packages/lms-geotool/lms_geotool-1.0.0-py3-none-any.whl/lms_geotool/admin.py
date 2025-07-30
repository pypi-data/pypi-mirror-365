from django.contrib import admin
from .models import AffineMatrix, Anchor
from django.utils.html import format_html
from .tools.matrix import affine_matrix
from django.http import JsonResponse
from django.urls import reverse


class ChoiceInline(admin.TabularInline):
    model = Anchor
    extra = 0


@admin.action(description="仿射变换")
def make_published(modeladmin, request, queryset):
    try:
        for each in queryset:
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


@admin.register(AffineMatrix)
class AffineMatrixAdmin(admin.ModelAdmin):
    list_display = ("mapid", "name", "floor", "matrix_html")
    actions = [make_published]

    def matrix_html(self, obj):
        if obj.matrix:
            path = reverse("matrix")
            full_url = f"{path}?mapid={obj.mapid}"
            res = f'<a href="{full_url}">查看</a>'
            # res = f"<a href='/geotool/matrix?mapid={obj.mapid}'>查看</a>"
            return format_html(res)
        else:
            res = f"<span style='color:red'>暂未转换</span>"
            return format_html(res)

    matrix_html.short_description = '矩阵计算'

    fieldsets = [
        ("地图信息", {"fields": ["mapid", "name", "floor"]}),
    ]

    inlines = [ChoiceInline]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
