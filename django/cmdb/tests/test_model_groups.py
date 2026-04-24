from django.urls import reverse
from rest_framework import status
from django.utils import timezone

from cmdb.models import ModelGroups
from cmdb.tests import CmdbAPITestCase


class ModelGroupsViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()
        # 2 normal groups
        self.group1 = ModelGroups.objects.create(
            name="network",
            verbose_name="网络设备",
            built_in=False,
            editable=True,
            description="网络设备分组",
            create_user="admin",
            update_user="admin",
        )
        self.group2 = ModelGroups.objects.create(
            name="server",
            verbose_name="服务器",
            built_in=False,
            editable=True,
            description="服务器分组",
            create_user="admin",
            update_user="admin",
        )
        # 1 built_in group
        self.built_in_group = ModelGroups.objects.create(
            name="system",
            verbose_name="系统内置",
            built_in=True,
            editable=True,
            description="系统内置分组",
            create_user="admin",
            update_user="admin",
        )
        # 1 non-editable group
        self.non_editable_group = ModelGroups.objects.create(
            name="readonly",
            verbose_name="只读分组",
            built_in=False,
            editable=False,
            description="不可编辑分组",
            create_user="admin",
            update_user="admin",
        )

    # ---- CRUD ----

    def test_list_groups(self):
        """测试获取模型分组列表"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_create_group(self):
        """测试创建模型分组"""
        url = reverse('modelgroups-list')
        data = {
            "name": "storage",
            "verbose_name": "存储设备",
            "description": "存储设备分组",
            "create_user": "admin",
            "update_user": "admin",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ModelGroups.objects.count(), 5)
        self.assertEqual(response.data['name'], 'storage')

    def test_retrieve_group(self):
        """测试获取单个模型分组详情"""
        url = reverse('modelgroups-detail', args=[self.group1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'network')

    def test_update_group(self):
        """测试更新模型分组"""
        url = reverse('modelgroups-detail', args=[self.group1.id])
        data = {"description": "更新后的描述"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group1.refresh_from_db()
        self.assertEqual(self.group1.description, "更新后的描述")

    def test_delete_group(self):
        """测试删除非内置、可编辑的模型分组"""
        url = reverse('modelgroups-detail', args=[self.group1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ModelGroups.objects.filter(id=self.group1.id).exists())

    def test_delete_builtin_group_forbidden(self):
        """测试删除内置分组返回 403"""
        url = reverse('modelgroups-detail', args=[self.built_in_group.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ModelGroups.objects.filter(id=self.built_in_group.id).exists())

    def test_delete_non_editable_group_forbidden(self):
        """测试删除不可编辑分组返回 403"""
        url = reverse('modelgroups-detail', args=[self.non_editable_group.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ModelGroups.objects.filter(id=self.non_editable_group.id).exists())

    # ---- Filters / Search / Ordering / Pagination ----

    def test_filter_by_name(self):
        """测试按名称过滤"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, {'name': 'network'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'network')

    def test_filter_by_builtin(self):
        """测试按 built_in 过滤"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, {'built_in': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'system')

    def test_search(self):
        """测试搜索功能"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, {'search': 'server'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'server')

    def test_sorting(self):
        """测试排序功能"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, {'ordering': 'name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, sorted(names))

        response = self.client.get(url, {'ordering': '-name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['results']]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_pagination(self):
        """测试分页功能"""
        url = reverse('modelgroups-list')
        response = self.client.get(url, {'page': 1, 'page_size': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    # ---- Serializer validation ----

    def test_create_duplicate_name_fails(self):
        """测试创建重名分组失败（不区分大小写）"""
        url = reverse('modelgroups-list')
        data = {
            "name": "Network",  # 与 group1 的 'network' 冲突（不区分大小写）
            "verbose_name": "重复名称",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_builtin_name_forbidden(self):
        """测试修改内置分组名称返回 403"""
        url = reverse('modelgroups-detail', args=[self.built_in_group.id])
        data = {"name": "new_system_name"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.built_in_group.refresh_from_db()
        self.assertEqual(self.built_in_group.name, 'system')

    def test_update_non_editable_name_forbidden(self):
        """测试修改不可编辑分组名称返回 403"""
        url = reverse('modelgroups-detail', args=[self.non_editable_group.id])
        data = {"name": "new_readonly_name"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.non_editable_group.refresh_from_db()
        self.assertEqual(self.non_editable_group.name, 'readonly')
