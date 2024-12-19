from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from core.models import Models

class ModelsViewSetTestCase(APITestCase):

    def setUp(self):
        # 创建测试数据
        self.model1 = Models.objects.create(
            name="Test Model 1",
            type="Type A",
            description="This is a test model 1",
            built_in=False,
            create_time=timezone.now(),
            update_time=timezone.now(),
            create_user="admin",
            update_user="admin"
        )
        self.model2 = Models.objects.create(
            name="Test Model 2",
            type="Type B",
            description="This is a test model 2",
            built_in=False,
            create_time=timezone.now(),
            update_time=timezone.now(),
            create_user="admin",
            update_user="admin"
        )
        self.built_in_model1 = Models.objects.create(
            name="Built-in Model 1",
            type="Type C",
            description="This is a built-in model 1",
            built_in=True,
            create_time=timezone.now(),
            update_time=timezone.now(),
            create_user="admin",
            update_user="admin"
        )
        self.built_in_model2 = Models.objects.create(
            name="Built-in Model 2",
            type="Type D",
            description="This is a built-in model 2",
            built_in=True,
            create_time=timezone.now(),
            update_time=timezone.now(),
            create_user="admin",
            update_user="admin"
        )

    def test_get_all_models(self):
        url = reverse('models-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)  # 确保有4个模型

    def test_pagination(self):
        url = reverse('models-list')
        response = self.client.get(url, {'page': 1, 'page_size': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 每页2个模型
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_filter_by_name(self):
        url = reverse('models-list')
        response = self.client.get(url, {'name': 'Test Model 1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Model 1')

    def test_filter_by_type(self):
        url = reverse('models-list')
        response = self.client.get(url, {'type': 'Type B'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Model 2')

    def test_filter_by_built_in(self):
        url = reverse('models-list')
        response = self.client.get(url, {'built_in': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            {model['name'] for model in response.data['results']},
            {'Built-in Model 1', 'Built-in Model 2'}
        )

    def test_filter_by_create_time(self):
        create_time = self.model1.create_time.strftime('%Y-%m-%dT%H:%M:%S')
        url = reverse('models-list')
        response = self.client.get(url, {'create_time_after': create_time}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 4)  # 至少有4个模型

    def test_invalid_filter_parameter(self):
        url = reverse('models-list')
        response = self.client.get(url, {'unknown_param': 'value'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 不会报错，但可能返回所有数据

    def test_sorting(self):
        url = reverse('models-list')
        response = self.client.get(url, {'ordering': 'name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [model['name'] for model in response.data['results']]
        self.assertEqual(names, sorted(names))  # 确保按名称排序

        response = self.client.get(url, {'ordering': '-name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [model['name'] for model in response.data['results']]
        self.assertEqual(names, sorted(names, reverse=True))  # 确保按名称降序排序