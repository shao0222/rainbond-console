webpackJsonp([1],{16:function(module,exports,__webpack_require__){"use strict";Object.defineProperty(exports,"__esModule",{value:!0});var volumepathTypeToCNMap={"share-file":"共享存储(文件)",local:"本地存储",memoryfs:"内存文件存储"},volumeUtil={getTypeCN:function(type){return volumepathTypeToCNMap[type]||"未知"}};exports.default=volumeUtil},19:function(module,exports,__webpack_require__){"use strict";function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj}}function _defineProperty(obj,key,value){return key in obj?Object.defineProperty(obj,key,{value:value,enumerable:!0,configurable:!0,writable:!0}):obj[key]=value,obj}Object.defineProperty(exports,"__esModule",{value:!0});var _pageController=__webpack_require__(2),_pageController2=_interopRequireDefault(_pageController),_appApiCenter=(__webpack_require__(4),__webpack_require__(1)),_pageAppApiCenter=__webpack_require__(3),_widget=__webpack_require__(0),_widget2=_interopRequireDefault(_widget),_volumeUtil=__webpack_require__(16),_volumeUtil2=_interopRequireDefault(_volumeUtil);__webpack_require__(34),__webpack_require__(33);var Msg=_widget2.default.Message,template=__webpack_require__(53),AppMnt=(0,_pageController2.default)({template:template,property:{tenantName:"",serviceAlias:"",servicecName:"",language:"",code_from:"",serviceId:"",renderData:{appInfo:{},pageData:{}}},method:{getInitData:function(){var _this=this;(0,_appApiCenter.getAppInfo)(this.tenantName,this.serviceAlias).done(function(appInfo){_this.renderData.appInfo=appInfo,(0,_pageAppApiCenter.getPageMntAppData)(_this.tenantName,_this.serviceAlias).done(function(pageData){var vList=pageData.volume_list||[],mList=pageData.mounted_apps||[];vList.forEach(function(item){item.volume_type_cn=_volumeUtil2.default.getTypeCN(item.volume_type)}),mList.forEach(function(item){item.dep_vol_type_cn=_volumeUtil2.default.getTypeCN(item.dep_vol_type)}),_this.renderData.pageData=pageData,_this.render()})})},handleRemoveDir:function(id){return(0,_appApiCenter.removeDir)(this.tenantName,this.serviceAlias,id)},handleConnectAppDisk:function(destServiceAlias){var self=this;(0,_appApiCenter.connectAppDisk)(this.tenantName,this.serviceAlias,destServiceAlias).done(function(data){Msg.success("操作成功"),self.getInitData()})},handleCutConnectAppDisk:function(id){var self=this;(0,_appApiCenter.cutConnectedAppDisk)(this.tenantName,this.serviceAlias,id).done(function(data){Msg.success("操作成功"),self.getInitData()})},showAddVolumeDialog:function(){var self=this,dialog=_widget2.default.create("addVolumepath",{serviceInfo:this.renderData.pageData.tenantServiceInfo,onOk:function(name,path,type){(0,_appApiCenter.addDir)(self.tenantName,self.serviceAlias,name,path,type).done(function(data){self.getInitData(),dialog.destroy()})}})}},domEvents:{"#add_volume_attr click":function(e){this.showAddVolumeDialog()},".removeDir click":function(e){var $target=$(e.currentTarget),id=$target.attr("data-id");id&&this.handleRemoveDir(id).done(function(){$target.parents("tr").remove()})},".connectAppDisk click":function(e){var destServiceAlias=$(e.currentTarget).parents("tr").attr("data-dest-service-alias");destServiceAlias&&this.handleConnectAppDisk(destServiceAlias)},".cutConnectAppDisk click":function(e){var id=$(e.currentTarget).attr("data-id");id&&this.handleCutConnectAppDisk(id)},".connectSharedAppDisk click":function(e){var _widget$create,_this2=this;_widget2.default.create("addSharedVolumepath",(_widget$create={tenantName:this.tenantName,serviceAlias:this.serviceAlias,serviceList:this.renderData.pageData.tenantServiceInfo},_defineProperty(_widget$create,"serviceAlias",this.renderData.pageData.serviceAlias),_defineProperty(_widget$create,"mntServiceIds",this.renderData.pageData.mntsids),_defineProperty(_widget$create,"onOk",function(){_this2.getInitData()}),_defineProperty(_widget$create,"onFail",function(){_this2.getInitData()}),_widget$create))}},onReady:function(){this.getInitData()}});window.AppMntController=AppMnt,exports.default=AppMnt},33:function(module,exports,__webpack_require__){"use strict";function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj}}function noop(){}var _widget=__webpack_require__(0),_widget2=_interopRequireDefault(_widget),_appApiCenter=__webpack_require__(1),_volumeUtil=__webpack_require__(16),_volumeUtil2=_interopRequireDefault(_volumeUtil),Msg=_widget2.default.Message;_widget2.default.define("addSharedVolumepath",{extend:"dialog",_defaultOption:function(obj,key,value){return key in obj?Object.defineProperty(obj,key,{value:value,enumerable:!0,configurable:!0,writable:!0}):obj[key]=value,obj}({onSuccess:noop,onFail:noop,onCancel:noop,width:"650px",height:"400px",title:"请选择要挂载的目录",tenantName:"",serviceAlias:"",serviceList:[],mntServiceIds:[]},"serviceAlias",""),_init:function(option){var self=this;option.domEvents={".btn-success click":function(){self.onOk()}},this.callParent(option),"addSharedVolumepath"==this.ClassName&&(this._create(),this.bind())},_create:function(){this.callParent();for(var datas=[],i=0;i<this.option.serviceList.length;i++)this.option.serviceList[i].service_alias!=this.otpion.serviceAlias&&this.option.mntServiceIds.indexOf(this.option.serviceList[i].service_id)<0&&datas.push(this.option.serviceList[i]);this.table=_widget2.default.create("tableList",{showPage:!0,pageSize:8,url:"/ajax/"+this.option.tenantName+"/"+this.option.serviceAlias+"/dep-mnts",columns:[{name:"dep_vol_name",text:"持久化名称",width:150},{name:"dep_vol_path",text:"持久化目录"},{name:"dep_vol_type",text:"持久化类型"},{name:"dep_app_name",text:"所属应用"},{name:"dep_app_group",text:"所属群组"}],render:{dep_vol_type:function(text,data){return _volumeUtil2.default.getTypeCN(text)}}}),this.setContent(this.table.getElement())},onOk:function(){var _this=this,volumeIds=this.table.getSelectedArrayByKey("dep_vol_id");if(!volumeIds.length)return void Msg.warning("请选择要挂载的持久化目录");(0,_appApiCenter.connectAppDisk)(this.option.tenantName,this.option.serviceAlias,volumeIds).done(function(data){_this.option.onOk&&_this.option.onOk(),_this.destroy()}).fail(function(data){_this.option.onFail&&_this.option.onFail(),_this.destroy()})},destroy:function(){this.table.destroy(),this.table=null,this.callParent()}})},34:function(module,exports,__webpack_require__){"use strict";function noop(){}var _widget=__webpack_require__(0),_widget2=function(obj){return obj&&obj.__esModule?obj:{default:obj}}(_widget),tmp=(__webpack_require__(1),__webpack_require__(50)),Msg=_widget2.default.Message;_widget2.default.define("addVolumepath",{extend:"dialog",_defaultOption:{width:"600px",height:"350px",title:"添加持久化目录",onOk:noop,serviceInfo:{}},_init:function(option){this.callParent(option),"addVolumepath"==this.ClassName&&(this._create(),this.bind())},_create:function(){this.callParent(),this.setContent(tmp),this.getElement().find(".fn-tips").tooltip(),"stateless"===this.option.serviceInfo.extend_method&&this.element.find(".local-radio").hide()},onOk:function(volume_name,volume_path,volume_type){this.option.onOk&&this.option.onOk(volume_name,volume_path,volume_type)},destroy:function(){this.unbind(),this.callParent()},bind:function(){this.callParent();var self=this,element=this.getElement();element.delegate(".btn-success","click",function(e){var volume_name=element.find("#volume_name").val();if(""==volume_name)return Msg.warning("持久化名称不能为空!"),!1;var volume_path=element.find("#volume_path").val();if(""==volume_path)return Msg.warning("持久化路径不能为空!"),!1;var volume_type=element.find("[name=volume_type]:checked").val();self.onOk(volume_name,volume_path,volume_type)})},unbind:function(){this.getElement().undelegate()}})},50:function(module,exports){module.exports='<form class="form-horizontal">\n  <div class="form-group">\n    <span for="volume_name" class="col-sm-2 control-label">名称</span>\n    <div class="col-sm-10">\n      <input type="text" class="form-control" id="volume_name" placeholder="请填写持久化名称">\n    </div>\n  </div>\n  <div class="form-group">\n    <span for="volume_path" class="col-sm-2 control-label">目录</span>\n    <div class="col-sm-10">\n      <input class="form-control" id="volume_path" placeholder="请填写持久化目录">\n    </div>\n  </div>\n  <div class="form-group">\n    <span for="inputPassword3" class="col-sm-2 control-label">类型</span>\n    <div class="col-sm-10">\n      <div class="radio">\n          <label class=" fn-tips"  data-toggle="tooltip" data-placement="top" title="分布式文件存储，可租户内共享挂载，适用于所有类型应用">\n            <input type="radio" name="volume_type" value="share-file" checked>\n            共享存储(文件)\n          </label>\n      </div>\n      <div class="radio local-radio">\n        <label class="fn-tips"  data-toggle="tooltip" data-placement="top" title="本地高速块存储设备，适用于有状态数据库服务">\n          <input type="radio" name="volume_type" value="local">\n          本地存储\n        </label>\n      </div>\n      <div class="radio">\n        <label class="fn-tips"  data-toggle="tooltip" data-placement="top" title="基于内存的存储设备，容量由内存量限制。应用重启数据即丢失，适用于高速暂存数据">\n          <input type="radio" name="volume_type" value="memoryfs">\n          内存文件存储\n        </label>\n      </div>\n\n    </div>\n  </div>\n</form>'},53:function(module,exports){module.exports='<section class="panel panel-default">\n    <div class="panel-heading clearfix">\n        持久化数据设置<small>(设置后需要重启服务)</small>\n    </div>\n    <div class="panel-body">\n        <table id="volume_table" class="table">\n            <thead>\n            <tr class="active">\n                <th>持久化名称</th>\n                <th>持久化目录</th>\n                <th>持久化类型</th>\n                <th class="text-right">操作</th>\n            </tr>\n            </thead>\n            <tbody>\n            {{each pageData.volume_list}}\n                <tr>\n                    <td>{{ $value.volume_name }}</td>\n                    <td>{{ $value.volume_path }}</td>\n                    <td>{{ $value.volume_type_cn }}</td>\n                    <td class="text-right">\n                        {{if appInfo.service.category == "application" }}\n                        <button type="button" class="btn btn-default btn-sm removeDir"\n                                data-id="{{ $value.ID }}">\n                            删除\n                        </button>\n                        {{/if}}\n                    </td>\n                </tr>\n                \n            {{/each}}\n            {{if pageData.volume_list.length == 0}}\n                 <tr>\n                    <td colspan="4" style="text-align: center">暂无数据</td>\n                </tr>\n            {{/if}}\n            </tbody>\n        </table>\n   </div>\n   {{if appInfo.service.category == "application" }}\n   <div class="panel-footer clearfix">\n        <button type="button" class="btn btn-success pull-right" id="add_volume_attr"\n                data-language="{{ appInfo.service.language }}">新增持久化设置\n        </button>\n   </div>\n   {{/if}}\n</section>\n\n\n<section class="panel panel-default">\n <div class="panel-heading">文件存储<small>(挂载了其他应用共享的持久化目录后需重启)</small></div>\n <div class="panel-body">\n    <table class="table">\n        <thead>\n        <tr class="active">\n            <th>持久化名称</th>\n            <th class="hidden-xs">持久化目录</th>\n            <th>持久化类型</th>\n            <th>所属应用</th>\n            <th class="hidden-xs">所属分组</th>\n            <th >操作</th>\n        </tr>\n        </thead>\n        <tbody>\n        {{each pageData.mounted_apps}}\n            <tr data-dest-service-alias="{{$value.service_alias}}">\n                <td>{{$value.dep_vol_name}}</td>\n                <td>{{$value.dep_vol_path}}</td>\n                <td>{{$value.dep_vol_type_cn}}</td>\n                <td class="hidden-xs">{{$value.dep_app_name}}</td>\n                <td>{{$value.dep_app_group}}</td>\n                <td class="text-right">\n                {{if pageData.actions[\'manage_service\'] || pageData.is_sys_admin}}\n                        <button data-id="{{$value.dep_vol_id}}" type="button" class="btn btn-default btn-sm cutConnectAppDisk">取消挂载</button>\n                {{/if}}\n                </td>\n            </tr>\n        {{/each}}\n        {{if pageData.mounted_apps.length == 0}}\n             <tr>\n                <td colspan="6" style="text-align: center">暂无数据</td>\n            </tr>\n        {{/if}}\n       </tbody>\n    </table>\n</div>\n{{if pageData.actions[\'manage_service\'] || pageData.is_sys_admin}}\n<div class="panel-footer clearfix">\n    <button type="button" class="btn btn-success pull-right connectSharedAppDisk">挂载目录</button>\n</div>\n{{/if}}\n</section>\n   \n\n'},69:function(module,exports,__webpack_require__){module.exports=__webpack_require__(19)}},[69]);