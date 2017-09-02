#!/usr/bin/env python
__author__ = 'Declan Shanaghy <declan@shanaghy.com>'


import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Processes all stacks in the account and deletes the old ones
    :param event: The event which triggered the lambda function
    :type event: See http://docs.aws.amazon.com/lambda/latest/
                 dg/python-programming-model-handler-types.html
    :param context: Lambda execution context object
    :type context: See http://docs.aws.amazon.com/lambda/latest/
                 dg/python-context-object.html
    :return: dictionary containing summary information of actions taken
    :rtype: dict
    """
    logger.info('action=handler, status=start, event=%s', event)
    logger.debug('action=debug_context, context="%s"', dir(context))

    return True

