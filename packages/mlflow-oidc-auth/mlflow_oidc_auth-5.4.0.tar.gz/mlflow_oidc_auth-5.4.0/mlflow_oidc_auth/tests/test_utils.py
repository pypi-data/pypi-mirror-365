import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import BAD_REQUEST, INVALID_PARAMETER_VALUE, RESOURCE_DOES_NOT_EXIST

from mlflow_oidc_auth.permissions import Permission
from mlflow_oidc_auth.utils import (
    PermissionResult,
    can_manage_experiment,
    can_manage_registered_model,
    can_read_experiment,
    can_read_registered_model,
    check_experiment_permission,
    check_prompt_permission,
    check_registered_model_permission,
    check_admin_permission,
    effective_experiment_permission,
    effective_prompt_permission,
    effective_registered_model_permission,
    fetch_all_experiments,
    fetch_all_prompts,
    fetch_all_registered_models,
    fetch_experiments_paginated,
    fetch_registered_models_paginated,
    fetch_readable_experiments,
    fetch_readable_registered_models,
    fetch_readable_logged_models,
    get_experiment_id,
    get_is_admin,
    get_model_name,
    get_model_id,
    get_optional_request_param,
    get_permission_from_store_or_default,
    get_request_param,
    get_url_param,
    get_optional_url_param,
    get_username,
    _get_registered_model_permission_from_regex,
    _get_experiment_permission_from_regex,
    _get_registered_model_group_permission_from_regex,
    _get_experiment_group_permission_from_regex,
    _permission_prompt_sources_config,
    _permission_experiment_sources_config,
    _permission_registered_model_sources_config,
    _experiment_id_from_name,
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_username")
    def test_get_is_admin(self, mock_get_username, mock_store):
        with self.app.test_request_context():
            mock_get_username.return_value = "user"
            mock_store.get_user.return_value.is_admin = True
            self.assertTrue(get_is_admin())
            mock_store.get_user.return_value.is_admin = False
            self.assertFalse(get_is_admin())

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    def test_get_permission_from_store_or_default(self, mock_get_permission, mock_config, mock_store):
        with self.app.test_request_context():
            mock_store_permission_user_func = MagicMock()
            mock_store_permission_group_func = MagicMock()
            mock_store_permission_user_func.return_value = "user_perm"
            mock_store_permission_group_func.return_value = "group_perm"
            mock_get_permission.return_value = Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True)
            mock_config.PERMISSION_SOURCE_ORDER = ["user", "group"]
            mock_config.DEFAULT_MLFLOW_PERMISSION = "default_perm"

            # user permission found
            result = get_permission_from_store_or_default({"user": mock_store_permission_user_func, "group": mock_store_permission_group_func})
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "user")

            # user not found, group found
            mock_store_permission_user_func.side_effect = MlflowException("", RESOURCE_DOES_NOT_EXIST)
            result = get_permission_from_store_or_default({"user": mock_store_permission_user_func, "group": mock_store_permission_group_func})
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "group")

            # both not found, fallback to default
            mock_store_permission_group_func.side_effect = MlflowException("", RESOURCE_DOES_NOT_EXIST)
            result = get_permission_from_store_or_default({"user": mock_store_permission_user_func, "group": mock_store_permission_group_func})
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "fallback")

            # invalid source in config
            mock_config.PERMISSION_SOURCE_ORDER = ["invalid"]
            # Just call and check fallback, don't assert logs
            result = get_permission_from_store_or_default({"user": mock_store_permission_user_func, "group": mock_store_permission_group_func})
            self.assertEqual(result.type, "fallback")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_can_manage_experiment(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True), "user"
            )
            self.assertTrue(can_manage_experiment("exp_id", "user"))
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=False), "user"
            )
            self.assertFalse(can_manage_experiment("exp_id", "user"))

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_can_manage_registered_model(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True), "user"
            )
            self.assertTrue(can_manage_registered_model("model_name", "user"))
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=False), "user"
            )
            self.assertFalse(can_manage_registered_model("model_name", "user"))

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_is_admin")
    @patch("mlflow_oidc_auth.utils.get_username")
    @patch("mlflow_oidc_auth.utils.get_experiment_id")
    @patch("mlflow_oidc_auth.utils.can_manage_experiment")
    @patch("mlflow_oidc_auth.utils.make_forbidden_response")
    def test_check_experiment_permission(
        self,
        mock_make_forbidden_response,
        mock_can_manage_experiment,
        mock_get_experiment_id,
        mock_get_username,
        mock_get_is_admin,
        mock_store,
    ):
        with self.app.test_request_context():
            mock_get_is_admin.return_value = False
            mock_get_username.return_value = "user"
            mock_get_experiment_id.return_value = "exp_id"
            mock_can_manage_experiment.return_value = False
            mock_make_forbidden_response.return_value = "forbidden"

            @check_experiment_permission
            def mock_func():
                return "success"

            self.assertEqual(mock_func(), "forbidden")

            mock_can_manage_experiment.return_value = True
            self.assertEqual(mock_func(), "success")

            # Admin always allowed
            mock_get_is_admin.return_value = True
            self.assertEqual(mock_func(), "success")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_is_admin")
    @patch("mlflow_oidc_auth.utils.get_username")
    @patch("mlflow_oidc_auth.utils.get_model_name")
    @patch("mlflow_oidc_auth.utils.can_manage_registered_model")
    @patch("mlflow_oidc_auth.utils.make_forbidden_response")
    def test_check_registered_model_permission(
        self,
        mock_make_forbidden_response,
        mock_can_manage_registered_model,
        mock_get_model_name,
        mock_get_username,
        mock_get_is_admin,
        mock_store,
    ):
        with self.app.test_request_context():
            mock_get_is_admin.return_value = False
            mock_get_username.return_value = "user"
            mock_get_model_name.return_value = "model_name"
            mock_can_manage_registered_model.return_value = False
            mock_make_forbidden_response.return_value = "forbidden"

            @check_registered_model_permission
            def mock_func():
                return "success"

            self.assertEqual(mock_func(), "forbidden")

            mock_can_manage_registered_model.return_value = True
            self.assertEqual(mock_func(), "success")

            # Admin always allowed
            mock_get_is_admin.return_value = True
            self.assertEqual(mock_func(), "success")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_is_admin")
    @patch("mlflow_oidc_auth.utils.get_username")
    @patch("mlflow_oidc_auth.utils.get_model_name")
    @patch("mlflow_oidc_auth.utils.can_manage_registered_model")
    @patch("mlflow_oidc_auth.utils.make_forbidden_response")
    def test_check_prompt_permission(
        self,
        mock_make_forbidden_response,
        mock_can_manage_registered_model,
        mock_get_model_name,
        mock_get_username,
        mock_get_is_admin,
        mock_store,
    ):
        with self.app.test_request_context():
            mock_get_is_admin.return_value = False
            mock_get_username.return_value = "user"
            mock_get_model_name.return_value = "prompt_name"
            mock_can_manage_registered_model.return_value = False
            mock_make_forbidden_response.return_value = "forbidden"

            @check_prompt_permission
            def mock_func():
                return "success"

            self.assertEqual(mock_func(), "forbidden")

            mock_can_manage_registered_model.return_value = True
            self.assertEqual(mock_func(), "success")

            # Admin always allowed
            mock_get_is_admin.return_value = True
            self.assertEqual(mock_func(), "success")

    def test_get_request_param(self):
        # GET method, param present
        with self.app.test_request_context("/?foo=bar", method="GET"):
            self.assertEqual(get_request_param("foo"), "bar")
        # POST method, param present
        with self.app.test_request_context("/", method="POST", json={"foo": "baz"}):
            self.assertEqual(get_request_param("foo"), "baz")
        # param missing, run_id fallback to run_uuid
        with self.app.test_request_context("/", method="GET"):
            with patch("mlflow_oidc_auth.utils.get_request_param", return_value="uuid_val") as mock_get:
                self.assertEqual(get_request_param("run_id"), "uuid_val")
        # param missing, not run_id
        with self.app.test_request_context("/", method="GET"):
            with self.assertRaises(MlflowException) as cm:
                get_request_param("notfound")
            self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")
        # unsupported method
        with self.app.test_request_context("/", method="PUT"):
            with self.assertRaises(MlflowException) as cm:
                get_request_param("foo")
            self.assertEqual(cm.exception.error_code, "BAD_REQUEST")

    def test_get_optional_request_param(self):
        # GET method, param present
        with self.app.test_request_context("/?foo=bar", method="GET"):
            self.assertEqual(get_optional_request_param("foo"), "bar")
        # POST method, param present
        with self.app.test_request_context("/", method="POST", json={"foo": "baz"}):
            self.assertEqual(get_optional_request_param("foo"), "baz")
        # param missing
        with self.app.test_request_context("/", method="GET"):
            self.assertIsNone(get_optional_request_param("notfound"))
        # unsupported method
        with self.app.test_request_context("/", method="PUT"):
            with self.assertRaises(MlflowException) as cm:
                get_optional_request_param("foo")
            self.assertEqual(cm.exception.error_code, "BAD_REQUEST")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_id(self, mock_tracking_store):
        # GET method, experiment_id present
        with self.app.test_request_context("/?experiment_id=123", method="GET"):
            self.assertEqual(get_experiment_id(), "123")
        # POST method, experiment_id present
        with self.app.test_request_context("/", method="POST", json={"experiment_id": "456"}, content_type="application/json"):
            self.assertEqual(get_experiment_id(), "456")
        # experiment_name present
        with self.app.test_request_context("/?experiment_name=exp", method="GET"):
            mock_tracking_store().get_experiment_by_name.return_value.experiment_id = "789"
            self.assertEqual(get_experiment_id(), "789")
        # missing both - mock request.json to avoid content type issues
        with self.app.test_request_context("/", method="GET"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = None
                mock_request.args = {}
                mock_request.json = None
                with self.assertRaises(MlflowException) as cm:
                    get_experiment_id()
                self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")
        # unsupported method
        with self.app.test_request_context("/", method="PUT"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = None
                mock_request.args = {}
                mock_request.json = None
                with self.assertRaises(MlflowException) as cm:
                    get_experiment_id()
                self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.validate_token")
    def test_get_username(self, mock_validate_token, mock_store):
        with self.app.test_request_context():
            # session username
            with patch("mlflow_oidc_auth.utils.session", {"username": "session_user"}):
                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = None
                    self.assertEqual(get_username(), "session_user")
            # basic auth username
            with patch("mlflow_oidc_auth.utils.session", {}):

                class AuthBasic:
                    type = "basic"
                    username = "basic_user"

                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = AuthBasic()
                    self.assertEqual(get_username(), "basic_user")

                # missing username in basic auth
                class AuthBasicNone:
                    type = "basic"
                    username = None

                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = AuthBasicNone()
                    with self.assertRaises(MlflowException):
                        get_username()
            # bearer token
            with patch("mlflow_oidc_auth.utils.session", {}):

                class AuthBearer:
                    type = "bearer"
                    token = "tok"

                mock_validate_token.return_value = {"email": "bearer_user"}
                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = AuthBearer()
                    self.assertEqual(get_username(), "bearer_user")
            # no auth
            with patch("mlflow_oidc_auth.utils.session", {}):
                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = None
                    with self.assertRaises(MlflowException):
                        get_username()

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_id_experiment_name_not_found(self, mock_tracking_store):
        # experiment_name provided but not found
        with self.app.test_request_context("/?experiment_name=nonexistent_exp", method="GET"):
            mock_tracking_store().get_experiment_by_name.return_value = None
            with self.assertRaises(MlflowException) as cm:
                get_experiment_id()
            self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_effective_experiment_permission(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True), "user"
            )
            result = effective_experiment_permission("exp_id", "user")
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "user")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_effective_registered_model_permission(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True), "user"
            )
            result = effective_registered_model_permission("model_name", "user")
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "user")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_effective_prompt_permission(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=True, can_delete=True, can_manage=True), "user"
            )
            result = effective_prompt_permission("prompt_name", "user")
            self.assertTrue(result.permission.can_manage)
            self.assertEqual(result.type, "user")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_can_read_experiment(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=False, can_delete=False, can_manage=False), "user"
            )
            self.assertTrue(can_read_experiment("exp_id", "user"))

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_permission_from_store_or_default")
    def test_can_read_registered_model(self, mock_get_permission_from_store_or_default, mock_store):
        with self.app.test_request_context():
            mock_get_permission_from_store_or_default.return_value = PermissionResult(
                Permission(name="perm", priority=1, can_read=True, can_update=False, can_delete=False, can_manage=False), "user"
            )
            self.assertTrue(can_read_registered_model("model_name", "user"))

    def test_get_url_param(self):
        # URL param present
        with self.app.test_request_context("/test/123"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"id": "123"}
                self.assertEqual(get_url_param("id"), "123")

        # URL param missing
        with self.app.test_request_context("/test"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {}
                with self.assertRaises(MlflowException) as cm:
                    get_url_param("id")
                self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")

    def test_get_optional_url_param(self):
        # URL param present
        with self.app.test_request_context("/test/123"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"id": "123"}
                self.assertEqual(get_optional_url_param("id"), "123")

        # URL param missing
        with self.app.test_request_context("/test"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {}
                self.assertIsNone(get_optional_url_param("id"))

    def test_get_model_name(self):
        # URL args
        with self.app.test_request_context("/model/test-model"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"name": "test-model"}
                mock_request.args = {}
                mock_request.json = None
                self.assertEqual(get_model_name(), "test-model")

        # Query args
        with self.app.test_request_context("/?name=test-model", method="GET"):
            self.assertEqual(get_model_name(), "test-model")

        # JSON data
        with self.app.test_request_context("/", method="POST", json={"name": "test-model"}, content_type="application/json"):
            self.assertEqual(get_model_name(), "test-model")

        # Missing name
        with self.app.test_request_context("/", method="GET"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = None
                mock_request.args = {}
                mock_request.json = None
                with self.assertRaises(MlflowException) as cm:
                    get_model_name()
                self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_experiment_id_from_name(self, mock_tracking_store):
        # Experiment found
        mock_tracking_store().get_experiment_by_name.return_value.experiment_id = "123"
        result = _experiment_id_from_name("test-experiment")
        self.assertEqual(result, "123")

        # Experiment not found
        mock_tracking_store().get_experiment_by_name.return_value = None
        with self.assertRaises(MlflowException) as cm:
            _experiment_id_from_name("nonexistent-experiment")
        self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.get_is_admin")
    @patch("mlflow_oidc_auth.utils.get_username")
    @patch("mlflow_oidc_auth.utils.make_forbidden_response")
    def test_check_admin_permission(self, mock_make_forbidden_response, mock_get_username, mock_get_is_admin, mock_store):
        with self.app.test_request_context():
            mock_get_username.return_value = "user"
            mock_get_is_admin.return_value = False
            mock_make_forbidden_response.return_value = "forbidden"

            @check_admin_permission
            def mock_func():
                return "success"

            self.assertEqual(mock_func(), "forbidden")

            # Admin allowed
            mock_get_is_admin.return_value = True
            self.assertEqual(mock_func(), "success")

    @patch("mlflow_oidc_auth.utils._get_model_registry_store")
    def test_fetch_all_registered_models(self, mock_model_store):
        # Single page
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([MagicMock(name="model1"), MagicMock(name="model2")]))
        mock_result.__len__ = MagicMock(return_value=2)
        mock_result.token = None
        mock_model_store().search_registered_models.return_value = mock_result

        result = fetch_all_registered_models()
        self.assertEqual(len(result), 2)

        # Multiple pages
        first_page = MagicMock()
        first_page.__iter__ = MagicMock(return_value=iter([MagicMock(name="model1")]))
        first_page.__len__ = MagicMock(return_value=1)
        first_page.token = "token123"

        second_page = MagicMock()
        second_page.__iter__ = MagicMock(return_value=iter([MagicMock(name="model2")]))
        second_page.__len__ = MagicMock(return_value=1)
        second_page.token = None

        mock_model_store().search_registered_models.side_effect = [first_page, second_page]

        result = fetch_all_registered_models()
        self.assertEqual(len(result), 2)

    @patch("mlflow_oidc_auth.utils.fetch_all_registered_models")
    def test_fetch_all_prompts(self, mock_fetch_models):
        mock_models = [MagicMock(name="prompt1"), MagicMock(name="prompt2")]
        mock_fetch_models.return_value = mock_models

        result = fetch_all_prompts()
        self.assertEqual(result, mock_models)
        mock_fetch_models.assert_called_once_with(filter_string="tags.`mlflow.prompt.is_prompt` = 'true'", max_results_per_page=1000)

    @patch("mlflow_oidc_auth.utils._get_model_registry_store")
    def test_fetch_registered_models_paginated(self, mock_model_store):
        mock_result = MagicMock()
        mock_model_store().search_registered_models.return_value = mock_result

        result = fetch_registered_models_paginated(filter_string="test_filter", max_results=100, order_by=["name"], page_token="token123")

        self.assertEqual(result, mock_result)
        mock_model_store().search_registered_models.assert_called_once_with(
            filter_string="test_filter", max_results=100, order_by=["name"], page_token="token123"
        )

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_fetch_all_experiments(self, mock_tracking_store):
        # Single page
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([MagicMock(name="exp1"), MagicMock(name="exp2")]))
        mock_result.__len__ = MagicMock(return_value=2)
        mock_result.token = None
        mock_tracking_store().search_experiments.return_value = mock_result

        result = fetch_all_experiments()
        self.assertEqual(len(result), 2)

        # Multiple pages
        first_page = MagicMock()
        first_page.__iter__ = MagicMock(return_value=iter([MagicMock(name="exp1")]))
        first_page.__len__ = MagicMock(return_value=1)
        first_page.token = "token123"

        second_page = MagicMock()
        second_page.__iter__ = MagicMock(return_value=iter([MagicMock(name="exp2")]))
        second_page.__len__ = MagicMock(return_value=1)
        second_page.token = None

        mock_tracking_store().search_experiments.side_effect = [first_page, second_page]

        result = fetch_all_experiments()
        self.assertEqual(len(result), 2)

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_fetch_experiments_paginated(self, mock_tracking_store):
        mock_result = MagicMock()
        mock_tracking_store().search_experiments.return_value = mock_result

        result = fetch_experiments_paginated(view_type=1, max_results=100, order_by=["name"], filter_string="test_filter", page_token="token123")

        self.assertEqual(result, mock_result)
        mock_tracking_store().search_experiments.assert_called_once_with(
            view_type=1, max_results=100, order_by=["name"], filter_string="test_filter", page_token="token123"
        )

    @patch("mlflow_oidc_auth.utils.fetch_all_experiments")
    @patch("mlflow_oidc_auth.utils.can_read_experiment")
    @patch("mlflow_oidc_auth.utils.get_username")
    def test_fetch_readable_experiments(self, mock_get_username, mock_can_read, mock_fetch_all):
        mock_get_username.return_value = "user"
        mock_exp1 = MagicMock()
        mock_exp1.experiment_id = "1"
        mock_exp2 = MagicMock()
        mock_exp2.experiment_id = "2"
        mock_fetch_all.return_value = [mock_exp1, mock_exp2]
        mock_can_read.side_effect = lambda exp_id, user: exp_id == "1"

        result = fetch_readable_experiments()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_exp1)

    @patch("mlflow_oidc_auth.utils.fetch_all_registered_models")
    @patch("mlflow_oidc_auth.utils.can_read_registered_model")
    @patch("mlflow_oidc_auth.utils.get_username")
    def test_fetch_readable_registered_models(self, mock_get_username, mock_can_read, mock_fetch_all):
        mock_get_username.return_value = "user"
        mock_model1 = MagicMock()
        mock_model1.name = "model1"
        mock_model2 = MagicMock()
        mock_model2.name = "model2"
        mock_fetch_all.return_value = [mock_model1, mock_model2]
        mock_can_read.side_effect = lambda name, user: name == "model1"

        result = fetch_readable_registered_models()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_model1)

    @patch("mlflow_oidc_auth.utils.store")
    def test_get_registered_model_permission_from_regex(self, mock_store):
        from mlflow_oidc_auth.entities import RegisteredModelRegexPermission

        regex_perms = [
            RegisteredModelRegexPermission(regex="test.*", permission="READ", priority=1, user_id=1),
            RegisteredModelRegexPermission(regex="prod.*", permission="MANAGE", priority=2, user_id=1),
        ]

        # Match found
        result = _get_registered_model_permission_from_regex(regex_perms, "test-model")
        self.assertEqual(result, "READ")

        # No match
        with self.assertRaises(MlflowException) as cm:
            _get_registered_model_permission_from_regex(regex_perms, "other-model")
        self.assertEqual(cm.exception.error_code, "RESOURCE_DOES_NOT_EXIST")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_permission_from_regex(self, mock_tracking_store, mock_store):
        from mlflow_oidc_auth.entities import ExperimentRegexPermission

        mock_tracking_store().get_experiment.return_value.name = "test-experiment"

        regex_perms = [
            ExperimentRegexPermission(regex="test.*", permission="READ", priority=1, user_id=1),
            ExperimentRegexPermission(regex="prod.*", permission="MANAGE", priority=2, user_id=1),
        ]

        # Match found
        result = _get_experiment_permission_from_regex(regex_perms, "exp123")
        self.assertEqual(result, "READ")

        # No match
        mock_tracking_store().get_experiment.return_value.name = "other-experiment"
        with self.assertRaises(MlflowException) as cm:
            _get_experiment_permission_from_regex(regex_perms, "exp123")
        self.assertEqual(cm.exception.error_code, "RESOURCE_DOES_NOT_EXIST")

    @patch("mlflow_oidc_auth.utils.store")
    def test_get_registered_model_group_permission_from_regex(self, mock_store):
        from mlflow_oidc_auth.entities import RegisteredModelGroupRegexPermission

        regex_perms = [
            RegisteredModelGroupRegexPermission(id_=1, regex="test.*", permission="READ", priority=1, group_id=1),
            RegisteredModelGroupRegexPermission(id_=2, regex="prod.*", permission="MANAGE", priority=2, group_id=1),
        ]

        # Match found
        result = _get_registered_model_group_permission_from_regex(regex_perms, "test-model")
        self.assertEqual(result, "READ")

        # No match
        with self.assertRaises(MlflowException) as cm:
            _get_registered_model_group_permission_from_regex(regex_perms, "other-model")
        self.assertEqual(cm.exception.error_code, "RESOURCE_DOES_NOT_EXIST")

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_group_permission_from_regex(self, mock_tracking_store, mock_store):
        from mlflow_oidc_auth.entities import ExperimentGroupRegexPermission

        mock_tracking_store().get_experiment.return_value.name = "test-experiment"

        regex_perms = [
            ExperimentGroupRegexPermission(id_=1, regex="test.*", permission="READ", priority=1, group_id=1),
            ExperimentGroupRegexPermission(id_=2, regex="prod.*", permission="MANAGE", priority=2, group_id=1),
        ]

        # Match found
        result = _get_experiment_group_permission_from_regex(regex_perms, "exp123")
        self.assertEqual(result, "READ")

        # No match
        mock_tracking_store().get_experiment.return_value.name = "other-experiment"
        with self.assertRaises(MlflowException) as cm:
            _get_experiment_group_permission_from_regex(regex_perms, "exp123")
        self.assertEqual(cm.exception.error_code, "RESOURCE_DOES_NOT_EXIST")

    @patch("mlflow_oidc_auth.utils.store")
    def test_permission_sources_config(self, mock_store):
        # Test prompt sources config
        config = _permission_prompt_sources_config("model1", "user1")
        self.assertIn("user", config)
        self.assertIn("group", config)
        self.assertIn("regex", config)
        self.assertIn("group-regex", config)

        # Test experiment sources config
        config = _permission_experiment_sources_config("exp1", "user1")
        self.assertIn("user", config)
        self.assertIn("group", config)
        self.assertIn("regex", config)
        self.assertIn("group-regex", config)

        # Test registered model sources config
        config = _permission_registered_model_sources_config("model1", "user1")
        self.assertIn("user", config)
        self.assertIn("group", config)
        self.assertIn("regex", config)
        self.assertIn("group-regex", config)

    def test_get_request_param_run_id_fallback(self):
        # Test run_id fallback to run_uuid
        with self.app.test_request_context("/?run_uuid=test-uuid", method="GET"):
            result = get_request_param("run_id")
            self.assertEqual(result, "test-uuid")

    def test_get_request_param_post_json(self):
        # Test POST with JSON data
        with self.app.test_request_context("/", method="POST", json={"param": "value"}, content_type="application/json"):
            result = get_request_param("param")
            self.assertEqual(result, "value")

    def test_get_optional_request_param_post_json(self):
        # Test POST with JSON data
        with self.app.test_request_context("/", method="POST", json={"param": "value"}, content_type="application/json"):
            result = get_optional_request_param("param")
            self.assertEqual(result, "value")

    def test_get_experiment_id_view_args(self):
        # Test experiment_id from view_args
        with self.app.test_request_context("/test/123"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"experiment_id": "123"}
                mock_request.args = {}
                mock_request.json = None
                result = get_experiment_id()
                self.assertEqual(result, "123")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_id_view_args_name(self, mock_tracking_store):
        # Test experiment_name from view_args
        mock_tracking_store().get_experiment_by_name.return_value.experiment_id = "456"
        with self.app.test_request_context("/test/exp-name"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"experiment_name": "exp-name"}
                mock_request.args = {}
                mock_request.json = None
                result = get_experiment_id()
                self.assertEqual(result, "456")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    def test_get_experiment_id_json_name(self, mock_tracking_store):
        # Test experiment_name from JSON
        mock_tracking_store().get_experiment_by_name.return_value.experiment_id = "789"
        with self.app.test_request_context("/", method="POST", json={"experiment_name": "exp-name"}, content_type="application/json"):
            result = get_experiment_id()
            self.assertEqual(result, "789")

    def test_get_username_bearer_missing_email(self):
        # Test bearer token without email
        with self.app.test_request_context():
            with patch("mlflow_oidc_auth.utils.session", {}):

                class AuthBearer:
                    type = "bearer"
                    token = "tok"

                with patch("mlflow_oidc_auth.utils.validate_token") as mock_validate:
                    mock_validate.return_value = {}  # No email field
                    with patch("mlflow_oidc_auth.utils.request") as mock_request:
                        mock_request.authorization = AuthBearer()
                        # The function returns None when email is missing, it doesn't raise an exception
                        result = get_username()
                        self.assertIsNone(result)

    def test_get_username_unknown_auth_type(self):
        # Test unknown auth type
        with self.app.test_request_context():
            with patch("mlflow_oidc_auth.utils.session", {}):

                class AuthUnknown:
                    type = "unknown"

                with patch("mlflow_oidc_auth.utils.request") as mock_request:
                    mock_request.authorization = AuthUnknown()
                    with self.assertRaises(MlflowException):
                        get_username()

    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    def test_get_permission_from_store_or_default_non_resource_exception(self, mock_get_permission, mock_config, mock_store):
        with self.app.test_request_context():
            mock_store_permission_user_func = MagicMock()
            mock_store_permission_user_func.side_effect = MlflowException("Other error", BAD_REQUEST)

            mock_config.PERMISSION_SOURCE_ORDER = ["user"]

            with self.assertRaises(MlflowException) as cm:
                get_permission_from_store_or_default({"user": mock_store_permission_user_func})
            self.assertEqual(cm.exception.error_code, "BAD_REQUEST")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    @patch("mlflow_oidc_auth.utils.get_username")
    def test_fetch_readable_logged_models_default_username(self, mock_get_username, mock_get_permission, mock_config, mock_store, mock_tracking_store):
        """Test fetch_readable_logged_models with default username"""
        with self.app.test_request_context():
            # Setup mocks
            mock_get_username.return_value = "test_user"
            mock_config.DEFAULT_MLFLOW_PERMISSION = "READ"

            # Mock permission
            mock_permission = MagicMock()
            mock_permission.can_read = True
            mock_get_permission.return_value = mock_permission

            # Mock store permissions
            mock_perms = [MagicMock(experiment_id="exp1", permission="READ")]
            mock_store.list_experiment_permissions.return_value = mock_perms

            # Mock tracking store search
            mock_logged_model = MagicMock()
            mock_logged_model.experiment_id = "exp1"

            mock_search_result = MagicMock()
            mock_search_result.__iter__ = lambda self: iter([mock_logged_model])
            mock_search_result.token = None
            mock_tracking_store.return_value.search_logged_models.return_value = mock_search_result

            # Call function
            result = fetch_readable_logged_models()

            # Verify
            mock_get_username.assert_called_once()
            mock_store.list_experiment_permissions.assert_called_once_with("test_user")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].experiment_id, "exp1")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    def test_fetch_readable_logged_models_with_username(self, mock_get_permission, mock_config, mock_store, mock_tracking_store):
        """Test fetch_readable_logged_models with explicit username"""
        with self.app.test_request_context():
            # Setup mocks
            mock_config.DEFAULT_MLFLOW_PERMISSION = "READ"

            # Mock permission
            mock_permission = MagicMock()
            mock_permission.can_read = True
            mock_get_permission.return_value = mock_permission

            # Mock store permissions
            mock_perms = [MagicMock(experiment_id="exp1", permission="READ")]
            mock_store.list_experiment_permissions.return_value = mock_perms

            # Mock tracking store search with pagination
            mock_logged_model1 = MagicMock()
            mock_logged_model1.experiment_id = "exp1"
            mock_logged_model2 = MagicMock()
            mock_logged_model2.experiment_id = "exp2"

            # First page
            mock_search_result1 = MagicMock()
            mock_search_result1.__iter__ = lambda self: iter([mock_logged_model1])
            mock_search_result1.token = "token123"

            # Second page
            mock_search_result2 = MagicMock()
            mock_search_result2.__iter__ = lambda self: iter([mock_logged_model2])
            mock_search_result2.token = None

            mock_tracking_store.return_value.search_logged_models.side_effect = [mock_search_result1, mock_search_result2]

            # Call function
            result = fetch_readable_logged_models(
                experiment_ids=["exp1", "exp2"], filter_string="filter", order_by=[{"field_name": "name"}], username="custom_user"
            )

            # Verify
            mock_store.list_experiment_permissions.assert_called_once_with("custom_user")
            self.assertEqual(len(result), 2)  # Both models should be readable
            self.assertEqual(mock_tracking_store.return_value.search_logged_models.call_count, 2)

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    def test_fetch_readable_logged_models_filtered_by_permissions(self, mock_get_permission, mock_config, mock_store, mock_tracking_store):
        """Test fetch_readable_logged_models filters models based on permissions"""
        with self.app.test_request_context():
            # Setup mocks
            mock_config.DEFAULT_MLFLOW_PERMISSION = "NONE"

            # Mock permissions - can read only returns True for READ permission
            def mock_permission_side_effect(perm):
                mock_perm = MagicMock()
                mock_perm.can_read = perm == "READ"
                return mock_perm

            mock_get_permission.side_effect = mock_permission_side_effect

            # Mock store permissions - user has READ on exp1, NONE on exp2
            mock_perms = [MagicMock(experiment_id="exp1", permission="READ")]
            mock_store.list_experiment_permissions.return_value = mock_perms

            # Mock tracking store search
            mock_logged_model1 = MagicMock()
            mock_logged_model1.experiment_id = "exp1"  # Should be readable
            mock_logged_model2 = MagicMock()
            mock_logged_model2.experiment_id = "exp2"  # Should NOT be readable (default NONE)

            mock_search_result = MagicMock()
            mock_search_result.__iter__ = lambda self: iter([mock_logged_model1, mock_logged_model2])
            mock_search_result.token = None
            mock_tracking_store.return_value.search_logged_models.return_value = mock_search_result

            # Call function
            result = fetch_readable_logged_models(username="test_user")

            # Verify - only model1 should be in result
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].experiment_id, "exp1")

    @patch("mlflow_oidc_auth.utils._get_tracking_store")
    @patch("mlflow_oidc_auth.utils.store")
    @patch("mlflow_oidc_auth.utils.config")
    @patch("mlflow_oidc_auth.utils.get_permission")
    def test_fetch_readable_logged_models_empty_result(self, mock_get_permission, mock_config, mock_store, mock_tracking_store):
        """Test fetch_readable_logged_models with empty search result"""
        with self.app.test_request_context():
            # Setup mocks
            mock_config.DEFAULT_MLFLOW_PERMISSION = "READ"

            # Mock permission
            mock_permission = MagicMock()
            mock_permission.can_read = True
            mock_get_permission.return_value = mock_permission

            # Mock store permissions
            mock_store.list_experiment_permissions.return_value = []

            # Mock tracking store search - empty result
            mock_search_result = MagicMock()
            mock_search_result.__iter__ = lambda self: iter([])
            mock_search_result.token = None
            mock_tracking_store.return_value.search_logged_models.return_value = mock_search_result

            # Call function
            result = fetch_readable_logged_models(username="test_user")

            # Verify
            self.assertEqual(len(result), 0)

    def test_get_model_id(self):
        from mlflow_oidc_auth.utils import get_model_id

        # URL args (view_args)
        with self.app.test_request_context("/model/123"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {"model_id": "123"}
                mock_request.args = {}
                mock_request.json = None
                self.assertEqual(get_model_id(), "123")

        # Query args
        with self.app.test_request_context("/?model_id=456", method="GET"):
            self.assertEqual(get_model_id(), "456")

        # JSON data
        with self.app.test_request_context("/", method="POST", json={"model_id": "789"}, content_type="application/json"):
            self.assertEqual(get_model_id(), "789")

        # Missing model_id
        with self.app.test_request_context("/", method="GET"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = None
                mock_request.args = {}
                mock_request.json = None
                with self.assertRaises(MlflowException) as cm:
                    get_model_id()
                self.assertEqual(cm.exception.error_code, "INVALID_PARAMETER_VALUE")
                self.assertIn("Model ID must be provided", str(cm.exception))

        # Empty view_args, but model_id in args
        with self.app.test_request_context("/?model_id=args_id", method="GET"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {}
                mock_request.args = {"model_id": "args_id"}
                mock_request.json = None
                self.assertEqual(get_model_id(), "args_id")

        # Empty view_args and args, but model_id in json
        with self.app.test_request_context("/", method="POST", json={"model_id": "json_id"}, content_type="application/json"):
            with patch("mlflow_oidc_auth.utils.request") as mock_request:
                mock_request.view_args = {}
                mock_request.args = {}
                mock_request.json = {"model_id": "json_id"}
                self.assertEqual(get_model_id(), "json_id")


if __name__ == "__main__":
    unittest.main()
