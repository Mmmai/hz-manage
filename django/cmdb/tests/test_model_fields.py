from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from cmdb.models import Models, ModelFields  # 修改导入的类名

class ModelFieldsViewSetTestCase(APITestCase):  # 修改测试类名
    def setUp(self):
        # 先创建一个 Models 实例，因为 ModelsFields 依赖它
        self.model = Models.objects.create(
            name="Test Model",
            description="Test model for fields",
            built_in=False,
            create_user="admin",
            update_user="admin"
        )
        
        # 创建测试用的字段数据
        self.field1 = ModelFields.objects.create(
            model=self.model,
            name="test_field_1",
            type="string",
            order=1,
            editable=True,
            required=True,
            description="Test field 1",
            create_user="admin",
            update_user="admin"
        )
        
        self.field2 = ModelFields.objects.create(
            model=self.model,
            name="test_field_2",
            type="integer",
            order=2,
            editable=True,
            required=False,
            description="Test field 2",
            create_user="admin",
            update_user="admin"
        )

    def test_list_fields(self):
        """测试获取字段列表"""
        url = reverse('modelfields-list')  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_field(self):
        """测试创建新字段"""
        url = reverse('modelfields-list')  # 修改 URL 名称
        data = {
            "model": self.model.id,
            "name": "new_field",
            "type": "boolean",
            "order": 3,
            "editable": True,
            "required": True,
            "description": "New test field",
            "create_user": "admin",
            "update_user": "admin"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ModelFields.objects.count(), 3)  # 修改类名引用

    def test_update_field(self):
        """测试更新字段"""
        url = reverse('modelfields-detail', args=[self.field1.id])  # 修改 URL 名称
        data = {
            "description": "Updated description"
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.field1.refresh_from_db()
        self.assertEqual(self.field1.description, "Updated description")

    def test_delete_field(self):
        """测试删除字段"""
        url = reverse('modelfields-detail', args=[self.field2.id])  # 修改 URL 名称
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ModelFields.objects.count(), 1)  # 修改类名引用

    def test_filter_fields(self):
        """测试字段筛选功能"""
        # 测试按类型筛选
        url = reverse('modelfields-list') + '?type=string'  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['type'], 'string')

        # 测试按必填项筛选
        url = reverse('modelfields-list') + '?required=true'  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['required'], True)

    def test_order_fields(self):
        """测试字段排序功能"""
        # 测试按顺序号正序排序
        url = reverse('modelfields-list') + '?ordering=order'  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['order'], 1)
        self.assertEqual(response.data['results'][1]['order'], 2)

        # 测试按顺序号倒序排序
        url = reverse('modelfields-list') + '?ordering=-order'  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['order'], 2)
        self.assertEqual(response.data['results'][1]['order'], 1)

        # 测试按创建时间排序
        url = reverse('modelfields-list') + '?ordering=create_time'  # 修改 URL 名称
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['results'][0]['create_time'] <= response.data['results'][1]['create_time'])

    def test_built_in_field(self):
        """测试内置字段"""
        # 创建一个内置字段
        built_in_field = ModelFields.objects.create(
            model=self.model,
            name="built_in_field",
            type="string",
            order=3,
            editable=False,
            required=True,
            built_in=True,
            description="Built-in test field",
            create_user="admin",
            update_user="admin"
        )

        # 测试删除内置字段（应该被禁止）
        url = reverse('modelfields-detail', args=[built_in_field.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ModelFields.objects.filter(id=built_in_field.id).exists())

        # 测试修改内置字段的受限属性（应该被禁止）
        data = {
            "name": "new_name",  # 内置字段不允许修改名称
            "type": "integer"    # 内置字段不允许修改类型
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        built_in_field.refresh_from_db()
        self.assertEqual(built_in_field.name, "built_in_field")
        self.assertEqual(built_in_field.type, "string")

        # 测试修改内置字段的非受限属性（应该允许）
        data = {
            "description": "Updated description",  # 允许修改描述
            "required": False                      # 允许修改是否必填
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        built_in_field.refresh_from_db()
        self.assertEqual(built_in_field.description, "Updated description")
        self.assertEqual(built_in_field.required, False)

    def test_non_editable_field(self):
        """测试不可编辑字段"""
        # 创建一个不可编辑字段
        non_editable_field = ModelFields.objects.create(
            model=self.model,
            name="non_editable_field",
            type="string",
            order=4,
            editable=False,
            required=True,
            description="Non-editable test field",
            create_user="admin",
            update_user="admin"
        )

        # 测试修改不可编辑字段的editable属性（应该被允许）
        url = reverse('modelfields-detail', args=[non_editable_field.id])
        data = {
            "editable": True
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        non_editable_field.refresh_from_db()
        self.assertTrue(non_editable_field.editable)

        # 测试获取不可编辑字段的列表
        url = reverse('modelfields-list') + '?editable=false'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        # 由于前面已经修改为可编辑，这里应该找不到不可编辑的字段
        self.assertEqual(len(response.data['results']), 0)

        # 恢复为不可编辑状态
        non_editable_field.editable = False
        non_editable_field.save()

        # 再次测试筛选
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'non_editable_field')