# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime
from django.db import models
from django.db.models.fields.files import FileField
from django.utils.crypto import salted_hmac


from console.utils.crypt import make_tenant_id
from console.utils.crypt import encrypt_passwd

logger = logging.getLogger("default")

app_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
plugin_scope = (("enterprise", u"企业"), ("team", u"团队"), ("goodrain", u"好雨云市"))
user_identity = ((u"管理员", "admin"),)
tenant_type = ((u"免费租户", "free"), (u"付费租户", "payed"))
user_origion = ((u"自主注册", "registration"), (u"邀请注册", "invitation"))
extend_method = ((u"不伸缩", 'stateless'), (u"垂直伸缩", 'vertical'))
tenant_identity = ((u"拥有者", "owner"), (u"管理员", "admin"), (u"开发者", "developer"),
                   (u"观察者", "viewer"), (u"访问", "access"))
service_identity = ((u"管理员", "admin"), (u"开发者", "developer"), (u"观察者", "viewer"))


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


class RainbondCenterApp(BaseModel):
    """云市应用包(组)"""

    class Meta:
        db_table = "rainbond_center_app"
        unique_together = ('group_key', 'version')

    group_key = models.CharField(max_length=32, help_text=u"应用包")
    group_name = models.CharField(max_length=64, help_text=u"应用包名")
    share_user = models.IntegerField(help_text=u"分享人id")
    record_id = models.IntegerField(help_text=u"分享流程id，控制一个分享流程产出一个实体")
    share_team = models.CharField(max_length=32, help_text=u"来源应用所属团队")
    tenant_service_group_id = models.IntegerField(default=0, help_text=u"应用归属的服务组id")
    pic = models.CharField(max_length=100, null=True, blank=True, help_text=u"应用头像信息")
    source = models.CharField(max_length=15, default="", null=True, blank=True, help_text=u"应用来源(本地创建，好雨云市)")
    version = models.CharField(max_length=20, help_text=u"版本")
    scope = models.CharField(max_length=10, choices=app_scope, help_text=u"可用范围")
    describe = models.CharField(max_length=400, null=True, blank=True, help_text=u"云市应用描述信息")
    app_template = models.TextField(help_text=u"全量应用与插件配置信息")
    is_complete = models.BooleanField(default=False, help_text=u"代码或镜像是否同步完成")
    is_ingerit = models.BooleanField(default=True, help_text=u"是否可被继承")
    template_version = models.CharField(max_length=10, default="v2", help_text=u"模板版本")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, help_text=u"更新时间")
    enterprise_id = models.CharField(max_length=32, default="public", help_text=u"企业ID")
    install_number = models.IntegerField(default=0, help_text=u'安装次数')
    is_official = models.BooleanField(default=False, help_text=u'是否官方认证')

    def __unicode__(self):
        return self.to_dict()


class RainbondCenterAppInherit(BaseModel):
    """云市应用组继承关系"""

    class Meta:
        db_table = "rainbond_center_app_inherit"

    group_key = models.CharField(max_length=32, unique=True, help_text=u"当前应用")
    version = models.CharField(max_length=20, unique=True, help_text=u"当前应用版本号")
    derived_group_key = models.CharField(max_length=32, unique=True, help_text=u"继承哪个云市应用")

    def __unicode__(self):
        return self.to_dict()


class RainbondCenterPlugin(BaseModel):
    """云市插件"""

    class Meta:
        db_table = "rainbond_center_plugin"

    plugin_key = models.CharField(max_length=32,  help_text=u"插件分享key")
    plugin_name = models.CharField(max_length=32, help_text=u"插件名称")
    plugin_id = models.CharField(max_length=32, null=True, help_text=u"插件id")
    category = models.CharField(max_length=32, help_text=u"插件类别")
    record_id = models.IntegerField(help_text=u"分享流程id")
    version = models.CharField(max_length=20, help_text=u"版本")
    build_version = models.CharField(max_length=32, help_text=u"构建版本")
    pic = models.CharField(max_length=100,null=True, blank=True, help_text=u"插件头像信息")
    scope = models.CharField(max_length=10, choices=plugin_scope, help_text=u"可用范围")
    source = models.CharField(max_length=15, default="", null=True, blank=True, help_text=u"应用来源(本地创建，好雨云市)")
    share_user = models.IntegerField(help_text=u"分享人id")
    share_team = models.CharField(max_length=32, help_text=u"来源应用所属团队")
    desc = models.CharField(max_length=400, null=True, blank=True, help_text=u"插件描述信息")
    plugin_template = models.TextField(help_text=u"全量插件信息")
    is_complete = models.BooleanField(default=False, help_text=u"代码或镜像是否同步完成")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, help_text=u"更新时间")
    enterprise_id = models.CharField(max_length=32, default='public', help_text=u"企业id")

    def __unicode__(self):
        return self.to_dict()


class PluginShareRecordEvent(BaseModel):
    """插件分享订单关联发布事件"""

    class Meta:
        db_table = "plugin_share_record_event"

    record_id = models.IntegerField(help_text=u"关联的记录ID")
    region_share_id = models.CharField(max_length=36, help_text=u"应用数据中心分享反馈ID")
    team_id = models.CharField(max_length=32, help_text=u"对应所在团队ID")
    team_name = models.CharField(max_length=32, help_text=u"应用所在团队唯一名称")
    plugin_id = models.CharField(max_length=32, help_text=u"对应插件ID")
    plugin_name = models.CharField(max_length=32, help_text=u"对应插件名称")
    event_id = models.CharField(max_length=32, default="", help_text=u"介质同步事件ID")
    event_status = models.CharField(max_length=32, default="not_start", help_text=u"事件状态")
    create_time = models.DateTimeField(auto_now_add=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text=u"更新时间")

    def __unicode__(self):
        return self.to_dict()


class ComposeGroup(BaseModel):
    """compose组"""

    class Meta:
        db_table = "compose_group"

    group_id = models.IntegerField(help_text=u"compose组关联的组id")
    team_id = models.CharField(max_length=32, help_text=u"团队 id")
    region = models.CharField(max_length=15, help_text=u"服务所属数据中心")
    compose_content = models.TextField(null=True, blank=True, help_text=u"compose文件内容")
    compose_id = models.CharField(max_length=32, unique=True, help_text=u"compose id")
    create_status = models.CharField(max_length=15, null=True, blank=True,
                                     help_text=u"compose组创建状态 creating|checking|checked|complete")
    check_uuid = models.CharField(
        max_length=36, blank=True, null=True, default="", help_text=u"compose检测ID")
    check_event_id = models.CharField(
        max_length=32, blank=True, null=True, default="", help_text=u"compose检测事件ID")

    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")


class ComposeServiceRelation(BaseModel):
    """compose组和服务的关系"""

    class Meta:
        db_table = "compose_service_relation"

    team_id = models.CharField(max_length=32, help_text=u"团队 id")
    service_id = models.CharField(max_length=32, help_text=u"服务 id")
    compose_id = models.CharField(max_length=32, help_text=u"compose id")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")


class TeamGitlabInfo(BaseModel):
    class Meta:
        db_table = "team_gitlab_info"

    team_id = models.CharField(max_length=32, help_text=u"团队ID")
    repo_name = models.CharField(max_length=100, help_text=u"代码仓库名称")
    respo_url = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"code代码仓库")
    git_project_id = models.IntegerField(help_text=u"gitlab 中项目id", default=0)
    code_version = models.CharField(
        max_length=100, null=True, blank=True, help_text=u"代码版本")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")


class EnterpriseUserPerm(BaseModel):
    """用户在企业的权限"""

    class Meta:
        db_table = 'enterprise_user_perm'

    user_id = models.IntegerField(help_text=u"用户id")
    enterprise_id = models.CharField(max_length=32, help_text=u"企业id")
    identity = models.CharField(
        max_length=15, choices=user_identity, help_text=u"用户在企业的身份")


class TenantUserRole(BaseModel):
    """用户在一个团队中的角色"""

    class Meta:
        db_table = 'tenant_user_role'
        unique_together = (('role_name', 'tenant_id'),)

    role_name = models.CharField(max_length=32, help_text=u'角色名称')
    tenant_id = models.IntegerField(null=True, blank=True, help_text=u'团队id')
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.to_dict()


class TenantUserPermission(BaseModel):
    """权限及对应的操作"""

    class Meta:
        db_table = 'tenant_user_permission'
        unique_together = (('codename', 'per_info'),)

    codename = models.CharField(max_length=32, help_text=u'权限名称')
    per_info = models.CharField(max_length=32, help_text=u'权限对应的操作信息')
    is_select = models.BooleanField(default=True, help_text=u'自定义权限时是否可以做选项')
    group = models.IntegerField(help_text=u'这个权限属于哪个权限组', null=True, blank=True)
    per_explanation = models.CharField(max_length=132, null=True, blank=True, help_text=u'这一条权限操作的具体说明')

    def __unicode__(self):
        return self.to_dict()


class TenantUserRolePermission(BaseModel):
    """团队中一个角色与权限的关系对应表"""

    class Meta:
        db_table = 'tenant_user_role_permission'

    role_id = models.IntegerField(help_text=u'团队中的一个角色的id')
    per_id = models.IntegerField(help_text=u'一个权限操作的id')

    def __unicode__(self):
        return self.to_dict()


class PermGroup(BaseModel):
    """权限组，用于给权限分组分类"""

    class Meta:
        db_table = 'tenant_permission_group'

    group_name = models.CharField(max_length=64, help_text=u'组名')

    def __unicode__(self):
        return self.to_dict()


class AppExportRecord(BaseModel):
    """应用导出"""

    class Meta:
        db_table = 'app_export_record'


    group_key = models.CharField(max_length=32, help_text=u"导出应用的key")
    version = models.CharField(max_length=20, help_text=u"导出应用的版本")
    format = models.CharField(max_length=15, help_text=u"导出应用的格式")
    event_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"事件id")
    status = models.CharField(max_length=10, null=True, blank=True, help_text=u"时间请求状态")
    file_path = models.CharField(max_length=256, null=True, blank=True, help_text=u"文件地址")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"更新时间")
    enterprise_id = models.CharField(max_length=32, help_text=u"企业ID")


class UserMessage(BaseModel):
    """用户站内信"""

    class Meta:
        db_table = 'user_message'

    message_id = models.CharField(max_length=32, help_text=u"消息ID")
    receiver_id = models.IntegerField(help_text=u"接受消息用户ID")
    content = models.CharField(max_length=1000, help_text=u"消息内容")
    is_read = models.BooleanField(default=False, help_text=u"是否已读")
    create_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, help_text=u"更新时间")
    msg_type = models.CharField(max_length=32, help_text=u"消息类型")
    announcement_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"公告ID")
    title = models.CharField(max_length=64, help_text=u"消息标题", default=u"title")
    level = models.CharField(max_length=32, default="low", help_text=u"通知的等级")


class AppImportRecord(BaseModel):
    class Meta:
        db_table = 'app_import_record'

    event_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"事件id")
    status = models.CharField(max_length=15, null=True, blank=True, help_text=u"时间请求状态")
    scope = models.CharField(max_length=10, null=True, blank=True, default="", help_text=u"导入范围")
    format = models.CharField(max_length=15, null=True, blank=True, default="", help_text=u"类型")
    source_dir = models.CharField(max_length=256, null=True, blank=True, default="", help_text=u"目录地址")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"更新时间")
    team_name = models.CharField(max_length=32, null=True, blank=True, help_text=u"正在导入的团队名称")
    region = models.CharField(max_length=32, null=True, blank=True, help_text=u"数据中心")


class GroupAppBackupRecord(BaseModel):
    class Meta:
        db_table = 'groupapp_backup'

    group_id = models.IntegerField(help_text=u"组ID")
    event_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"事件id")
    group_uuid = models.CharField(max_length=32, null=True, blank=True, help_text=u"group UUID")
    version = models.CharField(max_length=32, null=True, blank=True, help_text=u"备份版本")
    backup_id = models.CharField(max_length=36, null=True, blank=True, help_text=u"备份ID")
    team_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"团队ID")
    user = models.CharField(max_length=20, null=True, blank=True, help_text=u"备份人")
    region = models.CharField(max_length=15, null=True, blank=True, help_text=u"数据中心")
    status = models.CharField(max_length=15, null=True, blank=True, help_text=u"时间请求状态")
    note = models.CharField(max_length=128, null=True, blank=True, default="", help_text=u"备份说明")
    mode = models.CharField(max_length=15, null=True, blank=True, default="", help_text=u"备份类型")
    source_dir = models.CharField(max_length=256, null=True, blank=True, default="", help_text=u"目录地址")
    backup_size = models.IntegerField(help_text=u"备份文件大小")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    total_memory = models.IntegerField(help_text=u"备份应用的总内存")
    backup_server_info = models.CharField(max_length=400, null=True, blank=True, default="", help_text=u"备份服务信息")
    source_type = models.CharField(max_length=32, null=True, blank=True, help_text=u"源类型")


class GroupAppMigrateRecord(BaseModel):
    class Meta:
        db_table = 'groupapp_migrate'

    group_id = models.IntegerField(help_text=u"组ID")
    event_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"事件id")
    group_uuid = models.CharField(max_length=32, null=True, blank=True, help_text=u"group UUID")
    version = models.CharField(max_length=32, null=True, blank=True, help_text=u"迁移的版本")
    backup_id = models.CharField(max_length=36, null=True, blank=True, help_text=u"备份ID")
    migrate_team = models.CharField(max_length=32, null=True, blank=True, help_text=u"迁移的团队名称")
    user = models.CharField(max_length=20, null=True, blank=True, help_text=u"恢复人")
    migrate_region = models.CharField(max_length=15, null=True, blank=True, help_text=u"迁移的数据中心")
    status = models.CharField(max_length=15, null=True, blank=True, help_text=u"时间请求状态")
    migrate_type = models.CharField(max_length=15, default="migrate", help_text=u"类型")
    restore_id = models.CharField(max_length=36, null=True, blank=True, help_text=u"恢复ID")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    original_group_id = models.IntegerField(help_text=u"原始组ID")
    original_group_uuid = models.CharField(max_length=32, null=True, blank=True, help_text=u"原始group UUID")


class GroupAppBackupImportRecord(BaseModel):
    class Meta:
        db_table = 'groupapp_backup_import'

    event_id = models.CharField(max_length=32, null=True, blank=True, help_text=u"事件id")
    status = models.CharField(max_length=15, null=True, blank=True, help_text=u"时间请求状态")
    file_temp_dir = models.CharField(max_length=256, null=True, blank=True, default="", help_text=u"目录地址")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"更新时间")
    team_name = models.CharField(max_length=32, null=True, blank=True, help_text=u"正在导入的团队名称")
    region = models.CharField(max_length=32, null=True, blank=True, help_text=u"数据中心")


class Applicants(BaseModel):
    class Meta:
        db_table = 'applicants'

    # 用户ID
    user_id = models.IntegerField(help_text=u'申请用户ID')
    user_name = models.CharField(max_length=20, null=False, help_text=u"申请用户名")
    # 团队
    team_id = models.CharField(max_length=33, help_text=u'所属团队id')
    team_name = models.CharField(max_length=20,null=False, help_text=u"申请组名")
    # 申请时间
    apply_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text=u"申请时间")
    # is_pass是否通过
    is_pass = models.IntegerField(default=0, help_text=u'0表示审核中，1表示通过审核，2表示审核未通过')
    # 团队名
    team_alias = models.CharField(max_length=30, null=False, help_text=u"团队名")


class DeployRelation(BaseModel):
    class Meta:
        db_table = "deploy_relation"

    # 应用服务id
    service_id = models.CharField(
        max_length=32, unique=True, help_text=u"服务id")
    key_type = models.CharField(max_length=10, help_text=u"密钥类型")
    secret_key = models.CharField(max_length=200, help_text=u"密钥")


class TenantEnterpriseToken(BaseModel):
    class Meta:
        db_table = 'tenant_enterprise_token'
        unique_together = ('enterprise_id', 'access_target')

    enterprise_id = models.IntegerField(default=0, help_text=u"企业id")
    access_target = models.CharField(max_length=32, blank=True, null=True, default='', help_text=u"要访问的目标服务名称")
    access_url = models.CharField(max_length=255,  help_text=u"需要访问的api地址")
    access_id = models.CharField(max_length=32, help_text=u"target分配给客户端的ID")
    access_token = models.CharField(max_length=256, blank=True, null=True, default='', help_text=u"客户端token")
    crt = models.TextField(default='', blank=True, null=True, help_text=u"客户端证书")
    key = models.TextField(default='', blank=True, null=True, help_text=u"客户端证书key")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, help_text=u"更新时间")

    def __unicode__(self):
        return self.to_dict()


class TenantEnterprise(BaseModel):
    class Meta:
        db_table = 'tenant_enterprise'

    enterprise_id = models.CharField(max_length=32, unique=True, help_text=u"企业id")
    enterprise_name = models.CharField(max_length=64, help_text=u"企业名称")
    enterprise_alias = models.CharField(max_length=64, blank=True, null=True, default='', help_text=u"企业别名")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, help_text=u"创建时间")
    enterprise_token = models.CharField(max_length=256, blank=True, null=True, default='', help_text=u"企业身份token")
    is_active = models.IntegerField(default=0, help_text=u"是否在云市上激活, 0:未激活, 1:已激活")

    def __unicode__(self):
        return self.to_dict()


class Tenants(BaseModel):
    """
    租户表
    """
    class Meta:
        db_table = 'tenant_info'

    tenant_id = models.CharField(
        max_length=33, unique=True, default=make_tenant_id, help_text=u"租户id")
    tenant_name = models.CharField(
        max_length=40, unique=True, help_text=u"租户名称")
    region = models.CharField(
        max_length=30, default='', help_text=u"区域中心")
    is_active = models.BooleanField(default=True, help_text=u"激活状态")
    pay_type = models.CharField(
        max_length=5, choices=tenant_type, help_text=u"付费状态")
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"账户余额")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    creater = models.IntegerField(help_text=u"租户创建者", default=0)
    limit_memory = models.IntegerField(help_text=u"内存大小单位（M）", default=1024)
    update_time = models.DateTimeField(auto_now=True, help_text=u"更新时间")
    pay_level = models.CharField(
        max_length=30, default='free', help_text=u"付费级别:free,personal,company")
    expired_time = models.DateTimeField(null=True, help_text=u"过期时间")
    tenant_alias = models.CharField(max_length=64, null=True, blank=True, default='', help_text=u"团队别名")
    enterprise_id = models.CharField(max_length=32, null=True, blank=True, default='', help_text=u"企业id")

    def __unicode__(self):
        return self.tenant_name


class Users(models.Model):
    USERNAME_FIELD = 'nick_name'

    class Meta:
        db_table = 'user_info'

    user_id = models.AutoField(primary_key=True, max_length=10)
    email = models.EmailField(max_length=35, help_text=u"邮件地址")
    nick_name = models.CharField(
        max_length=24, unique=True, null=True, blank=True, help_text=u"用户昵称")
    password = models.CharField(max_length=16, help_text=u"密码")
    phone = models.CharField(
        max_length=11, null=True, blank=True, help_text=u"手机号码")
    is_active = models.BooleanField(default=False, help_text=u"激活状态")
    origion = models.CharField(
        max_length=12, choices=user_origion, help_text=u"用户来源")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    git_user_id = models.IntegerField(help_text=u"gitlab 用户id", default=0)
    github_token = models.CharField(max_length=60, help_text=u"github token")
    client_ip = models.CharField(max_length=20, help_text=u"注册ip")
    rf = models.CharField(max_length=60, help_text=u"register from")
    # 0:普通注册,未绑定微信
    # 1:普通注册,绑定微信
    # 2:微信注册,绑定微信,未补充信息
    # 3:微信注册,绑定微信,已补充信息
    # 4:微信注册,解除微信绑定,已补充信息
    status = models.IntegerField(default=0, help_text=u'用户类型 0:普通注册,未绑定微信')
    union_id = models.CharField(max_length=100, help_text=u'绑定微信的union_id')
    sso_user_id = models.CharField(max_length=32, null=True, blank=True, default='', help_text=u"统一认证中心的user_id")
    sso_user_token = models.CharField(max_length=256, null=True, blank=True, default='', help_text=u"统一认证中心的user_id")
    enterprise_id = models.CharField(max_length=32, null=True, blank=True, default='',
                                     help_text=u"统一认证中心的enterprise_id")

    def set_password(self, raw_password):
        self.password = encrypt_passwd(self.email + raw_password)

    def check_password(self, raw_password):
        return bool(encrypt_passwd(self.email + raw_password) == self.password)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @property
    def is_sys_admin(self):
        """
        是否是系统管理员
        :return: True/False
        """
        # admins = ('liufan@gmail.com', 'messi@goodrain.com', 'elviszhang@163.com', 'rhino@goodrain.com',
        #           'ethan@goodrain.com', 'fanfan@goodrain.com', 'wangjiajun33wjj@126.com', 'linmu0001@126.com')
        # return bool(self.email in admins)
        if self.user_id:
            try:
                SuperAdminUser.objects.get(user_id=self.user_id)
                return True
            except SuperAdminUser.DoesNotExist:
                pass
        return False

    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "goodrain.com.models.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()

    @property
    def safe_email(self):
        return re.sub(r'(?<=\w{2}).*(?=\w@.*)', 'xxxx', self.email)

    def __unicode__(self):
        return self.nick_name or self.email

    def to_dict(self):
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            data[f.name] = value
        return data

    def get_username(self):
        return self.nick_name


class SuperAdminUser(models.Model):
    """超级管理员"""

    class Meta:
        db_table = "user_administrator"

    user_id = models.IntegerField(unique=True, help_text=u"用户ID")
    email = models.EmailField(max_length=35, null=True, blank=True, help_text=u"邮件地址")


class PermRelTenant(BaseModel):
    """
    用户和团队的关系表
    identity ：租户权限
    """
    class Meta:
        db_table = 'tenant_perms'

    user_id = models.IntegerField(help_text=u"关联用户")
    tenant_id = models.IntegerField(help_text=u"团队id")
    identity = models.CharField(
        max_length=15, choices=tenant_identity, help_text=u"租户身份", null=True, blank=True)
    enterprise_id = models.IntegerField(help_text=u"关联企业")
    role_id = models.IntegerField(help_text=u'角色', null=True, blank=True)


class PermRelService(BaseModel):
    """
    用户和服务关系表/用户在一个服务中的角色
    """
    class Meta:
        db_table = 'service_perms'

    user_id = models.IntegerField(help_text=u"用户id")
    service_id = models.IntegerField(help_text=u"服务id")
    identity = models.CharField(
        max_length=15, choices=service_identity, help_text=u"服务身份", null=True, blank=True)
    role_id = models.IntegerField(help_text=u'角色', null=True, blank=True)


class TenantRegionInfo(BaseModel):
    class Meta:
        db_table = 'tenant_region'
        unique_together = (('tenant_id', 'region_name'),)

    tenant_id = models.CharField(
        max_length=33, db_index=True, help_text=u"租户id")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")
    is_active = models.BooleanField(default=True, help_text=u"是否已激活")
    is_init = models.BooleanField(default=False, help_text=u'是否创建租户网络')
    service_status = models.IntegerField(
        help_text=u"服务状态0:暂停，1:运行，2:关闭", default=1)
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text=u"更新时间")
    region_tenant_name = models.CharField(max_length=32, null=True, blank=True, default='', help_text=u"数据中心租户名")
    region_tenant_id = models.CharField(max_length=32, null=True, blank=True, default='', help_text=u"数据中心租户id")
    region_scope = models.CharField(max_length=32, null=True, blank=True, default='',
                                    help_text=u"数据中心类型 private/public")
    enterprise_id = models.CharField(max_length=32, null=True, blank=True, default='', help_text=u"企业id")


class TenantRegionPayModel(BaseModel):
    class Meta:
        db_table = 'tenant_region_pay_model'

    tenant_id = models.CharField(max_length=32, help_text=u"租户id")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")
    pay_model = models.CharField(
        max_length=10, default='hour', help_text=u"付费模式:hour,month,year")
    buy_period = models.IntegerField(help_text=u"购买周期", default=0)
    buy_memory = models.IntegerField(help_text=u"购买内存", default=0)
    buy_disk = models.IntegerField(help_text=u"购买磁盘", default=0)
    buy_net = models.IntegerField(help_text=u"购买流量", default=0)
    buy_start_time = models.DateTimeField(help_text=u"购买开始时间")
    buy_end_time = models.DateTimeField(help_text=u"购买结束时间")
    buy_money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text=u"购买金额")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, help_text=u"创建时间")


class TenantRegionResource(BaseModel):
    class Meta:
        db_table = 'tenant_region_resource'
        unique_together = (('tenant_id', 'region_name'),)

    enterprise_id = models.CharField(max_length=32, help_text=u"企业id")
    tenant_id = models.CharField(max_length=33, help_text=u"租户id")
    region_name = models.CharField(max_length=20, help_text=u"区域中心名称")
    memory_limit = models.IntegerField(help_text=u"内存使用上限(M)", default=0)
    memory_expire_date = models.DateTimeField(null=True, blank=True, help_text=u"内存有效期时间")
    disk_limit = models.IntegerField(help_text=u"磁盘使用上限(M)", default=0)
    disk_expire_date = models.DateTimeField(null=True, blank=True, help_text=u"磁盘有效期时间")
    net_limit = models.IntegerField(help_text=u"磁盘使用上限(M)", default=0)
    net_stock = models.IntegerField(help_text=u"磁盘使用余量(M)", default=0)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, help_text=u"创建时间")
    update_time = models.DateTimeField(auto_now=True, help_text=u"更新时间")


