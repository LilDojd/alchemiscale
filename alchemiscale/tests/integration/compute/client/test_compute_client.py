import pytest
from time import sleep

from gufe.tokenization import GufeTokenizable

from alchemiscale.models import ScopedKey
from alchemiscale.compute import client
from alchemiscale.storage.models import TaskStatusEnum

from alchemiscale.tests.integration.compute.utils import get_compute_settings_override


class TestComputeClient:
    def test_wrong_credential(
        self,
        scope_test,
        n4js_preloaded,
        compute_client_wrong_credential: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        with pytest.raises(client.AlchemiscaleComputeClientError):
            compute_client_wrong_credential.get_info()

    def test_refresh_credential(
        self,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        settings = get_compute_settings_override()
        assert compute_client._jwtoken == None
        compute_client._get_token()

        token = compute_client._jwtoken
        assert token is not None

        # token shouldn't change this fast
        compute_client.get_info()
        assert token == compute_client._jwtoken

        # should change if we wait a bit
        sleep(settings.JWT_EXPIRE_SECONDS + 2)
        compute_client.get_info()
        assert token != compute_client._jwtoken

    def test_api_check(
        self,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        compute_client._api_check()

    def test_list_scope(
        self,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
        scope_test,
    ):
        scopes = compute_client.list_scopes()
        # scope_test matches identity used to initialise the client in conftest
        assert scopes == [scope_test]

    ### compute

    def test_query_taskhubs(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        taskhub_sks = compute_client.query_taskhubs([scope_test])

        assert len(taskhub_sks) == 2

        taskhubs = compute_client.query_taskhubs([scope_test], return_gufe=True)
        assert all([tq.weight == 0.5 for tq in taskhubs.values()])

    def test_claim_taskhub_task(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        taskhub_sks = compute_client.query_taskhubs([scope_test])

        # claim a single task; should get highest priority task
        task_sks = compute_client.claim_taskhub_tasks(taskhub_sks[0], compute_service_id="me-123")
        all_tasks = n4js_preloaded.get_taskhub_tasks(taskhub_sks[0], return_gufe=True)

        assert len(task_sks) == 1
        assert task_sks[0] in all_tasks.keys()
        assert [t.gufe_key for t in task_sks] == [
            task.key for task in all_tasks.values() if task.priority == 1
        ]

        remaining_tasks = n4js_preloaded.get_taskhub_unclaimed_tasks(taskhub_sks[0])
        # claim two more tasks
        task_sks2 = compute_client.claim_taskhub_tasks(
            taskhub_sks[0], count=2, compute_service_id="me-123"
        )
        assert task_sks2[0] in remaining_tasks
        assert task_sks2[1] in remaining_tasks

    def test_get_task_transformation(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        network_tyk2,
        transformation,
        uvicorn_server,
    ):
        an_sk = ScopedKey(gufe_key=network_tyk2.key, **scope_test.dict())

        taskhub_sk = n4js_preloaded.get_taskhub(an_sk)

        # claim our first task
        task_sks = compute_client.claim_taskhub_tasks(taskhub_sk, compute_service_id="me-123")

        # get the transformation corresponding to this task
        (
            transformation_,
            extends_protocoldagresult,
        ) = compute_client.get_task_transformation(task_sks[0])

        assert transformation_ == transformation
        assert extends_protocoldagresult is None

    @pytest.mark.parametrize("status", [member for member in TaskStatusEnum])
    def test_set_task_status(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
        status,
    ):
        taskhub_sks = compute_client.query_taskhubs([scope_test])

        all_tasks = n4js_preloaded.get_taskhub_tasks(taskhub_sks[0], return_gufe=False)

        # special case for "complete" and "error" statuses as they cannot be
        # reached from "waiting" so we set to running first
        if status in [TaskStatusEnum.complete, TaskStatusEnum.error]:
            compute_client.set_task_status(all_tasks[0], TaskStatusEnum.running)

        # set the status of a task
        compute_client.set_task_status(all_tasks[0], status)

        # check that the status has been set
        # note must be list on n4js side
        statuses = n4js_preloaded.get_task_status([all_tasks[0]])
        assert statuses[0] == status

    @pytest.mark.parametrize("status", [member for member in TaskStatusEnum])
    def test_get_task_status(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
        status,
    ):
        taskhub_sks = compute_client.query_taskhubs([scope_test])

        all_tasks = n4js_preloaded.get_taskhub_tasks(taskhub_sks[0], return_gufe=False)

        # special case for "complete" and "error" statuses as they cannot be
        # reached from "waiting" so we set to running first
        if status in [TaskStatusEnum.complete, TaskStatusEnum.error]:
            compute_client.set_task_status(all_tasks[0], TaskStatusEnum.running)

        # set the status of a task
        compute_client.set_task_status(all_tasks[0], status)

        # check that the status has been set
        assert compute_client.get_task_status(all_tasks[0]) == status

    def test_set_task_complete(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        uvicorn_server,
    ):
        taskhub_sks = compute_client.query_taskhubs([scope_test])
        all_tasks = n4js_preloaded.get_taskhub_tasks(taskhub_sks[0], return_gufe=False)

        compute_client.set_task_status(all_tasks[0], TaskStatusEnum.running)

        # complete the task
        compute_client.set_task_status(all_tasks[0], TaskStatusEnum.complete)

        # check that the status has been set
        assert compute_client.get_task_status(all_tasks[0]) == TaskStatusEnum.complete

        # test if we change the status to something else it preserves it
        # IE see that the raise_error=False behaviour is upheld
        compute_client.set_task_status(all_tasks[1], TaskStatusEnum.invalid)

        compute_client.set_task_status(all_tasks[1], TaskStatusEnum.complete)

        assert compute_client.get_task_status(all_tasks[1]) == TaskStatusEnum.invalid

    ### results

    def test_set_task_result(
        self,
        scope_test,
        n4js_preloaded,
        compute_client: client.AlchemiscaleComputeClient,
        network_tyk2,
        transformation,
        protocoldagresults,
        uvicorn_server,
    ):
        an_sk = ScopedKey(gufe_key=network_tyk2.key, **scope_test.dict())
        tf_sk = ScopedKey(gufe_key=transformation.key, **scope_test.dict())
        taskhub_sk = n4js_preloaded.get_taskhub(an_sk)

        # claim our first task
        task_sks = compute_client.claim_taskhub_tasks(taskhub_sk, compute_service_id="me-123")

        # get the transformation corresponding to this task
        (
            transformation_,
            extends_protocoldagresult,
        ) = compute_client.get_task_transformation(task_sks[0])

        assert transformation_ == transformation
        assert extends_protocoldagresult is None

        # push a result for the task
        pdr_sk = compute_client.set_task_result(task_sks[0], protocoldagresults[0])

        # now, create a task that extends the one we just "performed"
        task_sk2 = n4js_preloaded.create_task(tf_sk, extends=task_sks[0])

        # get the transformation and the protocoldagresult for the task this extends
        # no need to claim to actually do this
        (
            transformation2,
            extends_protocoldagresult2,
        ) = compute_client.get_task_transformation(task_sk2)

        assert transformation2 == transformation_
        assert extends_protocoldagresult2 == protocoldagresults[0]