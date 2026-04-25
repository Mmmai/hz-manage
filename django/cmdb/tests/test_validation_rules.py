import json
from django.urls import reverse
from rest_framework import status
from cmdb.models import Models, ModelFields, ValidationRules
from cmdb.tests import CmdbAPITestCase


class ValidationRulesViewSetTestCase(CmdbAPITestCase):
    def setUp(self):
        super().setUp()

        self.model = Models.objects.create(
            name="Test Model",
            verbose_name="测试模型",
            description="Test model for validation rules",
            built_in=False,
            create_user="admin",
            update_user="admin",
        )

        self.normal_rule = ValidationRules.objects.create(
            name="regex_string",
            verbose_name="正则校验字符串",
            field_type="string",
            type="regex",
            rule="^[a-zA-Z0-9_]+$",
            built_in=False,
            editable=True,
            description="字母数字下划线正则",
            create_user="admin",
            update_user="admin",
        )

        self.built_in_rule = ValidationRules.objects.create(
            name="builtin_regex",
            verbose_name="内置正则",
            field_type="string",
            type="regex",
            rule="^\\d+$",
            built_in=True,
            editable=True,
            description="内置纯数字正则",
            create_user="admin",
            update_user="admin",
        )

        self.non_editable_rule = ValidationRules.objects.create(
            name="locked_regex",
            verbose_name="锁定正则",
            field_type="string",
            type="regex",
            rule=".*",
            built_in=False,
            editable=False,
            description="不可编辑规则",
            create_user="admin",
            update_user="admin",
        )

        self.in_use_rule = ValidationRules.objects.create(
            name="in_use_regex",
            verbose_name="使用中正则",
            field_type="string",
            type="regex",
            rule="^[A-Z]+$",
            built_in=False,
            editable=True,
            description="被字段引用的规则",
            create_user="admin",
            update_user="admin",
        )

        self.model_field = ModelFields.objects.create(
            model=self.model,
            name="ref_field",
            verbose_name="引用字段",
            type="string",
            order=1,
            editable=True,
            required=True,
            validation_rule=self.in_use_rule,
            description="引用校验规则的字段",
            create_user="admin",
            update_user="admin",
        )

    # ---------- CRUD ----------

    def test_list_rules(self):
        url = reverse("validationrules-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_create_rule(self):
        url = reverse("validationrules-list")
        data = {
            "name": "new_regex_rule",
            "verbose_name": "新建正则",
            "field_type": "string",
            "type": "regex",
            "rule": "^[a-z]+$",
            "description": "新建小写正则",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ValidationRules.objects.count(), 5)
        created = ValidationRules.objects.get(name="new_regex_rule")
        self.assertEqual(created.rule, "^[a-z]+$")

    def test_retrieve_rule(self):
        url = reverse("validationrules-detail", args=[self.normal_rule.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "regex_string")
        self.assertEqual(response.data["field_type"], "string")

    def test_update_rule(self):
        url = reverse("validationrules-detail", args=[self.normal_rule.id])
        data = {"description": "更新后的描述"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_rule.refresh_from_db()
        self.assertEqual(self.normal_rule.description, "更新后的描述")

    def test_delete_rule(self):
        url = reverse("validationrules-detail", args=[self.normal_rule.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ValidationRules.objects.filter(id=self.normal_rule.id).exists())

    # ---------- Delete guards ----------

    def test_delete_builtin_forbidden(self):
        url = reverse("validationrules-detail", args=[self.built_in_rule.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ValidationRules.objects.filter(id=self.built_in_rule.id).exists())

    def test_delete_non_editable_forbidden(self):
        url = reverse("validationrules-detail", args=[self.non_editable_rule.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ValidationRules.objects.filter(id=self.non_editable_rule.id).exists())

    def test_delete_in_use_forbidden(self):
        url = reverse("validationrules-detail", args=[self.in_use_rule.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ValidationRules.objects.filter(id=self.in_use_rule.id).exists())

    # ---------- Filtering ----------

    def test_filter_by_field_type(self):
        url = reverse("validationrules-list")
        response = self.client.get(url, {"field_type": "string"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

        response = self.client.get(url, {"field_type": "integer"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_filter_by_type(self):
        url = reverse("validationrules-list")
        response = self.client.get(url, {"type": "regex"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

        response = self.client.get(url, {"type": "range"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    # ---------- Search ----------

    def test_search(self):
        url = reverse("validationrules-list")
        response = self.client.get(url, {"search": "regex_string"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "regex_string")

    # ---------- Sorting ----------

    def test_sorting(self):
        url = reverse("validationrules-list")

        # ascending by name
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r["name"] for r in response.data["results"]]
        self.assertEqual(names, sorted(names))

        # descending by name
        response = self.client.get(url, {"ordering": "-name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r["name"] for r in response.data["results"]]
        self.assertEqual(names, sorted(names, reverse=True))

    # ---------- Enum rules ----------

    def test_create_enum_rule(self):
        url = reverse("validationrules-list")
        rule_content = json.dumps({"key1": "label1", "key2": "label2"})
        data = {
            "name": "enum_status",
            "verbose_name": "状态枚举",
            "field_type": "string",
            "type": "enum",
            "rule": rule_content,
            "description": "状态枚举选项",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = ValidationRules.objects.get(name="enum_status")
        self.assertEqual(created.type, "enum")
        self.assertEqual(json.loads(created.rule), {"key1": "label1", "key2": "label2"})

    def test_update_enum_rule(self):
        enum_rule = ValidationRules.objects.create(
            name="enum_priority",
            verbose_name="优先级枚举",
            field_type="string",
            type="enum",
            rule=json.dumps({"low": "低", "mid": "中", "high": "高"}),
            built_in=False,
            editable=True,
            description="优先级选项",
            create_user="admin",
            update_user="admin",
        )
        new_rule = json.dumps({"p0": "紧急", "p1": "高", "p2": "中", "p3": "低"})
        url = reverse("validationrules-detail", args=[enum_rule.id])
        response = self.client.patch(url, {"rule": new_rule})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enum_rule.refresh_from_db()
        self.assertEqual(
            json.loads(enum_rule.rule),
            {"p0": "紧急", "p1": "高", "p2": "中", "p3": "低"},
        )
