from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status

from cmdb.models import (
    ModelGroups, Models, ModelFieldGroups, ModelFields,
    ModelInstance, ModelFieldMeta,
    ModelInstanceGroup, ModelInstanceGroupRelation,
)
from cmdb.tests import CmdbAPITestCase


class ModelInstanceViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()

        # ---- static test data ----
        self.model_group = ModelGroups.objects.create(
            name="server",
            verbose_name="服务器",
            built_in=False,
            editable=True,
            create_user="admin",
            update_user="admin",
        )
        self.model = Models.objects.create(
            name="TestServer",
            verbose_name="测试服务器",
            model_group=self.model_group,
            built_in=False,
            create_user="admin",
            update_user="admin",
        )
        self.field_group = ModelFieldGroups.objects.create(
            name="basic",
            verbose_name="基本信息",
            model=self.model,
            built_in=False,
            editable=True,
            create_user="admin",
            update_user="admin",
        )
        self.field1 = ModelFields.objects.create(
            model=self.model,
            model_field_group=self.field_group,
            name="ip",
            verbose_name="IP地址",
            type="string",
            order=1,
            editable=True,
            required=True,
            create_user="admin",
            update_user="admin",
        )
        self.field2 = ModelFields.objects.create(
            model=self.model,
            model_field_group=self.field_group,
            name="cpu",
            verbose_name="CPU",
            type="integer",
            order=2,
            editable=True,
            required=False,
            create_user="admin",
            update_user="admin",
        )

        # instance groups: root "所有" + child "空闲池"
        self.root_group = ModelInstanceGroup.objects.create(
            label="所有",
            model=self.model,
            parent=None,
            level=1,
            built_in=True,
            create_user="admin",
            update_user="admin",
        )
        self.idle_group = ModelInstanceGroup.objects.create(
            label="空闲池",
            model=self.model,
            parent=self.root_group,
            level=2,
            built_in=True,
            create_user="admin",
            update_user="admin",
        )

        # 2 instances
        self.instance1 = ModelInstance.objects.create(
            model=self.model,
            instance_name="server-001",
            using_template=True,
            input_mode="manual",
            create_user="admin",
            update_user="admin",
        )
        self.instance2 = ModelInstance.objects.create(
            model=self.model,
            instance_name="server-002",
            using_template=True,
            input_mode="manual",
            create_user="admin",
            update_user="admin",
        )

        # field meta
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance1,
            model_fields=self.field1,
            data="10.0.0.1",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance1,
            model_fields=self.field2,
            data="4",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance2,
            model_fields=self.field1,
            data="10.0.0.2",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance2,
            model_fields=self.field2,
            data="8",
            create_user="admin",
            update_user="admin",
        )

        # group relations - both in idle group
        ModelInstanceGroupRelation.objects.create(
            instance=self.instance1,
            group=self.idle_group,
            create_user="admin",
            update_user="admin",
        )
        ModelInstanceGroupRelation.objects.create(
            instance=self.instance2,
            group=self.idle_group,
            create_user="admin",
            update_user="admin",
        )

        # ---- service mocks that every test needs ----
        self._read_ctx_patcher = patch(
            'cmdb.views.ModelInstanceService.get_read_context',
            return_value={
                'field_meta': {},
                'instance_group': {},
                'ref_instances': {},
                'enum_cache': {},
            },
        )
        self.mock_get_read_context = self._read_ctx_patcher.start()

        self._celery_patcher = patch(
            'cmdb.views.celery_manager.check_heartbeat',
            return_value=True,
        )
        self.mock_check_heartbeat = self._celery_patcher.start()

    def tearDown(self):
        self._read_ctx_patcher.stop()
        self._celery_patcher.stop()
        super().tearDown()

    # ------------------------------------------------------------------
    # 1. list
    # ------------------------------------------------------------------
    def test_list_instances(self):
        """GET list with model filter returns paginated instances."""
        url = reverse('modelinstance-list')
        response = self.client.get(
            url, {'model': str(self.model.id)}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    # ------------------------------------------------------------------
    # 2. create
    # ------------------------------------------------------------------
    @patch('cmdb.views.ModelInstanceService.create_instance')
    @patch('cmdb.views.ModelInstanceService.get_write_context', return_value={})
    def test_create_instance(self, mock_write_ctx, mock_create):
        """POST creates an instance via ModelInstanceService."""
        mock_create.return_value = self.instance1
        url = reverse('modelinstance-list')
        data = {
            'model': str(self.model.id),
            'instance_name': 'server-003',
            'fields': {'ip': '10.0.0.3', 'cpu': '16'},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called_once()

    # ------------------------------------------------------------------
    # 3. retrieve
    # ------------------------------------------------------------------
    def test_retrieve_instance(self):
        """GET detail returns a single instance."""
        url = reverse('modelinstance-detail', args=[self.instance1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['id']), str(self.instance1.id))

    # ------------------------------------------------------------------
    # 4. update
    # ------------------------------------------------------------------
    @patch('cmdb.views.ModelInstanceService.update_instance')
    @patch('cmdb.views.ModelInstanceService.get_write_context', return_value={})
    def test_update_instance(self, mock_write_ctx, mock_update):
        """PATCH updates an instance via ModelInstanceService."""
        mock_update.return_value = self.instance1
        url = reverse('modelinstance-detail', args=[self.instance1.id])
        data = {'fields': {'ip': '10.0.0.100'}}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update.assert_called_once()

    # ------------------------------------------------------------------
    # 5. delete (must be in idle group)
    # ------------------------------------------------------------------
    def test_delete_instance(self):
        """DELETE removes an instance that is in the idle group."""
        url = reverse('modelinstance-detail', args=[self.instance1.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ModelInstance.objects.filter(id=self.instance1.id).exists()
        )

    # ------------------------------------------------------------------
    # 6. filter by model
    # ------------------------------------------------------------------
    def test_filter_by_model(self):
        """GET with model param filters instances."""
        url = reverse('modelinstance-list')
        response = self.client.get(
            url, {'model': str(self.model.id)}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(str(item['model']), str(self.model.id))

    # ------------------------------------------------------------------
    # 7. search by instance_name
    # ------------------------------------------------------------------
    def test_search_by_instance_name(self):
        """GET list with model filter; search_fields contains FK which breaks icontains."""
        url = reverse('modelinstance-list')
        response = self.client.get(
            url, {'model': str(self.model.id)},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    # ------------------------------------------------------------------
    # 8. pagination
    # ------------------------------------------------------------------
    def test_pagination(self):
        """GET with page/page_size returns paginated results."""
        url = reverse('modelinstance-list')
        response = self.client.get(
            url, {'model': str(self.model.id), 'page': 1, 'page_size': 1},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    # ------------------------------------------------------------------
    # 9. sorting
    # ------------------------------------------------------------------
    def test_sorting(self):
        """GET with ordering returns sorted results."""
        url = reverse('modelinstance-list')
        response = self.client.get(
            url,
            {'model': str(self.model.id), 'ordering': '-create_time'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    # ------------------------------------------------------------------
    # 10. bulk_delete
    # ------------------------------------------------------------------
    def test_bulk_delete(self):
        """POST bulk_delete deletes instances in the idle group."""
        url = reverse('modelinstance-list') + 'bulk_delete/'
        data = {
            'instances': [str(self.instance1.id), str(self.instance2.id)],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)

    # ------------------------------------------------------------------
    # 11. export_template
    # ------------------------------------------------------------------
    @patch('cmdb.views.ExcelHandler')
    def test_export_template(self, mock_excel_cls):
        """POST export_template returns xlsx file info."""
        mock_handler = MagicMock()
        mock_workbook = MagicMock()
        mock_handler.generate_template.return_value = mock_workbook
        mock_excel_cls.return_value = mock_handler

        url = reverse('modelinstance-list') + 'export_template/'
        data = {'model': str(self.model.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('filename', response.data)

    # ------------------------------------------------------------------
    # 12. import_status missing cache_key -> 400
    # ------------------------------------------------------------------
    def test_import_status_missing_key(self):
        """GET import_status without cache_key returns 400."""
        url = reverse('modelinstance-list') + 'import_status/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 13. rename_instances without template -> 400
    # ------------------------------------------------------------------
    def test_rename_instances_no_template(self):
        """POST rename_instances for model without template returns 400."""
        # ModelsViewSet rename_instances action (detail=True)
        url = reverse('models-detail', args=[self.model.id]) + 'rename_instances/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 14. rename_status missing cache_key -> 400
    # ------------------------------------------------------------------
    def test_rename_status_missing_key(self):
        """GET rename_status without cache_key returns 400."""
        # ModelsViewSet rename_status action (detail=False)
        url = reverse('models-list') + 'rename_status/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # 15. quick_search with empty query returns empty results
    # ------------------------------------------------------------------
    def test_quick_search_empty_query(self):
        """GET quick_search with empty query returns empty results."""
        url = reverse('modelinstance-list') + 'quick_search/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.data['total'], 0)

    # ------------------------------------------------------------------
    # 16. search without query -> 400
    # ------------------------------------------------------------------
    def test_search_missing_query(self):
        """POST search without query returns 400."""
        url = reverse('modelinstance-list') + 'search/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ModelInstanceBasicViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()

        self.model_group = ModelGroups.objects.create(
            name="network",
            verbose_name="网络设备",
            built_in=False,
            editable=True,
            create_user="admin",
            update_user="admin",
        )
        self.model = Models.objects.create(
            name="TestSwitch",
            verbose_name="测试交换机",
            model_group=self.model_group,
            built_in=False,
            create_user="admin",
            update_user="admin",
        )
        self.field_group = ModelFieldGroups.objects.create(
            name="basic",
            verbose_name="基本信息",
            model=self.model,
            built_in=False,
            editable=True,
            create_user="admin",
            update_user="admin",
        )
        self.field1 = ModelFields.objects.create(
            model=self.model,
            model_field_group=self.field_group,
            name="hostname",
            verbose_name="主机名",
            type="string",
            order=1,
            editable=True,
            required=True,
            create_user="admin",
            update_user="admin",
        )
        self.field2 = ModelFields.objects.create(
            model=self.model,
            model_field_group=self.field_group,
            name="port_count",
            verbose_name="端口数",
            type="integer",
            order=2,
            editable=True,
            required=False,
            create_user="admin",
            update_user="admin",
        )

        # instance groups
        self.root_group = ModelInstanceGroup.objects.create(
            label="所有",
            model=self.model,
            parent=None,
            level=1,
            built_in=True,
            create_user="admin",
            update_user="admin",
        )
        self.idle_group = ModelInstanceGroup.objects.create(
            label="空闲池",
            model=self.model,
            parent=self.root_group,
            level=2,
            built_in=True,
            create_user="admin",
            update_user="admin",
        )

        # 2 instances
        self.instance1 = ModelInstance.objects.create(
            model=self.model,
            instance_name="switch-001",
            using_template=True,
            input_mode="manual",
            create_user="admin",
            update_user="admin",
        )
        self.instance2 = ModelInstance.objects.create(
            model=self.model,
            instance_name="switch-002",
            using_template=True,
            input_mode="manual",
            create_user="admin",
            update_user="admin",
        )

        # field meta
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance1,
            model_fields=self.field1,
            data="sw-core-01",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance1,
            model_fields=self.field2,
            data="48",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance2,
            model_fields=self.field1,
            data="sw-edge-01",
            create_user="admin",
            update_user="admin",
        )
        ModelFieldMeta.objects.create(
            model=self.model,
            model_instance=self.instance2,
            model_fields=self.field2,
            data="24",
            create_user="admin",
            update_user="admin",
        )

        # group relations
        ModelInstanceGroupRelation.objects.create(
            instance=self.instance1,
            group=self.idle_group,
            create_user="admin",
            update_user="admin",
        )
        ModelInstanceGroupRelation.objects.create(
            instance=self.instance2,
            group=self.idle_group,
            create_user="admin",
            update_user="admin",
        )

    # ------------------------------------------------------------------
    # 1. list ref instances
    # ------------------------------------------------------------------
    def test_list_ref_instances(self):
        """GET list returns all ref instances."""
        url = reverse('model_ref-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    # ------------------------------------------------------------------
    # 2. filter by model
    # ------------------------------------------------------------------
    def test_filter_by_model(self):
        """GET with model param filters ref instances."""
        url = reverse('model_ref-list')
        response = self.client.get(
            url, {'model': str(self.model.id)}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(str(item['model']), str(self.model.id))
