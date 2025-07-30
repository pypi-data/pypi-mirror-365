from .strg import like
from .logging import log


class Wtry:
    def __init__(self, e_ref):
        self.e_ref = e_ref

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            s = "[Wtry] No exception was caught"
            log(s)
            raise Exception(s)
        if like(str(exc_val), self.e_ref):
            log(f"[Wtry] Exception caught match expected ('{self.e_ref}')")
            return True
        else:
            s = f"[Wtry] Exception caught ('{exc_val}') don't match expected ('{self.e_ref}')"
            log(s)
            raise Exception(s)


def ttry(f, e_ref, *args, **kwargs):

    exception_occured = False
    try:
        f(*args, **kwargs)
    except Exception as e:
        exception_occured = True
        if like(str(e), e_ref):
            log(f"[ttry] Exception caught match expected ('{e_ref}')")
        else:
            s = f"[ttry] Exception caught ('{str(e)}') don't match expected ('{e_ref}')"
            log(s)
            raise Exception(s)

    if not exception_occured:
        s = "[ttry] No exception was caught"
        log(s)
        raise Exception(s)
