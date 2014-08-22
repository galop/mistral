# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# TODO(rakhmerov): Add checks for timestamps.

import copy

from mistral import context as auth_context
from mistral.db.v2.sqlalchemy import api as db_api
from mistral import exceptions as exc
from mistral.tests import base as test_base


WORKBOOKS = [
    {
        'id': '1',
        'name': 'my_workbook1',
        'definition': 'empty',
        'spec': {},
        'tags': ['mc'],
        'scope': 'public',
        'updated_at': None,
        'project_id': '1233',
        'trust_id': '1234'
    },
    {
        'id': '2',
        'name': 'my_workbook2',
        'description': 'my description',
        'definition': 'empty',
        'spec': {},
        'tags': ['mc'],
        'scope': 'private',
        'updated_at': None,
        'project_id': '1233',
        'trust_id': '12345'
    },
]


class WorkbookTest(test_base.DbTestCase):
    def test_create_and_get_and_load_workbook(self):
        created = db_api.create_workbook(WORKBOOKS[0])

        fetched = db_api.get_workbook(created['name'])

        self.assertEqual(created, fetched)

        fetched = db_api.load_workbook(created.name)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_workbook("not-existing-wb"))

    def test_update_workbook(self):
        created = db_api.create_workbook(WORKBOOKS[0])

        updated = db_api.update_workbook(
            created.name,
            {'definition': 'my new definition'}
        )

        self.assertEqual('my new definition', updated.definition)

        fetched = db_api.get_workbook(created['name'])

        self.assertEqual(updated, fetched)

    def test_create_or_update_workbook(self):
        name = WORKBOOKS[0]['name']

        self.assertIsNone(db_api.load_workbook(name))

        created = db_api.create_or_update_workbook(name, WORKBOOKS[0])

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.name)

        updated = db_api.create_or_update_workbook(
            created.name,
            {'definition': 'my new definition'}
        )

        self.assertEqual('my new definition', updated.definition)
        self.assertEqual(
            'my new definition',
            db_api.load_workbook(updated.name).definition
        )

        fetched = db_api.get_workbook(created.name)

        self.assertEqual(updated, fetched)

    def test_get_workbooks(self):
        created0 = db_api.create_workbook(WORKBOOKS[0])
        created1 = db_api.create_workbook(WORKBOOKS[1])

        fetched = db_api.get_workbooks()

        self.assertEqual(2, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual(created1, fetched[1])

    def test_delete_workbook(self):
        created = db_api.create_workbook(WORKBOOKS[0])

        fetched = db_api.get_workbook(created.name)

        self.assertEqual(created, fetched)

        db_api.delete_workbook(created.name)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_workbook,
            created.name
        )

    def test_workbook_private(self):
        # Create a workbook(scope=private) as under one project
        # then make sure it's NOT visible for other projects.
        created1 = db_api.create_workbook(WORKBOOKS[1])

        fetched = db_api.get_workbooks()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created1, fetched[0])

        # Create a new user.
        ctx = auth_context.MistralContext(
            user_id='9-0-44-5',
            project_id='99-88-33',
            user_name='test-user',
            project_name='test-another',
            is_admin=False
        )

        auth_context.set_ctx(ctx)

        fetched = db_api.get_workbooks()

        self.assertEqual(0, len(fetched))

    def test_workbook_public(self):
        # Create a workbook(scope=public) as under one project
        # then make sure it's visible for other projects.
        created0 = db_api.create_workbook(WORKBOOKS[0])

        fetched = db_api.get_workbooks()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created0, fetched[0])

        # Assert that the project_id stored is actually the context's
        # project_id not the one given.
        self.assertEqual(created0.project_id, auth_context.ctx().project_id)
        self.assertNotEqual(WORKBOOKS[0]['project_id'],
                            auth_context.ctx().project_id)

        # Create a new user.
        ctx = auth_context.MistralContext(
            user_id='9-0-44-5',
            project_id='99-88-33',
            user_name='test-user',
            project_name='test-another',
            is_admin=False
        )

        auth_context.set_ctx(ctx)

        fetched = db_api.get_workbooks()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual('public', created0.scope)

    def test_workbook_repr(self):
        s = db_api.create_workbook(WORKBOOKS[0]).__repr__()

        self.assertIn('Workbook ', s)
        self.assertIn("'name': 'my_workbook1'", s)

WORKFLOWS = [
    {
        'id': '1',
        'name': 'my_wf1',
        'definition': 'empty',
        'spec': {},
        'tags': ['mc'],
        'scope': 'public',
        'project_id': '1233',
        'trust_id': '1234'
    },
    {
        'id': '2',
        'name': 'my_wf2',
        'definition': 'empty',
        'spec': {},
        'tags': ['mc'],
        'scope': 'private',
        'project_id': '1233',
        'trust_id': '12345'
    },
]


class WorkflowTest(test_base.DbTestCase):
    def test_create_and_get_and_load_workflow(self):
        created = db_api.create_workflow(WORKFLOWS[0])

        fetched = db_api.get_workflow(created.name)

        self.assertEqual(created, fetched)

        fetched = db_api.load_workflow(created.name)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_workflow("not-existing-wf"))

    def test_update_workflow(self):
        created = db_api.create_workflow(WORKFLOWS[0])

        updated = db_api.update_workflow(
            created['name'],
            {'definition': 'my new definition'}
        )

        self.assertEqual('my new definition', updated.definition)

        fetched = db_api.get_workflow(created.name)

        self.assertEqual(updated, fetched)

    def test_create_or_update_workflow(self):
        name = WORKFLOWS[0]['name']

        self.assertIsNone(db_api.load_workflow(name))

        created = db_api.create_or_update_workflow(name, WORKFLOWS[0])

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.name)

        updated = db_api.create_or_update_workflow(
            created.name,
            {'definition': 'my new definition'}
        )

        self.assertEqual('my new definition', updated.definition)
        self.assertEqual(
            'my new definition',
            db_api.load_workflow(updated.name).definition
        )

        fetched = db_api.get_workflow(created.name)

        self.assertEqual(updated, fetched)

    def test_get_workflows(self):
        created0 = db_api.create_workflow(WORKFLOWS[0])
        created1 = db_api.create_workflow(WORKFLOWS[1])

        fetched = db_api.get_workflows()

        self.assertEqual(2, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual(created1, fetched[1])

    def test_delete_workflow(self):
        created = db_api.create_workflow(WORKFLOWS[0])

        fetched = db_api.get_workflow(created.name)

        self.assertEqual(created, fetched)

        db_api.delete_workflow(created.name)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_workflow,
            created.name
        )

    def test_workflow_private(self):
        # Create a workflow(scope=private) as under one project
        # then make sure it's NOT visible for other projects.
        created1 = db_api.create_workflow(WORKFLOWS[1])

        fetched = db_api.get_workflows()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created1, fetched[0])

        # Create a new user.
        ctx = auth_context.MistralContext(
            user_id='9-0-44-5',
            project_id='99-88-33',
            user_name='test-user',
            project_name='test-another',
            is_admin=False
        )

        auth_context.set_ctx(ctx)

        fetched = db_api.get_workflows()

        self.assertEqual(0, len(fetched))

    def test_workflow_public(self):
        # Create a workflow(scope=public) as under one project
        # then make sure it's visible for other projects.
        created0 = db_api.create_workflow(WORKFLOWS[0])

        fetched = db_api.get_workflows()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created0, fetched[0])

        # Assert that the project_id stored is actually the context's
        # project_id not the one given.
        self.assertEqual(created0.project_id, auth_context.ctx().project_id)
        self.assertNotEqual(
            WORKFLOWS[0]['project_id'],
            auth_context.ctx().project_id
        )

        # Create a new user.
        ctx = auth_context.MistralContext(
            user_id='9-0-44-5',
            project_id='99-88-33',
            user_name='test-user',
            project_name='test-another',
            is_admin=False
        )

        auth_context.set_ctx(ctx)

        fetched = db_api.get_workflows()

        self.assertEqual(1, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual('public', created0.scope)

    def test_workflow_repr(self):
        s = db_api.create_workflow(WORKFLOWS[0]).__repr__()

        self.assertIn('Workflow ', s)
        self.assertIn("'name': 'my_wf1'", s)


EXECUTIONS = [
    {
        'id': '1',
        'wf_spec': {},
        'start_params': {'task': 'my_task1'},
        'state': 'IDLE',
        'created_at': None,
        'updated_at': None,
        'context': None
    },
    {
        'id': '2',
        'wf_spec': {},
        'start_params': {'task': 'my_task1'},
        'state': 'RUNNING',
        'created_at': None,
        'updated_at': None,
        'context': {'image_id': '123123'}
    }
]


class ExecutionTest(test_base.DbTestCase):
    def test_create_and_get_and_load_execution(self):
        created = db_api.create_execution(EXECUTIONS[0])

        fetched = db_api.get_execution(created.id)

        self.assertEqual(created, fetched)

        fetched = db_api.load_execution(created.id)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_execution("not-existing-id"))

    def test_update_execution(self):
        created = db_api.create_execution(EXECUTIONS[0])

        updated = db_api.update_execution(created.id, {'state': 'RUNNING'})

        self.assertEqual('RUNNING', updated.state)
        self.assertEqual(
            'RUNNING',
            db_api.load_execution(updated.id).state
        )

        fetched = db_api.get_execution(created.id)

        self.assertEqual(updated, fetched)

    def test_create_or_update_execution(self):
        id = 'not-existing-id'

        self.assertIsNone(db_api.load_execution(id))

        created = db_api.create_or_update_execution(id, EXECUTIONS[0])

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.id)

        updated = db_api.create_or_update_execution(
            created.id,
            {'state': 'RUNNING'}
        )

        self.assertEqual('RUNNING', updated.state)
        self.assertEqual(
            'RUNNING',
            db_api.load_execution(updated.id).state
        )

        fetched = db_api.get_execution(created.id)

        self.assertEqual(updated, fetched)

    def test_get_executions(self):
        created0 = db_api.create_execution(EXECUTIONS[0])
        db_api.create_execution(EXECUTIONS[1])

        fetched = db_api.get_executions(
            state=EXECUTIONS[0]['state']
        )

        self.assertEqual(1, len(fetched))
        self.assertEqual(created0, fetched[0])

    def test_delete_execution(self):
        created = db_api.create_execution(EXECUTIONS[0])

        fetched = db_api.get_execution(created.id)

        self.assertEqual(created, fetched)

        db_api.delete_execution(created.id)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_execution,
            created.id
        )

    def test_execution_repr(self):
        s = db_api.create_execution(EXECUTIONS[0]).__repr__()

        self.assertIn('Execution ', s)
        self.assertIn("'id': '1'", s)
        self.assertIn("'state': 'IDLE'", s)


TASKS = [
    {
        'id': '1',
        'execution_id': '1',
        'wf_name': 'my_wb.my_wf',
        'name': 'my_task1',
        'requires': ['my_task2', 'my_task3'],
        'spec': None,
        'action_spec': None,
        'state': 'IDLE',
        'tags': ['deployment'],
        'in_context': None,
        'parameters': None,
        'output': None,
        'runtime_context': None,
        'created_at': None,
        'updated_at': None
    },
    {
        'id': '2',
        'execution_id': '1',
        'wf_name': 'my_wb.my_wf',
        'name': 'my_task2',
        'requires': ['my_task4', 'my_task5'],
        'spec': None,
        'action_spec': None,
        'state': 'IDLE',
        'tags': ['deployment'],
        'in_context': {'image_id': '123123'},
        'parameters': {'image_id': '123123'},
        'output': {'vm_id': '343123'},
        'runtime_context': None,
        'created_at': None,
        'updated_at': None
    },
]


class TaskTest(test_base.DbTestCase):
    def test_create_and_get_and_load_task(self):
        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        created = db_api.create_task(values)

        fetched = db_api.get_task(created.id)

        self.assertEqual(created, fetched)

        fetched = db_api.load_task(created.id)

        self.assertEqual(created, fetched)

        self.assertIsNone(db_api.load_task("not-existing-id"))

    def test_update_task(self):
        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        created = db_api.create_task(values)

        updated = db_api.update_task(
            created.id,
            {'description': 'my new desc'}
        )

        self.assertEqual('my new desc', updated['description'])

        fetched = db_api.get_task(created.id)

        self.assertEqual(updated, fetched)

    def test_create_or_update_task(self):
        id = 'not-existing-id'

        self.assertIsNone(db_api.load_task(id))

        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        created = db_api.create_or_update_task(id, values)

        self.assertIsNotNone(created)
        self.assertIsNotNone(created.id)

        updated = db_api.create_or_update_task(
            created.id,
            {'state': 'RUNNING'}
        )

        self.assertEqual('RUNNING', updated.state)
        self.assertEqual(
            'RUNNING',
            db_api.load_task(updated.id).state
        )

        fetched = db_api.get_task(created.id)

        self.assertEqual(updated, fetched)

    def test_get_tasks(self):
        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        created0 = db_api.create_task(values)

        values = copy.copy(TASKS[1])
        values.update({'execution_id': ex.id})

        created1 = db_api.create_task(values)

        fetched = db_api.get_tasks(wf_name=TASKS[0]['wf_name'])

        self.assertEqual(2, len(fetched))
        self.assertEqual(created0, fetched[0])
        self.assertEqual(created1, fetched[1])

    def test_delete_task(self):
        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        created = db_api.create_task(values)

        fetched = db_api.get_task(created.id)

        self.assertEqual(created, fetched)

        db_api.delete_task(created.id)

        self.assertRaises(
            exc.NotFoundException,
            db_api.get_task,
            created['id']
        )

    def test_task_repr(self):
        ex = db_api.create_execution(EXECUTIONS[0])

        values = copy.copy(TASKS[0])
        values.update({'execution_id': ex.id})

        s = db_api.create_task(values).__repr__()

        self.assertIn('Task ', s)
        self.assertIn("'id': '1'", s)
        self.assertIn("'name': 'my_task1'", s)


class TXTest(test_base.DbTestCase):
    def test_rollback(self):
        db_api.start_tx()

        try:
            created = db_api.create_workbook(WORKBOOKS[0])
            fetched = db_api.get_workbook(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

            db_api.rollback_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_workbook,
            created['id']
        )
        self.assertFalse(self.is_db_session_open())

    def test_commit(self):
        db_api.start_tx()

        try:
            created = db_api.create_workbook(WORKBOOKS[0])
            fetched = db_api.get_workbook(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

            db_api.commit_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_workbook(created.name)

        self.assertEqual(created, fetched)
        self.assertFalse(self.is_db_session_open())

    def test_commit_transaction(self):
        with db_api.transaction():
            created = db_api.create_workbook(WORKBOOKS[0])
            fetched = db_api.get_workbook(created.name)

            self.assertEqual(created, fetched)
            self.assertTrue(self.is_db_session_open())

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_workbook(created.name)

        self.assertEqual(created, fetched)
        self.assertFalse(self.is_db_session_open())

    def test_rollback_multiple_objects(self):
        db_api.start_tx()

        try:
            created = db_api.create_execution(EXECUTIONS[0])
            fetched = db_api.get_execution(created['id'])

            self.assertEqual(created, fetched)

            created_workbook = db_api.create_workbook(WORKBOOKS[0])
            fetched_workbook = db_api.get_workbook(created_workbook.name)

            self.assertEqual(created_workbook, fetched_workbook)
            self.assertTrue(self.is_db_session_open())

            db_api.rollback_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_execution,
            created.id
        )
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_workbook,
            created_workbook.name
        )

        self.assertFalse(self.is_db_session_open())

    def test_rollback_transaction(self):
        try:
            with db_api.transaction():
                created = db_api.create_workbook(WORKBOOKS[0])
                fetched = db_api.get_workbook(
                    created['name']
                )

                self.assertEqual(created, fetched)
                self.assertTrue(self.is_db_session_open())

                db_api.create_workbook(WORKBOOKS[0])

        except exc.DBException:
            pass

        self.assertFalse(self.is_db_session_open())
        self.assertRaises(
            exc.NotFoundException,
            db_api.get_workbook,
            created['name']
        )

    def test_commit_multiple_objects(self):
        db_api.start_tx()

        try:
            created = db_api.create_execution(EXECUTIONS[0])
            fetched = db_api.get_execution(created.id)

            self.assertEqual(created, fetched)

            created_workbook = db_api.create_workbook(WORKBOOKS[0])
            fetched_workbook = db_api.get_workbook(created_workbook.name)

            self.assertEqual(created_workbook, fetched_workbook)
            self.assertTrue(self.is_db_session_open())

            db_api.commit_tx()
        finally:
            db_api.end_tx()

        self.assertFalse(self.is_db_session_open())

        fetched = db_api.get_execution(created.id)

        self.assertEqual(created, fetched)

        fetched_workbook = db_api.get_workbook(created_workbook.name)

        self.assertEqual(created_workbook, fetched_workbook)
        self.assertFalse(self.is_db_session_open())