import uuid
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status

from cmdb.models import Models, ModelFieldGroups
from cmdb.tests import CmdbAPITestCase


class ModelFieldGroupsViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()
        self.model_obj = Models.objects.create(
            name="TestModel",
            verbose_name="测试模型",
            description="A model for field group tests",
            built_in=False,
            create_user="admin",
            update_user="admin",
        )
        # 2 normal field groups
        self.fg1 = ModelFieldGroups.objects.create(
            name="basic_info",
            verbose_name="基本信息",
            model=self.model_obj,
            built_in=False,
            editable=True,
            description="基本信息分组",
            create_user="admin",
            update_user="admin",
        )
        self.fg2 = ModelFieldGroups.objects.create(
            name="network_info",
            verbose_name="网络信息",
            model=self.model_obj,
            built_in=False,
            editable=True,
            description="网络信息分组",
            create_user="admin",
            update_user="admin",
        )
        # 1 built_in field group
        self.built_in_fg = ModelFieldGroups.objects.create(
            name="system_info",
            verbose_name="系统内置",
            model=self.model_obj,
            built_in=True,
            editable=True,
            description="系统内置分组",
            create_user="admin",
            update_user="admin",
        )
        # 1 non-editable field group
        self.non_editable_fg = ModelFieldGroups.objects.create(
            name="readonly_info",
            verbose_name="只读分组",
            model=self.model_obj,
            built_in=False,
            editable=False,
            description="不可编辑分组",
            create_user="admin",
            update_user="admin",
        )

    # ---- CRUD ----

    def test_list_field_groups(self):
        """测试获取字段分组列表"""
        url = reverse('modelfieldgroups-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_create_field_group(self):
        """测试创建字段分组"""
        url = reverse('modelfieldgroups-list')
        data = {
            "name": "extra_info",
            "verbose_name": "扩展信息",
            "model": self.model_obj.id,
            "description": "扩展信息分组",
            "create_user": "admin",
            "update_user": "admin",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ModelFieldGroups.objects.count(), 5)
        self.assertEqual(response.data['name'], 'extra_info')

    def test_retrieve_field_group(self):
        """测试获取单个字段分组详情"""
        url = reverse('modelfieldgroups-detail', args=[self.fg1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'basic_info')

    def test_update_field_group(self):
        """测试更新字段分组"""
        url = reverse('modelfieldgroups-detail', args=[self.fg1.id])
        data = {"description": "更新后的描述"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fg1.refresh_from_db()
        self.assertEqual(self.fg1.description, "更新后的描述")

    def test_delete_field_group(self):
        """测试删除非内置、可编辑的字段分组"""
        url = reverse('modelfieldgroups-detail', args=[self.fg1.id])
        with patch('cmdb.views.ModelFieldGroupsService.delete_field_group'):
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_builtin_forbidden(self):
        """测试删除内置字段分组返回 403"""
        url = reverse('modelfieldgroups-detail', args=[self.built_in_fg.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ModelFieldGroups.objects.filter(id=self.built_in_fg.id).exists())

    def test_delete_non_editable_forbidden(self):
        """测试删除不可编辑字段分组返回 403"""
        url = reverse('modelfieldgroups-detail', args=[self.non_editable_fg.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ModelFieldGroups.objects.filter(id=self.non_editable_fg.id).exists())

    # ---- Filters / Search / Ordering ----

    def test_filter_by_model(self):
        """测试按 model 过滤字段分组"""
        url = reverse('modelfieldgroups-list')
        response = self.client.get(url, {'model': self.model_obj.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

        # 用一个不存在的 model id 过滤应返回空
        response = self.client.get(url, {'model': uuid.uuid4()}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_by_builtin(self):
        """测试按 built_in 过滤字段分组"""
        url = reverse('modelfieldgroups-list')
        response = self.client.get(url, {'built_in': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'system_info')

    def test_search(self):
        """测试搜索功能"""
        url = reverse('modelfieldgroups-list')
        response = self.client.get(url, {'search': 'network'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'network_info')

    def test_sorting(self):
        """测试排序功能"""
        url = reverse('modelfieldgroups-list')
        response = self.client.get(url, {'ordering': 'name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, sorted(names))

        response = self.client.get(url, {'ordering': '-name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, sorted(names, reverse=True))

    # ---- Serializer validation ----

    def test_create_duplicate_name(self):
        """测试创建重名字段分组失败（不区分大小写）"""
        url = reverse('modelfieldgroups-list')
        data = {
            "name": "Basic_Info",  # 与 fg1 的 'basic_info' 冲突（不区分大小写）
            "verbose_name": "重复名称",
            "model": self.model_obj.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
