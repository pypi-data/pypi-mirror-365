import dis

class MustBeQualified:
    
    def __init__(self, *a, **k):

        try:
            raise Exception()
        except Exception as e:
            traceback = e.__traceback__

        MustBeQualified._error_if_unqualified(traceback)

        super().__init__(*a, **k)

    @classmethod
    def _error_if_unqualified(cls, tb):
        f = tb.tb_frame
        prev = None
        relevant_co = None
        while f is not None:
            if prev is not None:
                if prev.f_code.co_name == "__init__" and f.f_code.co_name != "__init__":
                    relevant_co = f.f_code
                    break
            prev = f
            f = f.f_back

        enclosing_class, _, _ = prev.f_code.co_qualname.partition(".")
        _, _, enclosing_module_fn = prev.f_code.co_filename.rpartition("/")
        enclosing_module, _, _ = enclosing_module_fn.partition(".")

        a = list(dis.get_instructions(relevant_co))

        for i, j in zip(a, a[1:]):
            if (
                f.f_lineno == i.positions.lineno 
                and (i.opname == "LOAD_GLOBAL"  or i.opname == "LOAD_NAME")
                and str(i.argval).rpartition(".")[2] == enclosing_module 
                and j.opname == "LOAD_ATTR" and j.argval == enclosing_class
            ):
                break
        else:
            raise Exception(f"Class {enclosing_class} was instantiated from an alias.")
