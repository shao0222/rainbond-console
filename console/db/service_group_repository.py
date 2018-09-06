# -*- coding:utf-8 -*-
from console.models.services import ServiceGroupRelation
from console.models.services import ServiceGroup


class ServiceGroupRepository(object):
    def get_rel_region(self, service_id, tenant_id, region):
        try:
            return ServiceGroupRelation.objects.get(
                service_id=service_id, tenant_id=tenant_id, region_name=region
            )
        except ServiceGroupRelation.DoesNotExist:
            return None

    def get_by_pk(self,pk):
        try:
            return ServiceGroup.objects.get(pk=pk)
        except ServiceGroup.DoesNotExist:
            return None
