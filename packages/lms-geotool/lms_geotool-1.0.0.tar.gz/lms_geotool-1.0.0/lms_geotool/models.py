from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AffineMatrix(models.Model):
    mapid = models.CharField(max_length=20, unique=True, verbose_name="地图编码")
    name = models.CharField(max_length=20, unique=False, verbose_name="地图名称")
    floor = models.IntegerField(default=1, unique=False, verbose_name="楼层")
    matrix = models.CharField(max_length=200, editable=False, verbose_name="转换矩阵")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='map_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='map_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "地图信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Anchor(models.Model):
    map = models.ForeignKey(AffineMatrix, on_delete=models.CASCADE, related_name="anchor", verbose_name="地图信息")
    origin_x = models.FloatField(default=0, verbose_name="原坐标x")
    origin_y = models.FloatField(default=0, verbose_name="原坐标y")
    target_x = models.FloatField(default=0, verbose_name="目标坐标x")
    target_y = models.FloatField(default=0, verbose_name="目标坐标y")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='anchor_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='anchor_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "锚点信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return ""
