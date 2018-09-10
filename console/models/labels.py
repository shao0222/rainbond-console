# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from django.db import models
from django.db.models.fields.files import FileField

logger = logging.getLogger("default")

app_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
plugin_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
user_identity = ((u"管理员", "admin"),)
tenant_type = ((u"免费租户", "free"), (u"付费租户", "payed"))
user_origion = ((u"自主注册", "registration"), (u"邀请注册", "invitation"))
extend_method = ((u"不伸缩", 'stateless'), (u"垂直伸缩", 'vertical'))
pay_method = ((u'预付费提前采购', "prepaid"), (u'按使用后付费', "postpaid"))


class BaseModel(models.Model):
    class Meta:
        abstract = True

    ID = models.AutoField(primary_key=True, max_length=10)

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(f, FileField):
                value = value.url if value else None
            data[f.name] = value
        return data


class ServiceLabels(BaseModel):
    class Meta:
        db_table = "service_labels"

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    label_id = models.CharField(max_length=32, help_text=u"标签id")
    region = models.CharField(max_length=30, help_text=u"区域中心")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")


class NodeLabels(BaseModel):
    class Meta:
        db_table = "node_labels"

    region_id = models.CharField(max_length=32, help_text=u"数据中心 id")
    cluster_id = models.CharField(max_length=32, help_text=u"集群ID")
    node_uuid = models.CharField(max_length=36, help_text=u"节点uuid")
    label_id = models.CharField(max_length=32, help_text=u"标签id")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")


class Labels(BaseModel):
    class Meta:
        db_table = "labels"

    label_id = models.CharField(max_length=32, help_text=u"标签id")
    label_name = models.CharField(max_length=128, help_text=u"标签名(汉语拼音)")
    label_alias = models.CharField(max_length=15, help_text=u"标签名(汉字)")
    category = models.CharField(max_length=20, default="", help_text=u"标签分类")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")


