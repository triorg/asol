import logging
from . import logger
log = logging.getLogger(__name__)
log.addHandler(logger.handler)
import sys
import os
from . import params
from . import runner
from . import __version__

"""
The command line interface.
"""

def main ():
    # pars=params.ParamsPrepare()
    pars=params.args_read()
    if pars.version:
        print(__version__)
        sys.exit(0)

    run=runner.Runner(pars)
    if pars.debug_params:
        run.debug_pars()
        sys.exit(0)

    # log.info("")
    # runner.count_files_norecurse(pars.input)
    ###
    # file: YYYY-MMMM-DD_DW
    # date, text
    # date in filename should be same in atribute

    # runner.ActOnParams(pars)
    # print(runner.count_files_norecurse(pars.input))
    # files_count=runner.count_files(pars.input)
    # logroot.info(f"Processing {files_count} files")

if __name__ == '__main__':
    main()
