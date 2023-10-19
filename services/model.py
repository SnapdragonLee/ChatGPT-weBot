class Selfinfo:
    def __init__(self, wxid, name, account_id, data_path, save_path, db_key):
        self.wx_id = wxid
        self.wx_idname = name
        self.wx_idaccount_id = account_id
        self.wx_iddata_path = data_path
        self.wx_idsave_path = save_path
        self.wx_iddb_key = db_key


class BotError(Exception):
    """
    Base class for exceptions in this module.
    Error codes:
    -9: Unknown error
    -3: response runtime error
    -2: API busy error
    -1: User error
    """

    error: str
    message: str
    code: int

    def __init__(self, source: str, message: str, code: int = 0) -> None:
        self.error = source
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.error}: {self.message} (code: {self.code})"
