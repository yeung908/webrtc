# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging

from telemetry.core import exceptions
from telemetry.core import web_contents
from telemetry.core import util

class Oobe(web_contents.WebContents):
  def __init__(self, inspector_backend, backend_list):
    super(Oobe, self).__init__(inspector_backend, backend_list)

  def _GaiaLoginContext(self):
    for gaia_context in range(15):
      try:
        if self.EvaluateJavaScriptInContext(
            "document.getElementById('Email') != null", gaia_context):
          return gaia_context
      except exceptions.EvaluateException:
        pass
    return None

  def _ExecuteOobeApi(self, api, *args):
    logging.info('Invoking %s' % api)
    self.WaitForJavaScriptExpression("typeof Oobe == 'function'", 20)

    if self.EvaluateJavaScript("typeof %s == 'undefined'" % api):
      raise exceptions.LoginException('%s js api missing' % api)

    js = api + '(' + ("'%s'," * len(args)).rstrip(',') + ');'
    self.ExecuteJavaScript(js % args)

  def NavigateGuestLogin(self):
    """Logs in as guest."""
    self._ExecuteOobeApi('Oobe.guestLoginForTesting')

  def NavigateFakeLogin(self, username, password):
    """Fake user login."""
    self._ExecuteOobeApi('Oobe.loginForTesting', username, password)

  def NavigateGaiaLogin(self, username, password):
    """Logs in to GAIA with provided credentials."""
    self._ExecuteOobeApi('Oobe.addUserForTesting')

    gaia_context = util.WaitFor(self._GaiaLoginContext, timeout=30)

    self.ExecuteJavaScriptInContext("""
        document.getElementById('Email').value='%s';
        document.getElementById('Passwd').value='%s';
        document.getElementById('signIn').click();"""
            % (username, password),
        gaia_context)
