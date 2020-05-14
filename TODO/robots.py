import re
import requests
from behave import step
from qa.settings import HOST_URL


@step('I hit the robots.txt url')
def step_impl(context):
    context.response = context.session.get(HOST_URL + '/robots.txt')


@step('it should have a "{code:d}" status code')
def step_impl(context, code):
    assert context.response.status_code == code, \
        'Did not get %s response, instead %i' % (
        code,
        context.response.status_code
    )


@step('it should contain User-agent: *')
def step_impl(context):
    assert 'User-agent: *' in context.response.text, \
        'Did not find User-agent: * in response.'


@step('it should disallow admin')
def step_impl(context):
    assert 'Disallow: /admin' in context.response.text, \
        'Did not find Disallow: /admin in response.'


@step('it should contain a sitemap url')
def step_impl(context):
    assert '/sitemap.xml' in context.response.text, \
        'Did not find Sitemap in response.'
