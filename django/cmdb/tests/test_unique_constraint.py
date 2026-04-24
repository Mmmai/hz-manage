from django.urls import reverse
from rest_framework import status

from cmdb.models import Models, ModelFields, UniqueConstraint
from cmdb.tests import CmdbAPITestCase


class UniqueConstraintViewSetTestCase(CmdbAPITestCase):

    def setUp(self):
        super().setUp()

        self.model = Models.objects.create(
            name="Test Model",
            description="Test model for unique constraints",
            built_in=False,
            create_user="admin",
            update_user="admin",
        )

        self.field1 = ModelFields.objects.create(
            model=self.model,
            name="test_field_1",
            verbose_name="Test Field 1",
            type="string",
            order=1,
            editable=True,
            required=True,
            description="Test field 1",
            create_user="admin",
            update_user="admin",
        )

        self.field2 = ModelFields.objects.create(
            model=self.model,
            name="test_field_2",
            verbose_name="Test Field 2",
            type="integer",
            order=2,
            editable=True,
            required=False,
            description="Test field 2",
            create_user="admin",
            update_user="admin",
        )

        self.normal_constraint = UniqueConstraint.objects.create(
            model=self.model,
            fields=[str(self.field1.id)],
            validate_null=False,
            built_in=False,
            description="Normal unique constraint",
            create_user="admin",
            update_user="admin",
        )

        self.built_in_constraint = UniqueConstraint.objects.create(
            model=self.model,
            fields=[str(self.field2.id)],
            validate_null=False,
            built_in=True,
            description="Built-in unique constraint",
            create_user="admin",
            update_user="admin",
        )

    def test_list_constraints(self):
        """GET list returns all constraints"""
        url = reverse('uniqueconstraint-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_constraint(self):
        """POST with model and fields creates a constraint"""
        url = reverse('uniqueconstraint-list')
        data = {
            'model': self.model.id,
            'fields': [str(self.field1.id), str(self.field2.id)],
            'description': 'New constraint',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UniqueConstraint.objects.count(), 3)

    def test_retrieve_constraint(self):
        """GET detail returns a single constraint"""
        url = reverse('uniqueconstraint-detail', args=[self.normal_constraint.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['id']), str(self.normal_constraint.id))

    def test_update_constraint(self):
        """PATCH description updates a normal constraint"""
        url = reverse('uniqueconstraint-detail', args=[self.normal_constraint.id])
        data = {'description': 'Updated description'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_constraint.refresh_from_db()
        self.assertEqual(self.normal_constraint.description, 'Updated description')

    def test_delete_constraint(self):
        """DELETE removes a normal constraint"""
        url = reverse('uniqueconstraint-detail', args=[self.normal_constraint.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UniqueConstraint.objects.filter(id=self.normal_constraint.id).exists()
        )

    def test_delete_builtin_forbidden(self):
        """DELETE built_in constraint returns 403"""
        url = reverse('uniqueconstraint-detail', args=[self.built_in_constraint.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            UniqueConstraint.objects.filter(id=self.built_in_constraint.id).exists()
        )

    def test_filter_by_model(self):
        """GET with model param filters constraints"""
        url = reverse('uniqueconstraint-list')
        response = self.client.get(
            url, {'model': str(self.model.id)}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_duplicate_fields_fails(self):
        """POST with same fields as existing constraint returns validation error"""
        url = reverse('uniqueconstraint-list')
        data = {
            'model': self.model.id,
            'fields': [str(self.field1.id)],
            'description': 'Duplicate constraint',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fields', response.data)

    def test_create_invalid_field_ids_fails(self):
        """POST with non-existent field IDs returns validation error"""
        import uuid

        url = reverse('uniqueconstraint-list')
        fake_id = str(uuid.uuid4())
        data = {
            'model': self.model.id,
            'fields': [fake_id],
            'description': 'Invalid fields constraint',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fields', response.data)

    def test_update_builtin_forbidden(self):
        """PATCH built_in constraint returns 403"""
        url = reverse('uniqueconstraint-detail', args=[self.built_in_constraint.id])
        data = {'description': 'Attempt to modify built-in'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
