from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from cmdb.models import ModelGroups, Models, ModelInstance, RelationDefinition, Relations
from cmdb.serializers import RelationsSerializer
from cmdb.tests import CmdbAPITestCase


class RelationDefinitionViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()
        # 1 group
        self.group = ModelGroups.objects.create(
            name='network',
            verbose_name='网络设备',
            built_in=False,
            editable=True,
            description='网络设备分组',
            create_user='admin',
            update_user='admin',
        )
        # 2 models
        self.source_model = Models.objects.create(
            name='Switch',
            verbose_name='交换机',
            model_group=self.group,
            built_in=False,
            description='交换机模型',
            create_user='admin',
            update_user='admin',
        )
        self.target_model = Models.objects.create(
            name='Server',
            verbose_name='服务器',
            model_group=self.group,
            built_in=False,
            description='服务器模型',
            create_user='admin',
            update_user='admin',
        )
        # 1 RelationDefinition
        self.relation_def = RelationDefinition.objects.create(
            name='connects',
            forward_verb='连接',
            reverse_verb='被连接',
            topology_type='daggered',
            description='交换机连接服务器',
            create_user='admin',
            update_user='admin',
        )
        self.relation_def.source_model.add(self.source_model)
        self.relation_def.target_model.add(self.target_model)

    # ---- CRUD ----

    def test_list_definitions(self):
        """测试获取关系定义列表"""
        url = reverse('relationdefinition-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'connects')

    @patch('cmdb.views.RelationDefinitionService.create_relation_definition')
    def test_create_definition(self, mock_create):
        """测试创建关系定义（委托给 RelationDefinitionService）"""
        # Use the existing relation_def as the mock return value (it's already saved)
        mock_create.return_value = self.relation_def

        url = reverse('relationdefinition-list')
        data = {
            'name': 'depends_on',
            'forward_verb': '依赖',
            'reverse_verb': '被依赖',
            'topology_type': 'directed',
            'description': '依赖关系',
            'source_model': [str(self.source_model.id)],
            'target_model': [str(self.target_model.id)],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called_once()

    def test_retrieve_definition(self):
        """测试获取单个关系定义详情"""
        url = reverse('relationdefinition-detail', args=[self.relation_def.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'connects')
        self.assertEqual(response.data['forward_verb'], '连接')

    def test_update_definition(self):
        """测试部分更新关系定义"""
        url = reverse('relationdefinition-detail', args=[self.relation_def.id])
        data = {'description': '更新后的描述'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.relation_def.refresh_from_db()
        self.assertEqual(self.relation_def.description, '更新后的描述')

    def test_delete_definition(self):
        """测试删除未被使用的关系定义"""
        url = reverse('relationdefinition-detail', args=[self.relation_def.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RelationDefinition.objects.filter(id=self.relation_def.id).exists())

    def test_delete_in_use_forbidden(self):
        """测试删除已被使用的关系定义返回 403"""
        # 创建实例和关系
        source_instance = ModelInstance.objects.create(
            model=self.source_model,
            instance_name='sw-01',
            create_user='admin',
            update_user='admin',
        )
        target_instance = ModelInstance.objects.create(
            model=self.target_model,
            instance_name='srv-01',
            create_user='admin',
            update_user='admin',
        )
        Relations.objects.create(
            source_instance=source_instance,
            target_instance=target_instance,
            relation=self.relation_def,
            create_user='admin',
            update_user='admin',
        )

        url = reverse('relationdefinition-detail', args=[self.relation_def.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(RelationDefinition.objects.filter(id=self.relation_def.id).exists())

    # ---- Filters / Search ----

    def test_filter_by_name(self):
        """测试按名称过滤关系定义"""
        url = reverse('relationdefinition-list')
        response = self.client.get(url, {'name': 'connects'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'connects')

    def test_search(self):
        """测试搜索功能"""
        url = reverse('relationdefinition-list')
        response = self.client.get(url, {'search': 'connects'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RelationsViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()
        # 1 group
        self.group = ModelGroups.objects.create(
            name='infra',
            verbose_name='基础设施',
            built_in=False,
            editable=True,
            description='基础设施分组',
            create_user='admin',
            update_user='admin',
        )
        # 2 models
        self.source_model = Models.objects.create(
            name='Switch',
            verbose_name='交换机',
            model_group=self.group,
            built_in=False,
            description='交换机模型',
            create_user='admin',
            update_user='admin',
        )
        self.target_model = Models.objects.create(
            name='Host',
            verbose_name='主机',
            model_group=self.group,
            built_in=False,
            description='主机模型',
            create_user='admin',
            update_user='admin',
        )
        # 2 instances
        self.source_instance = ModelInstance.objects.create(
            model=self.source_model,
            instance_name='sw-core-01',
            create_user='admin',
            update_user='admin',
        )
        self.target_instance = ModelInstance.objects.create(
            model=self.target_model,
            instance_name='host-web-01',
            create_user='admin',
            update_user='admin',
        )
        # 1 RelationDefinition
        self.relation_def = RelationDefinition.objects.create(
            name='connects',
            forward_verb='连接',
            reverse_verb='被连接',
            topology_type='daggered',
            description='交换机连接主机',
            create_user='admin',
            update_user='admin',
        )
        self.relation_def.source_model.add(self.source_model)
        self.relation_def.target_model.add(self.target_model)
        # 1 Relations instance
        self.relation = Relations.objects.create(
            source_instance=self.source_instance,
            target_instance=self.target_instance,
            relation=self.relation_def,
            create_user='admin',
            update_user='admin',
        )

    # ---- CRUD ----

    def test_list_relations(self):
        """测试获取关系列表"""
        url = reverse('relations-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    @patch.object(RelationsSerializer, 'validate', side_effect=lambda data: data)
    def test_create_relation(self, mock_validate):
        """测试创建关系（mock serializer.validate 以跳过 schema 校验）"""
        # Create a new target instance to avoid UniqueTogether violation
        new_target = ModelInstance.objects.create(
            model=self.target_model,
            instance_name='host-db-01',
            create_user='admin',
            update_user='admin',
        )
        url = reverse('relations-list')
        data = {
            'source_instance': str(self.source_instance.id),
            'target_instance': str(new_target.id),
            'relation': str(self.relation_def.id),
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Relations.objects.count(), 2)

    def test_retrieve_relation(self):
        """测试获取单个关系详情"""
        url = reverse('relations-detail', args=[self.relation.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.relation.id))

    def test_delete_relation(self):
        """测试删除关系"""
        url = reverse('relations-detail', args=[self.relation.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Relations.objects.filter(id=self.relation.id).exists())

    # ---- Filters ----

    def test_filter_by_relation(self):
        """测试按 relation 过滤关系"""
        url = reverse('relations-list')
        response = self.client.get(
            url,
            {'relation': str(self.relation_def.id)},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # ---- Bulk actions ----

    def test_bulk_delete_empty_fails(self):
        """测试批量删除不传 IDs 返回 400"""
        url = reverse('relations-bulk-delete')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
