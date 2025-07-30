# -*- coding: utf-8 -*-

import sys
import warnings
from datetime import datetime
from google.cloud import bigquery
from IPython.core.magic import Magics, line_cell_magic, magics_class
try:
    from traitlets.config.configurable import Configurable
    from traitlets import Bool, Int, Unicode
except ImportError:
    from IPython.config.configurable import Configurable
    from IPython.utils.traitlets import Bool, Int, Unicode

__version__ = "0.1.4"

@magics_class
class BigqueryMagic(Magics, Configurable):
    autolimit = Int(
        1000000,
        config=True,
        allow_none=True,
        help="Automatically limit the number of rows to be returned (Set None to retrieve all rows)"
    )
    usepolars = Bool(
        False,
        config=True,
        help="Use polars instead of pandas to return the result.  "
             "This is useful for large datasets, but requires polars to be installed."
    )
    showtime = Bool(
        True,
        config=True,
        help="Show execution time message"
    )
    showbytes = Bool(
        True,
        config=True,
        help="Show total bytes after execution"
    )
    showquery = Bool(
        False,
        config=True,
        help="Show query to run"
    )
    quiet = Bool(
        False,
        config=True,
        help="Display no message"
    )
    localjson = Unicode(
        None,
        config=True,
        allow_none=True,
        help="Local json file for authenticating to bigquery"
    )

    @line_cell_magic
    def bq(self, line, cell=""):
        query = line or cell
        if self.showquery and not self.quiet:
            print(f"Running query: {query}", file=sys.stderr)

        t1 = datetime.now()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # This is to avoid the warning:
            #   Your application has authenticated using end user credentials from Google Cloud SDK without a quota project
            if self.localjson is not None:
                client = bigquery.Client.from_service_account_json(self.localjson)
            else:
                client = bigquery.Client()
            job = client.query(query)
            if self.showtime and not self.quiet:
                print(f"Start query at {t1}", file=sys.stderr)
        result = job.result() # wait until the job finshes
        t2 = datetime.now()
        if not self.quiet:
            if self.showtime and self.showbytes:
                print(f"End query at {t2} (Execution time: {t2-t1}, Processed: {round(job.total_bytes_processed/1024**3, 1)} GB)", file=sys.stderr)
            elif self.showtime:
                print(f"End query at {t2} (Execution time: {t2-t1})", file=sys.stderr)
            elif self.showbytes:
                print(f"Processed: {round(job.total_bytes_processed/1024**3, 1)} GB", file=sys.stderr)

        if self.autolimit is None or result.total_rows <= self.autolimit:
            # no limit or within the limit
            data = [dict(row.items()) for row in result]
        else:
            data = []
            for i, row in enumerate(result):
                if i >= self.autolimit:
                    if not self.quiet:
                        print(f"Result is truncated at the row {self.autolimit} of {result.total_rows}", file=sys.stderr)
                    break
                data.append(dict(row.items()))
        if len(data) == 0:
            return None  # No result returned
        if self.usepolars:
            import polars as pl
            return pl.DataFrame(data)
        else:
            import pandas as pd
            return pd.DataFrame(data)


def load_ipython_extension(ipython):
    ipython.register_magics(BigqueryMagic)
