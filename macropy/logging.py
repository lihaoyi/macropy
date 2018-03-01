# -*- coding: utf-8 -*-
# :Project:   macropy3 -- enable basic logging
# :Created:   gio 01 mar 2018 02:43:14 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
log.debug('Log started')
