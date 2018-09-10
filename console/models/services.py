# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from django.db import models
from django.db.models.fields.files import FileField
from django.db.models.fields import DateTimeField
from .main import Users
from .fields import GrOptionsCharField
from django.conf import settings
from console.utils.crypt import make_uuid


logger = logging.getLogger("default")

app_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
plugin_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
user_identity = ((u"管理员", "admin"),)
tenant_type = ((u"免费租户", "free"), (u"付费租户", "payed"))
user_origion = ((u"自主注册", "registration"), (u"邀请注册", "invitation"))
extend_method = ((u"不伸缩", 'stateless'), (u"垂直伸缩", 'vertical'))
pay_method = ((u'预付费提前采购', "prepaid"), (u'按使用后付费', "postpaid"))
service_status = ((u"已发布", 'published'), (u"测试中", "test"),)
group_publish_type = (
    ('services_group', u'应用组'), ("cloud_frame", u'云框架'),
)
pay_status = ((u"已发布", 'payed'), (u"测试中", "unpayed"),)
app_status = (
    ('show', u'显示'), ("hidden", u'隐藏'),
)


def logo_path(instance, filename):
    suffix = filename.split('.')[-1]
    return '{0}/logo/{1}.{2}'.format(settings.MEDIA_ROOT, make_uuid(), suffix)


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


class ServiceShareRecord(BaseModel):
    """应用分享记录"""

    class Meta:
        db_table = "service_share_record"

    group_share_id = models.CharField(max_length=32, unique=True, help_text=u"发布应用组或插件的唯一Key")
    group_id = models.CharField(max_length=32, help_text=u"分享应用组id或者单独插件ID")
    team_name = models.CharField(max_length=32, help_text=u"应用所在团队唯一名称")
    event_id = models.CharField(max_length=32, help_text=u"介质同步事件ID,弃用，使用表service_share_record_event")
    share_version = models.CharField(max_length=15, help_text=u"应用组发布版本")
    is_success = models.BooleanField(default=False, help_text=u"发布是否成功")
    step = models.IntegerField(default=0, help_text=u"当前发布进度")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text=u"更新时间")

    def __unicode__(self):
        return self.to_dict()


class ServiceShareRecordEvent(BaseModel):
    """应用分享订单关联发布事件"""

    class Meta:
        db_table = "service_share_record_event"

    record_id = models.IntegerField(help_text=u"关联的订单ID")
    region_share_id = models.CharField(max_length=36, help_text=u"应用数据中心分享反馈ID")
    team_name = models.CharField(max_length=32, help_text=u"应用所在团队唯一名称")
    service_key = models.CharField(max_length=32, help_text=u"对应应用key")
    service_id = models.CharField(max_length=32, help_text=u"对应应用ID")
    service_alias = models.CharField(max_length=10, help_text=u"对应应用别名")
    service_name = models.CharField(max_length=32, help_text=u"对应应用名称")
    team_id = models.CharField(max_length=32, help_text=u"对应所在团队ID")
    event_id = models.CharField(max_length=32, default="", help_text=u"介质同步事件ID")
    event_status = models.CharField(max_length=32, default="not_start", help_text=u"事件状态")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text=u"更新时间")

    def __unicode__(self):
        return self.to_dict()


class ServiceSourceInfo(BaseModel):
    """应用源信息"""

    class Meta:
        db_table = "service_source_info"

    service_id = models.CharField(max_length=32, help_text=u"服务ID")
    team_id = models.CharField(max_length=32, help_text=u"服务所在团队ID")
    user_name = models.CharField(max_length=32, null=True, blank=True, help_text=u"用户名")
    password = models.CharField(max_length=32, null=True, blank=True, help_text=u"密码")
    extend_info = models.CharField(max_length=1024, null=True, blank=True, default="", help_text=u"扩展信息")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")


class ServiceRecycleBin(BaseModel):
    """应用回收"""
    class Meta:
        db_table = 'service_recycle_bin'
        unique_together = ('tenant_id', 'service_alias')

    service_id = models.CharField(
        max_length=32, unique=True, help_text=u"服务id")
    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_key = models.CharField(max_length=32, help_text=u"服务key")
    service_alias = models.CharField(max_length=100, help_text=u"服务别名")
    service_cname = models.CharField(
        max_length=100, default='', help_text=u"服务名")
    service_region = models.CharField(max_length=15, help_text=u"服务所属区")
    desc = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"描述")
    category = models.CharField(
        max_length=15, help_text=u"服务分类：application,cache,store")
    service_port = models.IntegerField(help_text=u"服务端口", default=0)
    is_web_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否web服务")
    version = models.CharField(max_length=20, help_text=u"版本")
    update_version = models.IntegerField(default=1, help_text=u"内部发布次数")
    image = models.CharField(max_length=100, help_text=u"镜像")
    cmd = models.CharField(
        max_length=2048, null=True, blank=True, help_text=u"启动参数")
    setting = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"设置项")
    extend_method = models.CharField(
        max_length=15,
        default='stateless',
        help_text=u"伸缩方式")
    env = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"环境变量")
    min_node = models.IntegerField(help_text=u"启动个数", default=1)
    min_cpu = models.IntegerField(help_text=u"cpu个数", default=500)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=256)
    inner_port = models.IntegerField(help_text=u"内部端口", default=0)
    volume_mount_path = models.CharField(
        max_length=50, null=True, blank=True, help_text=u"mount目录")
    host_path = models.CharField(
        max_length=300, null=True, blank=True, help_text=u"mount目录")
    deploy_version = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"部署版本")
    code_from = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"代码来源:gitlab,github")
    git_url = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"code代码仓库")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    git_project_id = models.IntegerField(help_text=u"gitlab 中项目id", default=0)
    is_code_upload = models.BooleanField(
        default=False, blank=True, help_text=u"是否上传代码")
    code_version = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"代码版本")
    service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    creater = models.IntegerField(help_text=u"服务创建者", default=0)
    language = models.CharField(
        max_length=40, null=True, blank=True, help_text=u"代码语言")
    protocol = models.CharField(
        max_length=15, default='', help_text=u"服务协议：http,stream")
    total_memory = models.IntegerField(help_text=u"内存使用M", default=0)
    is_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否inner服务")
    namespace = models.CharField(
        max_length=100, default='', help_text=u"镜像发布云帮的区间")

    volume_type = models.CharField(
        max_length=15, default='shared', help_text=u"共享类型shared、exclusive")
    port_type = models.CharField(
        max_length=15,
        default='multi_outer',
        help_text=u"端口类型，one_outer;dif_protocol;multi_outer")
    # 服务创建类型,cloud、assistant
    service_origin = models.CharField(
        max_length=15,
        default='assistant',
        help_text=u"服务创建类型cloud云市服务,assistant云帮服务")
    expired_time = models.DateTimeField(null=True, help_text=u"过期时间")
    tenant_service_group_id = models.IntegerField(default=0, help_text=u"应用归属的服务组id")

    service_source = models.CharField(max_length=15, default="", null=True, blank=True,
                                      help_text=u"应用来源(source_code, market, docker_run, docker_compose)")
    create_status = models.CharField(max_length=15, null=True, blank=True, help_text=u"应用创建状态 creating|complete")
    update_time = models.DateTimeField(auto_now_add=True, blank=True, help_text=u"更新时间")
    check_uuid = models.CharField(
        max_length=36, blank=True, null=True, default="", help_text=u"应用检测ID")
    check_event_id = models.CharField(
        max_length=32, blank=True, null=True, default="", help_text=u"应用检测事件ID")
    docker_cmd = models.CharField(
        max_length=1024, null=True, blank=True, help_text=u"镜像创建命令")


class ServiceRelationRecycleBin(BaseModel):
    """应用关系回收"""
    class Meta:
        db_table = 'service_relation_recycle_bin'
        unique_together = ('service_id', 'dep_service_id')

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    dep_service_id = models.CharField(max_length=32, help_text=u"依赖服务id")
    dep_service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    dep_order = models.IntegerField(help_text=u"依赖顺序")


class ServiceRelPerms(BaseModel):
    """用户在应用下的权限"""

    class Meta:
        db_table = 'service_user_perms'

    user_id = models.IntegerField(help_text=u"用户id")
    service_id = models.IntegerField(help_text=u"服务id")
    perm_id = models.IntegerField(help_text=u'权限id')

    def __unicode__(self):
        return self.to_dict()


class TenantServiceInfo(BaseModel):
    """应用"""
    class Meta:
        db_table = 'service'
        unique_together = ('tenant_id', 'service_alias')

    service_id = models.CharField(
        max_length=32, unique=True, help_text=u"服务id")
    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_key = models.CharField(max_length=32, help_text=u"服务key")
    service_alias = models.CharField(max_length=100, help_text=u"服务别名")
    service_cname = models.CharField(
        max_length=100, default='', help_text=u"服务名")
    service_region = models.CharField(max_length=15, help_text=u"服务所属区")
    desc = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"描述")
    category = models.CharField(
        max_length=15, help_text=u"服务分类：application,cache,store")
    service_port = models.IntegerField(help_text=u"服务端口", default=0)
    is_web_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否web服务")
    version = models.CharField(max_length=20, help_text=u"版本")
    update_version = models.IntegerField(default=1, help_text=u"内部发布次数")
    image = models.CharField(max_length=100, help_text=u"镜像")
    cmd = models.CharField(
        max_length=2048, null=True, blank=True, help_text=u"启动参数")
    setting = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"设置项")
    extend_method = models.CharField(
        max_length=15,
        choices=extend_method,
        default='stateless',
        help_text=u"伸缩方式")
    env = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"环境变量")
    min_node = models.IntegerField(help_text=u"启动个数", default=1)
    min_cpu = models.IntegerField(help_text=u"cpu个数", default=500)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=256)
    inner_port = models.IntegerField(help_text=u"内部端口", default=0)
    volume_mount_path = models.CharField(
        max_length=50, null=True, blank=True, help_text=u"mount目录")
    host_path = models.CharField(
        max_length=300, null=True, blank=True, help_text=u"mount目录")
    deploy_version = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"部署版本")
    code_from = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"代码来源:gitlab,github")
    git_url = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"code代码仓库")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    git_project_id = models.IntegerField(help_text=u"gitlab 中项目id", default=0)
    is_code_upload = models.BooleanField(
        default=False, blank=True, help_text=u"是否上传代码")
    code_version = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"代码版本")
    service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    creater = models.IntegerField(help_text=u"服务创建者", default=0)
    language = models.CharField(
        max_length=40, null=True, blank=True, help_text=u"代码语言")
    protocol = models.CharField(
        max_length=15, default='', help_text=u"服务协议：http,stream")
    total_memory = models.IntegerField(help_text=u"内存使用M", default=0)
    is_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否inner服务")
    namespace = models.CharField(
        max_length=100, default='', help_text=u"镜像发布云帮的区间")

    volume_type = models.CharField(
        max_length=15, default='shared', help_text=u"共享类型shared、exclusive")
    port_type = models.CharField(
        max_length=15,
        default='multi_outer',
        help_text=u"端口类型，one_outer;dif_protocol;multi_outer")
    # 服务创建类型,cloud、assistant
    service_origin = models.CharField(
        max_length=15,
        default='assistant',
        help_text=u"服务创建类型cloud云市服务,assistant云帮服务")
    expired_time = models.DateTimeField(null=True, help_text=u"过期时间")
    tenant_service_group_id = models.IntegerField(default=0, help_text=u"应用归属的服务组id")

    service_source = models.CharField(max_length=15, default="", null=True, blank=True,
                                      help_text=u"应用来源(source_code, market, docker_run, docker_compose)")
    create_status = models.CharField(max_length=15, null=True, blank=True, help_text=u"应用创建状态 creating|complete")
    update_time = models.DateTimeField(auto_now_add=True, blank=True, help_text=u"更新时间")
    check_uuid = models.CharField(
        max_length=36, blank=True, null=True, default="", help_text=u"应用检测ID")
    check_event_id = models.CharField(
        max_length=32, blank=True, null=True, default="", help_text=u"应用检测事件ID")
    docker_cmd = models.CharField(
        max_length=1024, null=True, blank=True, help_text=u"镜像创建命令")
    open_webhooks = models.BooleanField(default=False, help_text=u'是否开启自动触发部署功能')
    secret = models.CharField(max_length=64, null=True, blank=True, help_text=u"webhooks验证密码")
    server_type = models.CharField(
        max_length=5, default='git', help_text=u"源码仓库类型")

    def __unicode__(self):
        return self.service_alias

    def toJSON(self):
        data = {}
        for f in self._meta.fields:
            obj = getattr(self, f.name)
            if type(f.name) == DateTimeField:
                data[f.name] = obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                data[f.name] = obj
        return data

    @property
    def clone_url(self):
        if self.code_from == "github":
            code_user = self.git_url.split("/")[3]
            code_project_name = self.git_url.split("/")[4].split(".")[0]
            createUser = Users.objects.get(user_id=self.creater)
            git_url = "https://" + createUser.github_token + "@github.com/" + code_user + "/" + code_project_name + ".git"
            return git_url
        else:
            return self.git_url

    def is_slug(self):
        # return bool(self.image.startswith('goodrain.me/runner'))
        return bool(self.image.endswith('/runner')) or bool(
            '/runner:' in self.image)


class ServiceDomain(BaseModel):
    """应用域名"""
    class Meta:
        db_table = 'service_domain'

    service_id = models.CharField(max_length=32, help_text=u"服务id")
    service_name = models.CharField(max_length=32, help_text=u"服务名")
    domain_name = models.CharField(max_length=256, help_text=u"域名")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    container_port = models.IntegerField(default=0, help_text=u"容器端口")
    protocol = models.CharField(max_length=15, default='http', help_text=u"域名类型 http https httptphttps httpandhttps")
    certificate_id = models.IntegerField(default=0, help_text=u'证书ID')
    domain_type = models.CharField(max_length=20, default='www', help_text=u"服务域名类型")

    def __unicode__(self):
        return self.domain_name


class ServiceDomainCertificate(BaseModel):
    """应用域名证书"""
    class Meta:
        db_table = 'service_domain_certificate'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    private_key = models.TextField(default='', help_text=u"证书key")
    certificate = models.TextField(default='', help_text=u'证书')
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    alias = models.CharField(max_length=32, help_text=u"证书别名")

    def __unicode__(self):
        return "private_key:{} certificate:{}".format(self.private_key, self.certificate)


class ServiceAttachInfo(BaseModel):
    """应用配套信息"""

    class Meta:
        db_table = 'service_attach_info'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    memory_pay_method = models.CharField(max_length=32, choices=pay_method)
    disk_pay_method = models.CharField(max_length=32, choices=pay_method)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=128)
    min_node = models.IntegerField(help_text=u"节点个数", default=1)
    disk = models.IntegerField(help_text=u'磁盘大小')
    pre_paid_period = models.IntegerField(
        help_text=u"预付费项目购买时长(单位:月)", default=0)
    pre_paid_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"预付费金额")
    buy_start_time = models.DateTimeField(help_text=u"购买开始时间")
    buy_end_time = models.DateTimeField(help_text=u"购买结束时间")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    region = models.CharField(max_length=32, help_text=u"数据中心")

    def toJSON(self):
        data = {}
        for f in self._meta.fields:
            obj = getattr(self, f.name)
            if type(f.name) == DateTimeField:
                data[f.name] = obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                data[f.name] = obj
        return data


class ServicePaymentNotify(BaseModel):
    class Meta:
        db_table = "service_payment_notify"

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    notify_type = models.CharField(max_length=10, help_text=u"通知类型")
    notify_content = models.CharField(max_length=200, help_text=u"通知内容")
    send_person = models.CharField(max_length=20, help_text=u"通知内容")
    time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    end_time = models.DateTimeField(blank=True, help_text=u"删除截止时间")
    status = models.CharField(max_length=10, help_text=u"状态")


class TenantServiceEnv(BaseModel):
    class Meta:
        db_table = 'service_env'

    service_id = models.CharField(max_length=32, help_text=u"服务id")
    language = models.CharField(
        max_length=40, null=True, blank=True, help_text=u"代码语言")
    check_dependency = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"检测运行环境依赖")
    user_dependency = models.CharField(
        max_length=1000, null=True, blank=True, help_text=u"用户自定义运行环境依赖")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")


class ServiceExtendMethod(BaseModel):
    """待删除"""
    class Meta:
        db_table = 'app_service_extend_method'

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    min_node = models.IntegerField(default=1, help_text=u"最小节点")
    max_node = models.IntegerField(default=20, help_text=u"最大节点")
    step_node = models.IntegerField(default=1, help_text=u"节点步长")
    min_memory = models.IntegerField(default=1, help_text=u"最小内存")
    max_memory = models.IntegerField(default=20, help_text=u"最大内存")
    step_memory = models.IntegerField(default=1, help_text=u"内存步长")
    is_restart = models.BooleanField(default=False, blank=True, help_text=u"是否重启")

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data[f.name] = value
        return data


class TenantServiceEnvVar(BaseModel):
    class Meta:
        db_table = 'service_env_var'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(
        max_length=32, db_index=True, help_text=u"服务id")
    container_port = models.IntegerField(default=0, help_text=u"端口")
    name = models.CharField(max_length=100, blank=True, help_text=u"名称")
    attr_name = models.CharField(max_length=100, help_text=u"属性")
    attr_value = models.CharField(max_length=512, help_text=u"值")
    is_change = models.BooleanField(
        default=False, blank=True, help_text=u"是否可改变")
    scope = models.CharField(max_length=10, help_text=u"范围", default="outer")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")

    def __unicode__(self):
        return self.name


class TenantServicesPort(BaseModel):
    """应用端口"""
    class Meta:
        db_table = 'services_port'
        unique_together = ('service_id', 'container_port')

    tenant_id = models.CharField(
        max_length=32, null=True, blank=True, help_text=u'租户id')
    service_id = models.CharField(
        max_length=32, db_index=True, help_text=u"服务ID")
    container_port = models.IntegerField(default=0, help_text=u"容器端口")
    mapping_port = models.IntegerField(default=0, help_text=u"映射端口")
    lb_mapping_port = models.IntegerField(default=0, help_text=u"负载均衡映射端口")
    protocol = models.CharField(
        max_length=15, default='', blank=True, help_text=u"服务协议：http,stream")
    port_alias = models.CharField(
        max_length=30, default='', blank=True, help_text=u"port别名")
    is_inner_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否内部服务；0:不绑定；1:绑定")
    is_outer_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否外部服务；0:不绑定；1:绑定")


class ImageServiceRelation(BaseModel):
    """应用镜像关系"""

    class Meta:
        db_table = 'service_image_relation'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    image_url = models.CharField(max_length=100, help_text=u"镜像地址")
    service_cname = models.CharField(
        max_length=100, default='', help_text=u"服务名")


class TenantServiceVolume(BaseModel):
    """应用存储"""

    class Meta:
        db_table = 'service_volume'

    SHARE = 'share-file'
    LOCAL = 'local'
    TMPFS = 'memoryfs'

    service_id = models.CharField(max_length=32, help_text=u"服务id")
    category = models.CharField(max_length=50, null=True, blank=True, help_text=u"服务类型")
    host_path = models.CharField(max_length=400, help_text=u"物理机的路径,绝对路径")
    volume_type = models.CharField(max_length=30, blank=True, null=True)
    volume_path = models.CharField(max_length=400, help_text=u"容器内路径,application为相对;其他为绝对")
    volume_name = models.CharField(max_length=100, blank=True, null=True)


class TenantServiceInfoDelete(BaseModel):
    """应用删除"""
    class Meta:
        db_table = 'service_delete'

    service_id = models.CharField(
        max_length=32, unique=True, help_text=u"服务id")
    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_key = models.CharField(max_length=32, help_text=u"服务key")
    service_alias = models.CharField(max_length=100, help_text=u"服务别名")
    service_cname = models.CharField(
        max_length=100, default='', help_text=u"服务名")
    service_region = models.CharField(max_length=15, help_text=u"服务所属区")
    desc = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"描述")
    category = models.CharField(
        max_length=15, help_text=u"服务分类：application,cache,store")
    service_port = models.IntegerField(help_text=u"服务端口", default=8000)
    is_web_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否web服务")
    version = models.CharField(max_length=20, help_text=u"版本")
    update_version = models.IntegerField(default=1, help_text=u"内部发布次数")
    image = models.CharField(max_length=100, help_text=u"镜像")
    cmd = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"启动参数")
    setting = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"设置项")
    extend_method = models.CharField(
        max_length=15,
        choices=extend_method,
        default='stateless',
        help_text=u"伸缩方式")
    env = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"环境变量")
    min_node = models.IntegerField(help_text=u"启动个数", default=1)
    min_cpu = models.IntegerField(help_text=u"cpu个数", default=500)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=256)
    inner_port = models.IntegerField(help_text=u"内部端口")
    volume_mount_path = models.CharField(
        max_length=50, null=True, blank=True, help_text=u"mount目录")
    host_path = models.CharField(
        max_length=300, null=True, blank=True, help_text=u"mount目录")
    deploy_version = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"部署版本")
    code_from = models.CharField(
        max_length=20, null=True, blank=True, help_text=u"代码来源:gitlab,github")
    git_url = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"code代码仓库")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    git_project_id = models.IntegerField(help_text=u"gitlab 中项目id", default=0)
    is_code_upload = models.BooleanField(
        default=False, blank=True, help_text=u"是否上传代码")
    code_version = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"代码版本")
    service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    delete_time = models.DateTimeField(auto_now_add=True)
    creater = models.IntegerField(help_text=u"服务创建者", default=0)
    language = models.CharField(
        max_length=40, null=True, blank=True, help_text=u"代码语言")
    protocol = models.CharField(max_length=15, help_text=u"服务协议：http,stream")
    total_memory = models.IntegerField(help_text=u"内存使用M", default=0)
    is_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否inner服务")
    namespace = models.CharField(
        max_length=100, default='', help_text=u"镜像发布云帮的区间")
    volume_type = models.CharField(
        max_length=15, default='shared', help_text=u"共享类型shared、exclusive")
    port_type = models.CharField(
        max_length=15,
        default='multi_outer',
        help_text=u"端口类型，one_outer;dif_protocol;multi_outer")
    # 服务创建类型,cloud、assistant
    service_origin = models.CharField(
        max_length=15,
        default='assistant',
        help_text=u"服务创建类型cloud云市服务,assistant云帮服务")
    expired_time = models.DateTimeField(null=True, help_text=u"过期时间")
    service_source = models.CharField(max_length=15, default="source_code", null=True, blank=True, help_text=u"应用来源")
    create_status = models.CharField(max_length=15, null=True, blank=True, help_text=u"应用创建状态 creating|complete")
    update_time = models.DateTimeField(auto_now_add=True, blank=True, help_text=u"更新时间")
    tenant_service_group_id = models.IntegerField(default=0, help_text=u"应用归属的服务组id")
    check_uuid = models.CharField(
        max_length=36, blank=True, null=True, default="", help_text=u"应用id")
    check_event_id = models.CharField(
        max_length=32, blank=True, null=True, default="", help_text=u"应用检测事件ID")
    docker_cmd = models.CharField(
        max_length=1024, null=True, blank=True, help_text=u"镜像创建命令")
    open_webhooks = models.BooleanField(default=False, help_text=u'是否开启自动触发部署功能')
    secret = models.CharField(max_length=64, null=True, blank=True, help_text=u"webhooks验证密码")
    server_type = models.CharField(
        max_length=5, default='git', help_text=u"源码仓库类型")


class TenantServiceAuth(BaseModel):
    class Meta:
        db_table = 'service_auth'

    service_id = models.CharField(max_length=32, help_text=u"应用id")
    user = models.CharField(
        max_length=40, null=True, blank=True, help_text=u"代码语言")
    password = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"服务运行环境依赖")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")


class TenantServiceMountRelation(BaseModel):
    class Meta:
        db_table = 'service_mnt_relation'
        unique_together = ('service_id', 'dep_service_id', 'mnt_name')

    tenant_id = models.CharField(max_length=32, help_text=u"团队id")
    service_id = models.CharField(max_length=32, help_text=u"应用id")
    dep_service_id = models.CharField(max_length=32, help_text=u"依赖服务id")
    mnt_name = models.CharField(max_length=100, help_text=u"mnt name")
    mnt_dir = models.CharField(max_length=400, help_text=u"mnt dir")


class TenantServiceRelation(BaseModel):
    """团队应用关系"""
    class Meta:
        db_table = 'tenant_service_relation'
        unique_together = ('service_id', 'dep_service_id')

    tenant_id = models.CharField(max_length=32, help_text=u"团队id")
    service_id = models.CharField(max_length=32, help_text=u"应用id")
    dep_service_id = models.CharField(max_length=32, help_text=u"依赖服务id")
    dep_service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    dep_order = models.IntegerField(help_text=u"依赖顺序")


class ServiceCreateStep(BaseModel):
    class Meta:
        db_table = 'service_create_step'

    tenant_id = models.CharField(max_length=32, help_text=u"团队id")
    service_id = models.CharField(max_length=32, help_text=u"应用id")
    app_step = models.IntegerField(default=1, help_text=u"创建应用的步数")


class ServiceEvent(BaseModel):
    """应用事件"""
    class Meta:
        db_table = 'service_event'

    event_id = models.CharField(max_length=32, help_text=u"操作id")
    tenant_id = models.CharField(max_length=32, help_text=u"团队id")
    service_id = models.CharField(max_length=32, help_text=u"应用d")
    user_name = models.CharField(max_length=50, help_text=u"操作用户")
    start_time = models.DateTimeField(help_text=u"操作开始时间")
    end_time = models.DateTimeField(help_text=u"操作结束时间", null=True)
    type = models.CharField(max_length=20, help_text=u"操作类型")
    status = models.CharField(
        max_length=20, help_text=u"操作处理状态 success failure")
    final_status = models.CharField(
        max_length=20,
        default="",
        help_text=u"操作状态，complete or timeout or null")
    message = models.CharField(max_length=200, help_text=u"操作说明")
    deploy_version = models.CharField(max_length=20, help_text=u"部署版本")
    old_deploy_version = models.CharField(max_length=20, help_text=u"历史部署版本")
    code_version = models.CharField(max_length=200, help_text=u"部署代码版本")
    old_code_version = models.CharField(max_length=200, help_text=u"历史部署代码版本")
    region = models.CharField(max_length=32, default="", help_text=u"服务所属数据中心")


class ServiceGroup(BaseModel):
    """应用分组"""

    class Meta:
        db_table = 'service_group'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    group_name = models.CharField(max_length=32, help_text=u"组名")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")
    is_default = models.BooleanField(default=False, help_text=u"默认组")


class ServiceGroupRelation(BaseModel):
    """应用与分组关系"""

    class Meta:
        db_table = 'service_group_relation'

    service_id = models.CharField(max_length=32, help_text=u"服务id")
    group_id = models.IntegerField()
    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")


class TenantServiceGroup(BaseModel):
    """应用组实体"""

    class Meta:
        db_table = 'tenant_service_group'

    tenant_id = models.CharField(max_length=32, help_text=u"团队id")
    group_name = models.CharField(max_length=64, help_text=u"服务组名")
    group_alias = models.CharField(max_length=64, help_text=u"服务别名")
    group_key = models.CharField(max_length=32, help_text=u"服务组id")
    group_version = models.CharField(max_length=32, help_text=u"服务组版本")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")
    service_group_id = models.IntegerField(default=0, help_text=u"ServiceGroup主键, 应用分类ID")


class ServiceProbe(BaseModel):
    class Meta:
        db_table = 'service_probe'

    service_id = models.CharField(max_length=32, help_text=u"服务id")
    probe_id = models.CharField(max_length=32, help_text=u"探针id")
    mode = models.CharField(max_length=10, help_text=u"探针模式")
    scheme = models.CharField(
        max_length=10, default="tcp", help_text=u"探针使用协议,tcp,http,cmd")
    path = models.CharField(max_length=50, default="", help_text=u"路径")
    port = models.IntegerField(default=80, help_text=u"检测端口")
    cmd = models.CharField(max_length=150, default="", help_text=u"cmd 命令")
    http_header = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text=u"http请求头，key=value,key2=value2")
    initial_delay_second = models.IntegerField(default=1, help_text=u"初始化等候时间")
    period_second = models.IntegerField(default=3, help_text=u"检测间隔时间")
    timeout_second = models.IntegerField(default=30, help_text=u"检测超时时间")
    failure_threshold = models.IntegerField(default=3, help_text=u"标志为失败的检测次数")
    success_threshold = models.IntegerField(default=1, help_text=u"标志为成功的检测次数")
    is_used = models.BooleanField(default=1, help_text=u"是否启用")


class TenantServiceExtendMethod(BaseModel):
    class Meta:
        db_table = 'tenant_service_extend_method'

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    min_node = models.IntegerField(default=1, help_text=u"最小节点")
    max_node = models.IntegerField(default=20, help_text=u"最大节点")
    step_node = models.IntegerField(default=1, help_text=u"节点步长")
    min_memory = models.IntegerField(default=1, help_text=u"最小内存")
    max_memory = models.IntegerField(default=20, help_text=u"最大内存")
    step_memory = models.IntegerField(default=1, help_text=u"内存步长")
    is_restart = models.BooleanField(default=False, blank=True, help_text=u"是否重启")


class ServiceInfo(BaseModel):
    """ 服务发布表格 """

    class Meta:
        db_table = 'service'
        unique_together = ('service_key', 'version')

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    publisher = models.EmailField(max_length=35, help_text=u"邮件地址")
    service_name = models.CharField(max_length=100, help_text=u"服务发布名称")
    pic = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"logo")
    info = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"简介")
    desc = models.CharField(
        max_length=400, null=True, blank=True, help_text=u"描述")
    status = models.CharField(
        max_length=15, choices=service_status, help_text=u"服务状态：发布后显示还是隐藏")
    category = models.CharField(
        max_length=15, help_text=u"服务分类：application,cache,store")
    is_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否inner服务")
    is_web_service = models.BooleanField(
        default=False, blank=True, help_text=u"是否web服务")
    version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    update_version = models.IntegerField(default=1, help_text=u"内部发布次数")
    image = models.CharField(max_length=100, help_text=u"镜像")
    namespace = models.CharField(
        max_length=100, default='', help_text=u"镜像发布云帮的区间")
    slug = models.CharField(max_length=200, help_text=u"slug包路径", default="")
    extend_method = models.CharField(
        max_length=15,
        choices=extend_method,
        default='stateless',
        help_text=u"伸缩方式")
    cmd = models.CharField(
        max_length=2048, null=True, blank=True, help_text=u"启动参数")
    setting = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"设置项")
    env = models.CharField(
        max_length=200, null=True, blank=True, help_text=u"环境变量")
    dependecy = models.CharField(
        max_length=100, default="", help_text=u"依赖服务--service_key待确认")
    min_node = models.IntegerField(help_text=u"启动个数", default=1)
    min_cpu = models.IntegerField(help_text=u"cpu个数", default=500)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=256)
    inner_port = models.IntegerField(help_text=u"内部端口", default=0)
    publish_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    volume_mount_path = models.CharField(
        max_length=50, null=True, blank=True, help_text=u"mount目录")
    service_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    is_init_accout = models.BooleanField(
        default=False, blank=True, help_text=u"是否初始化账户")
    creater = models.IntegerField(null=True, help_text=u"创建人")
    publish_type = models.CharField(
        max_length=10, default="single", help_text=u"判断服务是否属于组")

    def is_slug(self):
        return bool(self.image.startswith('goodrain.me/runner'))
        # return bool(self.image.endswith('/runner')) or bool(self.image.search('/runner:+'))

    def is_image(self):
        return not self.is_slug()


class AppServiceEnv(BaseModel):
    # 待删除
    """ 服务环境配置 """

    class Meta:
        db_table = 'app_service_env_var'
        unique_together = ('service_key', 'app_version', 'attr_name')

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    container_port = models.IntegerField(default=0, help_text=u"端口")
    name = models.CharField(max_length=100, blank=True, help_text=u"名称")
    attr_name = models.CharField(max_length=100, help_text=u"属性")
    attr_value = models.CharField(max_length=200, help_text=u"值")
    is_change = models.BooleanField(default=False, blank=True, help_text=u"是否可改变")
    scope = models.CharField(max_length=10, help_text=u"范围", default="outer")
    options = GrOptionsCharField(max_length=100, null=True, blank=True, help_text=u"参数选项", default="readonly")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data[f.name] = value
        return data


class AppServicePort(BaseModel):
    # 待删除
    """ 服务端口配置 """

    class Meta:
        db_table = 'app_service_port'
        unique_together = ('service_key', 'app_version', 'container_port')

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    container_port = models.IntegerField(default=0, help_text=u"容器端口")
    protocol = models.CharField(max_length=15, default='', blank=True, help_text=u"服务协议：http,stream")
    port_alias = models.CharField(max_length=30, default='', blank=True, help_text=u"port别名")
    is_inner_service = models.BooleanField(default=False, blank=True, help_text=u"是否内部服务；0:不绑定；1:绑定")
    is_outer_service = models.BooleanField(default=False, blank=True, help_text=u"是否外部服务；0:不绑定；1:绑定")


class AppServiceRelation(BaseModel):
    """ 应用依赖关系 """

    class Meta:
        db_table = 'service_rely_relation'

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    app_alias = models.CharField(max_length=100, help_text=u"服务发布名称")
    dep_service_key = models.CharField(max_length=32, help_text=u"服务key")
    dep_app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    dep_app_alias = models.CharField(max_length=100, help_text=u"服务发布名称")

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data[f.name] = value
        return data


class AppServiceVolume(BaseModel):
    # 待删除
    """发布数据持久化表格"""

    class Meta:
        db_table = 'app_service_volume'

    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    category = models.CharField(max_length=50, null=True, blank=True, help_text=u"服务类型")
    volume_path = models.CharField(max_length=400, help_text=u"容器内路径,application为相对;其他为绝对")
    volume_type = models.CharField(max_length=30, blank=True, null=True)
    volume_name = models.CharField(max_length=100, blank=True, null=True)

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data[f.name] = value
        return data


class AppServiceGroup(BaseModel):
    # 待删除
    """服务组分享记录"""

    class Meta:
        db_table = "app_service_group"
        unique_together = ('group_share_id', 'group_version')

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    group_share_id = models.CharField(max_length=32, unique=True, help_text=u"服务组发布id")
    group_share_alias = models.CharField(max_length=100, help_text=u"服务组发布名称")
    group_id = models.CharField(max_length=100, help_text=u"对应的服务分类ID,为0表示不是导入或者同步的数据")
    service_ids = models.CharField(max_length=1024, null=False, help_text=u"对应的服务id")
    is_success = models.BooleanField(default=False, help_text=u"发布是否成功")
    step = models.IntegerField(default=0, help_text=u"当前发布进度")
    publish_type = models.CharField(max_length=16, default="services_group", choices=group_publish_type,
                                    help_text=u"发布的应用组类型")
    group_version = models.CharField(max_length=20, null=False, default="0.0.1", help_text=u"服务组版本")
    is_market = models.BooleanField(default=False, blank=True, help_text=u"是否发布到公有市场")
    desc = models.CharField(max_length=400, null=True, blank=True, help_text=u"更新说明")
    installable = models.BooleanField(default=True, blank=True, help_text=u"发布到云市后是否允许安装")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text=u"更新时间")
    deploy_time = models.DateTimeField(auto_now_add=True, help_text=u"最后一次被部署的时间")
    installed_count = models.IntegerField(default=0, help_text=u"部署次数")
    source = models.CharField(max_length=32, default='local', null=False, blank=True, help_text=u"应用组数据来源")
    enterprise_id = models.IntegerField(default=0, help_text=u"应用组的企业id")
    share_scope = models.CharField(max_length=20, null=False, help_text=u"分享范围")
    is_publish_to_market = models.BooleanField(default=False, blank=True, help_text=u"判断该版本应用组是否之前发布过公有市场")


class PublishedGroupServiceRelation(BaseModel):
    # 待删除
    """分享的服务组和服务的关系"""

    class Meta:
        db_table = "publish_group_service_relation"

    group_pk = models.IntegerField()
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    service_key = models.CharField(max_length=32, help_text=u"服务key")
    version = models.CharField(max_length=20, help_text=u"当前最新版本")


class ServiceConsume(BaseModel):
    """待删除"""
    class Meta:
        db_table = 'service_consume'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    memory = models.IntegerField(help_text=u"内存大小单位（M）", default=0)
    node_num = models.IntegerField(help_text=u"节点个数", default=1)
    disk = models.IntegerField(help_text=u'磁盘大小', default=0)
    net = models.IntegerField(help_text=u"网络使用K", default=0)
    memory_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"内存金额")
    disk_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"磁盘金额")
    net_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"网络金额")
    pay_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"实际付费金额")
    pay_status = models.CharField(
        max_length=15, choices=pay_status, help_text=u"付费状态")
    region = models.CharField(max_length=32, help_text=u"数据中心")
    status = models.IntegerField(default=0, help_text=u"0:无效；1:有效；2:操作中")
    time = models.DateTimeField(help_text=u"创建时间")
    real_memory_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"内存按需金额")
    real_disk_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"磁盘按需金额")



class AppService(BaseModel):
    # 待删除
    """ 服务发布表格 """

    class Meta:
        db_table = 'app_service'
        unique_together = ('service_key', 'app_version')

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    service_key = models.CharField(max_length=32, help_text=u"服务key")
    app_version = models.CharField(max_length=20, null=False, help_text=u"当前最新版本")
    app_alias = models.CharField(max_length=100, help_text=u"服务发布名称")
    logo = models.FileField(upload_to=logo_path, null=True, blank=True, help_text=u"logo")
    info = models.CharField(max_length=100, null=True, blank=True, help_text=u"简介")
    desc = models.CharField(max_length=400, null=True, blank=True, help_text=u"描述")
    status = models.CharField(max_length=15, choices=app_status, help_text=u"服务状态：发布后显示还是隐藏")
    category = models.CharField(max_length=15, help_text=u"服务分类：application,cache,store,app_publish")
    is_service = models.BooleanField(default=False, blank=True, help_text=u"是否inner服务")
    is_web_service = models.BooleanField(default=False, blank=True, help_text=u"是否web服务")
    image = models.CharField(max_length=100, help_text=u"镜像")
    namespace = models.CharField(max_length=100, default='', help_text=u"镜像发布云帮的区间")
    slug = models.CharField(max_length=200, help_text=u"slug包路径", default="")
    extend_method = models.CharField(max_length=15, choices=extend_method, default='stateless', help_text=u"伸缩方式")
    cmd = models.CharField(max_length=100, null=True, blank=True, help_text=u"启动参数")
    env = models.CharField(max_length=200, null=True, blank=True, help_text=u"环境变量")
    min_node = models.IntegerField(help_text=u"启动个数", default=1)
    min_cpu = models.IntegerField(help_text=u"cpu个数", default=500)
    min_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=256)
    inner_port = models.IntegerField(help_text=u"内部端口", default=0)
    volume_mount_path = models.CharField(max_length=50, null=True, blank=True, help_text=u"mount目录")
    service_type = models.CharField(max_length=50, null=True, blank=True,
                                    help_text=u"服务类型:web,mysql,redis,mongodb,phpadmin")
    is_init_accout = models.BooleanField(default=False, blank=True, help_text=u"是否初始化账户")
    is_base = models.BooleanField(default=False, blank=True, help_text=u"是否基础服务")
    is_outer = models.BooleanField(default=False, blank=True, help_text=u"是否发布到公有市场")
    is_ok = models.BooleanField(help_text=u'发布是否成功', default=False)
    dest_yb = models.BooleanField(help_text=u'云帮发布是否成功', default=False)
    dest_ys = models.BooleanField(help_text=u'云市发布是否成功', default=False)
    creater = models.IntegerField(null=True, help_text=u"创建人")
    publisher = models.EmailField(max_length=35, help_text=u"邮件地址")
    show_category = models.CharField(max_length=15, help_text=u"服务分类")

    show_app = models.BooleanField(default=False, blank=True, help_text=u"发布到公有市场后是否在云市展示")
    show_assistant = models.BooleanField(default=False, blank=True, help_text=u"发布到公有市场后是否在云帮展示")
    update_version = models.IntegerField(default=1, help_text=u"内部发布次数")

    def is_slug(self):
        # return bool(self.image.startswith('goodrain.me/runner'))
        return bool(self.image.endswith('/runner')) or bool('/runner:' in self.image)

    def is_image(self):
        return not self.is_slug()

    def __unicode__(self):
        return u"{0}({1})".format(self.service_id, self.service_key)


class AppServiceShareInfo(BaseModel):
    # 待删除
    """普通发布存储环境是否可修改信息"""

    class Meta:
        db_table = 'app_service_share'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")

    tenant_env_id = models.IntegerField(help_text=u"服务的环境id")
    is_change = models.BooleanField(default=False, help_text=u"是否可改变")


class ServiceFeeBill(BaseModel):
    # 待删除
    class Meta:
        db_table = 'service_fee_bill'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    prepaid_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"付费金额")
    pay_status = models.CharField(
        max_length=15, choices=pay_status, help_text=u"付费状态")
    cost_type = models.CharField(max_length=15, help_text=u"消费类型")
    node_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=128)
    node_num = models.IntegerField(help_text=u"节点个数", default=1)
    disk = models.IntegerField(help_text=u'磁盘大小')
    buy_period = models.IntegerField(help_text=u"预付费时长(单位:小时)", default=0)
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    pay_time = models.DateTimeField(auto_now_add=True, help_text=u"支付时间")


class TenantServiceStatics(BaseModel):
    # 待删除
    class Meta:
        db_table = 'tenant_service_statics'
        unique_together = ('service_id', 'time_stamp')
        get_latest_by = 'ID'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    service_id = models.CharField(max_length=32, help_text=u"服务id")
    pod_id = models.CharField(max_length=32, help_text=u"服务id")
    node_num = models.IntegerField(help_text=u"节点个数", default=0)
    node_memory = models.IntegerField(help_text=u"节点内存k", default=0)
    container_cpu = models.IntegerField(help_text=u"cpu使用", default=0)
    container_memory = models.IntegerField(help_text=u"内存使用K", default=0)
    container_memory_working = models.IntegerField(
        help_text=u"正在使用内存K", default=0)
    pod_cpu = models.IntegerField(help_text=u"cpu使用", default=0)
    pod_memory = models.IntegerField(help_text=u"内存使用K", default=0)
    pod_memory_working = models.IntegerField(help_text=u"正在使用内存K", default=0)
    container_disk = models.IntegerField(help_text=u"磁盘使用K", default=0)
    storage_disk = models.IntegerField(help_text=u"磁盘使用K", default=0)
    net_in = models.IntegerField(help_text=u"网络使用K", default=0)
    net_out = models.IntegerField(help_text=u"网络使用K", default=0)
    flow = models.IntegerField(help_text=u"网络下载量", default=0)
    time_stamp = models.IntegerField(help_text=u"时间戳", default=0)
    status = models.IntegerField(default=0, help_text=u"0:无效；1:有效；2:操作中")
    region = models.CharField(max_length=15, help_text=u"服务所属区")
    time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
