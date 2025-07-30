import uuid

class LanguageType:
    PYTHON = 'python'
    SQL = 'sql'
    JAVASCRIPT = 'javascript'


def res_success(ret):
    return {
        'status': 0,
        'msg': 'success',
        'result': ret,
        'trcid': str(uuid.uuid4())
    }


def res_failed(msg):
    return {
        'status': 0,
        'msg': msg,
        'result': {},
        'trcid': str(uuid.uuid4())
    }
