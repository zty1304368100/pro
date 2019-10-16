import json

from eslcampus.settings import REDIS_CONN


def set_kv(to_user, msg_dict):
    """
    设置键值对
    """
    REDIS_CONN.set(to_user,json.dumps(msg_dict))

    return True


