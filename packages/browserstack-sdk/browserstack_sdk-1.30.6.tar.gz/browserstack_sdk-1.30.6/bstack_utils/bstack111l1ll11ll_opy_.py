# coding: UTF-8
import sys
bstack111ll1_opy_ = sys.version_info [0] == 2
bstack1l11lll_opy_ = 2048
bstack111l1ll_opy_ = 7
def bstackl_opy_ (bstack1111111_opy_):
    global bstack1lllll1_opy_
    bstack111l111_opy_ = ord (bstack1111111_opy_ [-1])
    bstack1l11l11_opy_ = bstack1111111_opy_ [:-1]
    bstack1lll1l1_opy_ = bstack111l111_opy_ % len (bstack1l11l11_opy_)
    bstack1llll1_opy_ = bstack1l11l11_opy_ [:bstack1lll1l1_opy_] + bstack1l11l11_opy_ [bstack1lll1l1_opy_:]
    if bstack111ll1_opy_:
        bstack1llll1l_opy_ = unicode () .join ([unichr (ord (char) - bstack1l11lll_opy_ - (bstack1l1l1l_opy_ + bstack111l111_opy_) % bstack111l1ll_opy_) for bstack1l1l1l_opy_, char in enumerate (bstack1llll1_opy_)])
    else:
        bstack1llll1l_opy_ = str () .join ([chr (ord (char) - bstack1l11lll_opy_ - (bstack1l1l1l_opy_ + bstack111l111_opy_) % bstack111l1ll_opy_) for bstack1l1l1l_opy_, char in enumerate (bstack1llll1_opy_)])
    return eval (bstack1llll1l_opy_)
import os
import time
from bstack_utils.bstack11ll11l1l11_opy_ import bstack11ll11l11ll_opy_
from bstack_utils.constants import bstack11l1ll1111l_opy_
from bstack_utils.helper import get_host_info
class bstack111l1l1l1l1_opy_:
    bstackl_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡉࡣࡱࡨࡱ࡫ࡳࠡࡶࡨࡷࡹࠦ࡯ࡳࡦࡨࡶ࡮ࡴࡧࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡸ࡭ࠦࡴࡩࡧࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡶࡩࡷࡼࡥࡳ࠰ࠍࠤࠥࠦࠠࠣࠤࠥ῔")
    def __init__(self, config, logger):
        bstackl_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡀࡰࡢࡴࡤࡱࠥࡩ࡯࡯ࡨ࡬࡫࠿ࠦࡤࡪࡥࡷ࠰ࠥࡺࡥࡴࡶࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣࡧࡴࡴࡦࡪࡩࠍࠤࠥࠦࠠࠡࠢࠣࠤ࠿ࡶࡡࡳࡣࡰࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡣࡸࡺࡲࡢࡶࡨ࡫ࡾࡀࠠࡴࡶࡵ࠰ࠥࡺࡥࡴࡶࠣࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡹࡴࡳࡣࡷࡩ࡬ࡿࠠ࡯ࡣࡰࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤ῕")
        self.config = config
        self.logger = logger
        self.bstack1llllll1ll11_opy_ = bstackl_opy_ (u"ࠤࡷࡩࡸࡺ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳ࠵ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡱ࡮࡬ࡸ࠲ࡺࡥࡴࡶࡶࠦῖ")
        self.bstack1llllll11lll_opy_ = None
        self.bstack1llllll11l1l_opy_ = 60
        self.bstack1llllll11l11_opy_ = 5
        self.bstack1llllll1l1ll_opy_ = 0
    def bstack111l1ll111l_opy_(self, test_files, orchestration_strategy):
        bstackl_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡊࡰ࡬ࡸ࡮ࡧࡴࡦࡵࠣࡸ࡭࡫ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡸࡥࡲࡷࡨࡷࡹࠦࡡ࡯ࡦࠣࡷࡹࡵࡲࡦࡵࠣࡸ࡭࡫ࠠࡳࡧࡶࡴࡴࡴࡳࡦࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡵࡵ࡬࡭࡫ࡱ࡫࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥῗ")
        self.logger.debug(bstackl_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡍࡳ࡯ࡴࡪࡣࡷ࡭ࡳ࡭ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡽࡩࡵࡪࠣࡷࡹࡸࡡࡵࡧࡪࡽ࠿ࠦࡻࡾࠤῘ").format(orchestration_strategy))
        try:
            payload = {
                bstackl_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦῙ"): [{bstackl_opy_ (u"ࠨࡦࡪ࡮ࡨࡔࡦࡺࡨࠣῚ"): f} for f in test_files],
                bstackl_opy_ (u"ࠢࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡓࡵࡴࡤࡸࡪ࡭ࡹࠣΊ"): orchestration_strategy,
                bstackl_opy_ (u"ࠣࡰࡲࡨࡪࡏ࡮ࡥࡧࡻࠦ῜"): int(os.environ.get(bstackl_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡐࡒࡈࡊࡥࡉࡏࡆࡈ࡜ࠧ῝")) or bstackl_opy_ (u"ࠥ࠴ࠧ῞")),
                bstackl_opy_ (u"ࠦࡹࡵࡴࡢ࡮ࡑࡳࡩ࡫ࡳࠣ῟"): int(os.environ.get(bstackl_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡕࡔࡂࡎࡢࡒࡔࡊࡅࡠࡅࡒ࡙ࡓ࡚ࠢῠ")) or bstackl_opy_ (u"ࠨ࠱ࠣῡ")),
                bstackl_opy_ (u"ࠢࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠧῢ"): self.config.get(bstackl_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ΰ"), bstackl_opy_ (u"ࠩࠪῤ")),
                bstackl_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠨῥ"): self.config.get(bstackl_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧῦ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstackl_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥῧ"): os.environ.get(bstackl_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬῨ"), None),
                bstackl_opy_ (u"ࠢࡩࡱࡶࡸࡎࡴࡦࡰࠤῩ"): get_host_info(),
            }
            self.logger.debug(bstackl_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡧࡱࡨ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠿ࠦࡻࡾࠤῪ").format(payload))
            response = bstack11ll11l11ll_opy_.bstack1111111ll1l_opy_(self.bstack1llllll1ll11_opy_, payload)
            if response:
                self.bstack1llllll11lll_opy_ = self._1llllll111ll_opy_(response)
                self.logger.debug(bstackl_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡕࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧΎ").format(self.bstack1llllll11lll_opy_))
            else:
                self.logger.error(bstackl_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠰ࠥῬ"))
        except Exception as e:
            self.logger.error(bstackl_opy_ (u"ࠦࡠࡹࡰ࡭࡫ࡷࡘࡪࡹࡴࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹ࠺࠻ࠢࡾࢁࠧ῭").format(e))
    def _1llllll111ll_opy_(self, response):
        bstackl_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠦࡡ࡯ࡦࠣࡩࡽࡺࡲࡢࡥࡷࡷࠥࡸࡥ࡭ࡧࡹࡥࡳࡺࠠࡧ࡫ࡨࡰࡩࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧ΅")
        bstack1llll11ll_opy_ = {}
        bstack1llll11ll_opy_[bstackl_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ`")] = response.get(bstackl_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࠣ῰"), self.bstack1llllll11l1l_opy_)
        bstack1llll11ll_opy_[bstackl_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮ࠥ῱")] = response.get(bstackl_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡌࡲࡹ࡫ࡲࡷࡣ࡯ࠦῲ"), self.bstack1llllll11l11_opy_)
        bstack1llllll1ll1l_opy_ = response.get(bstackl_opy_ (u"ࠥࡶࡪࡹࡵ࡭ࡶࡘࡶࡱࠨῳ"))
        bstack1llllll1l111_opy_ = response.get(bstackl_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣῴ"))
        if bstack1llllll1ll1l_opy_:
            bstack1llll11ll_opy_[bstackl_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸ࡚ࡸ࡬ࠣ῵")] = bstack1llllll1ll1l_opy_.split(bstack11l1ll1111l_opy_ + bstackl_opy_ (u"ࠨ࠯ࠣῶ"))[1] if bstack11l1ll1111l_opy_ + bstackl_opy_ (u"ࠢ࠰ࠤῷ") in bstack1llllll1ll1l_opy_ else bstack1llllll1ll1l_opy_
        else:
            bstack1llll11ll_opy_[bstackl_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦῸ")] = None
        if bstack1llllll1l111_opy_:
            bstack1llll11ll_opy_[bstackl_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࡘࡶࡱࠨΌ")] = bstack1llllll1l111_opy_.split(bstack11l1ll1111l_opy_ + bstackl_opy_ (u"ࠥ࠳ࠧῺ"))[1] if bstack11l1ll1111l_opy_ + bstackl_opy_ (u"ࠦ࠴ࠨΏ") in bstack1llllll1l111_opy_ else bstack1llllll1l111_opy_
        else:
            bstack1llll11ll_opy_[bstackl_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹ࡛ࡲ࡭ࠤῼ")] = None
        if (
            response.get(bstackl_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ´")) is None or
            response.get(bstackl_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤ῾")) is None or
            response.get(bstackl_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰࠧ῿")) is None or
            response.get(bstackl_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧ ")) is None
        ):
            self.logger.debug(bstackl_opy_ (u"ࠥ࡟ࡵࡸ࡯ࡤࡧࡶࡷࡤࡹࡰ࡭࡫ࡷࡣࡹ࡫ࡳࡵࡵࡢࡶࡪࡹࡰࡰࡰࡶࡩࡢࠦࡒࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡰࡸࡰࡱࠦࡶࡢ࡮ࡸࡩ࠭ࡹࠩࠡࡨࡲࡶࠥࡹ࡯࡮ࡧࠣࡥࡹࡺࡲࡪࡤࡸࡸࡪࡹࠠࡪࡰࠣࡷࡵࡲࡩࡵࠢࡷࡩࡸࡺࡳࠡࡃࡓࡍࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢ "))
        return bstack1llll11ll_opy_
    def bstack111l1l11ll1_opy_(self):
        if not self.bstack1llllll11lll_opy_:
            self.logger.error(bstackl_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡧࡥࡹࡧࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠱ࠦ "))
            return None
        bstack1llllll1111l_opy_ = None
        test_files = []
        bstack1llllll11ll1_opy_ = int(time.time() * 1000) # bstack1llllll1l1l1_opy_ sec
        bstack1llllll111l1_opy_ = int(self.bstack1llllll11lll_opy_.get(bstackl_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࡏ࡮ࡵࡧࡵࡺࡦࡲࠢ "), self.bstack1llllll11l11_opy_))
        bstack1llllll1l11l_opy_ = int(self.bstack1llllll11lll_opy_.get(bstackl_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ "), self.bstack1llllll11l1l_opy_)) * 1000
        bstack1llllll1l111_opy_ = self.bstack1llllll11lll_opy_.get(bstackl_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦ "), None)
        bstack1llllll1ll1l_opy_ = self.bstack1llllll11lll_opy_.get(bstackl_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ "), None)
        if bstack1llllll1ll1l_opy_ is None and bstack1llllll1l111_opy_ is None:
            return None
        try:
            while bstack1llllll1ll1l_opy_ and (time.time() * 1000 - bstack1llllll11ll1_opy_) < bstack1llllll1l11l_opy_:
                response = bstack11ll11l11ll_opy_.bstack1111111llll_opy_(bstack1llllll1ll1l_opy_, {})
                if response and response.get(bstackl_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ ")):
                    bstack1llllll1111l_opy_ = response.get(bstackl_opy_ (u"ࠥࡸࡪࡹࡴࡴࠤ "))
                self.bstack1llllll1l1ll_opy_ += 1
                if bstack1llllll1111l_opy_:
                    break
                time.sleep(bstack1llllll111l1_opy_)
                self.logger.debug(bstackl_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡸࡥࡴࡷ࡯ࡸ࡛ࠥࡒࡍࠢࡤࡪࡹ࡫ࡲࠡࡹࡤ࡭ࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡻࡾࠢࡶࡩࡨࡵ࡮ࡥࡵ࠱ࠦ ").format(bstack1llllll111l1_opy_))
            if bstack1llllll1l111_opy_ and not bstack1llllll1111l_opy_:
                self.logger.debug(bstackl_opy_ (u"ࠧࡡࡧࡦࡶࡒࡶࡩ࡫ࡲࡦࡦࡗࡩࡸࡺࡆࡪ࡮ࡨࡷࡢࠦࡆࡦࡶࡦ࡬࡮ࡴࡧࠡࡱࡵࡨࡪࡸࡥࡥࠢࡷࡩࡸࡺࡳࠡࡨࡵࡳࡲࠦࡴࡪ࡯ࡨࡳࡺࡺࠠࡖࡔࡏࠦ "))
                response = bstack11ll11l11ll_opy_.bstack1111111llll_opy_(bstack1llllll1l111_opy_, {})
                if response and response.get(bstackl_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧ​")):
                    bstack1llllll1111l_opy_ = response.get(bstackl_opy_ (u"ࠢࡵࡧࡶࡸࡸࠨ‌"))
            if bstack1llllll1111l_opy_ and len(bstack1llllll1111l_opy_) > 0:
                for bstack111ll1llll_opy_ in bstack1llllll1111l_opy_:
                    file_path = bstack111ll1llll_opy_.get(bstackl_opy_ (u"ࠣࡨ࡬ࡰࡪࡖࡡࡵࡪࠥ‍"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llllll1111l_opy_:
                return None
            self.logger.debug(bstackl_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡓࡷࡪࡥࡳࡧࡧࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡴࡨࡧࡪ࡯ࡶࡦࡦ࠽ࠤࢀࢃࠢ‎").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstackl_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥࡵࡲࡥࡧࡵࡩࡩࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵ࠽ࠤࢀࢃࠢ‏").format(e))
            return None
    def bstack111l1l1ll11_opy_(self):
        bstackl_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡧࡦࡲ࡬ࡴࠢࡰࡥࡩ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠥࠦࠧ‐")
        return self.bstack1llllll1l1ll_opy_