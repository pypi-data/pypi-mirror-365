from typing import Final

from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.test.aws.url import build_dynamic_url


ROOT__: Final[list] = [AA.Account]

def read_user_title_list_url():
    return build_dynamic_url(ROOT__, [AA.UserTitle, AA.List])

def read_user_flag_list_url():
    return build_dynamic_url(ROOT__, [AA.UserFlag, AA.List])
