"""Test config entries API."""

import asyncio
from collections import OrderedDict
from unittest.mock import patch

import pytest
import voluptuous as vol

from homeassistant.config_entries import ConfigFlowHandler, HANDLERS
from homeassistant.setup import async_setup_component
from homeassistant.components.config import config_entries


@pytest.fixture
def client(hass, test_client):
    """Fixture that can interact with the config manager API."""
    hass.loop.run_until_complete(async_setup_component(hass, 'http', {}))
    hass.loop.run_until_complete(config_entries.async_setup(hass))
    yield hass.loop.run_until_complete(test_client(hass.http.app))


@asyncio.coroutine
def test_initialize_flow(hass, client):
    """Test we can initialize a flow."""
    class TestFlow(ConfigFlowHandler):
        @asyncio.coroutine
        def async_step_init(self, user_input=None):
            schema = OrderedDict()
            schema[vol.Required('username')] = str
            schema[vol.Required('password')] = str

            return self.async_show_form(
                title='test-title',
                step_id='init',
                description='test-description',
                data_schema=schema,
                errors={
                    'username': 'Should be unique.'
                }
            )

    with patch.dict(HANDLERS, {'test': TestFlow}):
        resp = yield from client.post('/api/config/config_entries/flow',
                                      json={'domain': 'test'})

    assert resp.status == 200
    data = yield from resp.json()

    assert data['title'] == 'test-title'
    assert data['description'] == 'test-description'
    assert data['data_schema'] == [
        {
            'name': 'username',
            'required': True,
            'type': 'string'
        },
        {
            'name': 'password',
            'required': True,
            'type': 'string'
        }
    ]
    assert data['errors'] == {
        'username': 'Should be unique.'
    }


@asyncio.coroutine
def test_abort(hass, client):
    """Test a flow that aborts."""
    class TestFlow(ConfigFlowHandler):
        @asyncio.coroutine
        def async_step_init(self, user_input=None):
            return self.async_abort(reason='bla')

    with patch.dict(HANDLERS, {'test': TestFlow}):
        resp = yield from client.post('/api/config/config_entries/flow',
                                      json={'domain': 'test'})

    assert resp.status == 200
    data = yield from resp.json()
    data.pop('flow_id')
    assert data == {
        'reason': 'bla',
        'type': 'abort'
    }


@asyncio.coroutine
def test_create_account(hass, client):
    """Test a flow that creates an account."""
    class TestFlow(ConfigFlowHandler):
        ENTRY_SCHEMA = vol.Schema({
            'secret': str
        })

        @asyncio.coroutine
        def async_step_init(self, user_input=None):
            return self.async_create_entry(
                title='Test Entry',
                data={'secret': 'account_token'}
            )

    with patch.dict(HANDLERS, {'test': TestFlow}):
        resp = yield from client.post('/api/config/config_entries/flow',
                                      json={'domain': 'test'})

    assert resp.status == 200
    data = yield from resp.json()
    data.pop('flow_id')
    assert data == {
        'title': 'Test Entry',
        'type': 'create_entry'
    }


@asyncio.coroutine
def test_two_step_flow(hass, client):
    """Test we can finish a two step flow."""
    class TestFlow(ConfigFlowHandler):
        ENTRY_SCHEMA = vol.Schema({
            'secret': str
        })

        @asyncio.coroutine
        def async_step_init(self, user_input=None):
            return self.async_show_form(
                title='test-title',
                step_id='account',
                data_schema=vol.Schema({
                    'user_title': str
                }))

        @asyncio.coroutine
        def async_step_account(self, user_input=None):
            return self.async_create_entry(
                title=user_input['user_title'],
                data={'secret': 'account_token'}
            )

    with patch.dict(HANDLERS, {'test': TestFlow}):
        resp = yield from client.post('/api/config/config_entries/flow',
                                      json={'domain': 'test'})
        assert resp.status == 200
        data = yield from resp.json()
        assert data['type'] == 'form'
        assert data['data_schema'] == [
            {
                'name': 'user_title',
                'type': 'string'
            }
        ]

    with patch.dict(HANDLERS, {'test': TestFlow}):
        resp = yield from client.post(
            '/api/config/config_entries/flow/{}'.format(data['flow_id']),
            json={'user_title': 'user-title'})
        assert resp.status == 200
        data = yield from resp.json()
        assert data['type'] == 'create_entry'
        assert data['title'] == 'user-title'


@asyncio.coroutine
def test_aborting_flow(hass, client):
    """."""
    # TODO


@asyncio.coroutine
def test_get_entries(hass, client):
    """."""
    # TODO


@asyncio.coroutine
def test_get_progress_index(hass, client):
    """."""
    # TODO


@asyncio.coroutine
def test_get_progress_flow(hass, client):
    """."""
    # TODO


@asyncio.coroutine
def test_remove_entry(hass, client):
    """."""
    # TODO


@asyncio.coroutine
def test_available_flows(hass, client):
    """."""
    # TODO
