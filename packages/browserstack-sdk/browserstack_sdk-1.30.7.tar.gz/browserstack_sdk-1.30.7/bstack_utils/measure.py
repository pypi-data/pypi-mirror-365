# coding: UTF-8
import sys
bstack1ll11l1_opy_ = sys.version_info [0] == 2
bstack11l11l_opy_ = 2048
bstack11lll_opy_ = 7
def bstack1l11l11_opy_ (bstack1llll11_opy_):
    global bstack11ll1l1_opy_
    bstack111l111_opy_ = ord (bstack1llll11_opy_ [-1])
    bstack11lll11_opy_ = bstack1llll11_opy_ [:-1]
    bstack1ll11_opy_ = bstack111l111_opy_ % len (bstack11lll11_opy_)
    bstack1l1l_opy_ = bstack11lll11_opy_ [:bstack1ll11_opy_] + bstack11lll11_opy_ [bstack1ll11_opy_:]
    if bstack1ll11l1_opy_:
        bstack11l1l1_opy_ = unicode () .join ([unichr (ord (char) - bstack11l11l_opy_ - (bstack111l1l1_opy_ + bstack111l111_opy_) % bstack11lll_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l_opy_)])
    else:
        bstack11l1l1_opy_ = str () .join ([chr (ord (char) - bstack11l11l_opy_ - (bstack111l1l1_opy_ + bstack111l111_opy_) % bstack11lll_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l_opy_)])
    return eval (bstack11l1l1_opy_)
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1l1ll11lll_opy_ import get_logger
from bstack_utils.bstack1l1l11llll_opy_ import bstack1ll1l1lllll_opy_
bstack1l1l11llll_opy_ = bstack1ll1l1lllll_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l1lll11l_opy_: Optional[str] = None):
    bstack1l11l11_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡆࡨࡧࡴࡸࡡࡵࡱࡵࠤࡹࡵࠠ࡭ࡱࡪࠤࡹ࡮ࡥࠡࡵࡷࡥࡷࡺࠠࡵ࡫ࡰࡩࠥࡵࡦࠡࡣࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡵ࡮ࠋࠢࠣࠤࠥࡧ࡬ࡰࡰࡪࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࠡࡰࡤࡱࡪࠦࡡ࡯ࡦࠣࡷࡹࡧࡧࡦ࠰ࠍࠤࠥࠦࠠࠣࠤࠥᷫ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll11l1l111_opy_: str = bstack1l1l11llll_opy_.bstack11ll1ll111l_opy_(label)
            start_mark: str = label + bstack1l11l11_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᷬ")
            end_mark: str = label + bstack1l11l11_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᷭ")
            result = None
            try:
                if stage.value == STAGE.bstack11l1l11l_opy_.value:
                    bstack1l1l11llll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1l1l11llll_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l1lll11l_opy_)
                elif stage.value == STAGE.bstack1lll11l1_opy_.value:
                    start_mark: str = bstack1ll11l1l111_opy_ + bstack1l11l11_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᷮ")
                    end_mark: str = bstack1ll11l1l111_opy_ + bstack1l11l11_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᷯ")
                    bstack1l1l11llll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1l1l11llll_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l1lll11l_opy_)
            except Exception as e:
                bstack1l1l11llll_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l1lll11l_opy_)
            return result
        return wrapper
    return decorator