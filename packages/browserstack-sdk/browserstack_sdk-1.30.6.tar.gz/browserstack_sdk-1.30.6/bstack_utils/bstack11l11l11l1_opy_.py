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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11ll11l1l11_opy_ import bstack11ll11l11ll_opy_
from bstack_utils.constants import bstack11l1ll1111l_opy_, bstack11lll11111_opy_
from bstack_utils.bstack1l11ll11_opy_ import bstack1ll11l11l1_opy_
from bstack_utils import bstack1ll11l1ll_opy_
bstack11l1l11l1l1_opy_ = 10
class bstack1l11111l1l_opy_:
    def __init__(self, bstack1l111l111l_opy_, config, bstack11l1l1l1111_opy_=0):
        self.bstack11l1l11ll11_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l1l1ll111_opy_ = bstackl_opy_ (u"ࠦࢀࢃ࠯ࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳࡫ࡧࡩ࡭ࡧࡧ࠱ࡹ࡫ࡳࡵࡵࠥ᪻").format(bstack11l1ll1111l_opy_)
        self.bstack11l1l1l11ll_opy_ = os.path.join(tempfile.gettempdir(), bstackl_opy_ (u"ࠧࡧࡢࡰࡴࡷࡣࡧࡻࡩ࡭ࡦࡢࡿࢂࠨ᪼").format(os.environ.get(bstackl_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇ᪽ࠫ"))))
        self.bstack11l1l111ll1_opy_ = os.path.join(tempfile.gettempdir(), bstackl_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡻࡾ࠰ࡷࡼࡹࠨ᪾").format(os.environ.get(bstackl_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉᪿ࠭"))))
        self.bstack11l1l1l111l_opy_ = 2
        self.bstack1l111l111l_opy_ = bstack1l111l111l_opy_
        self.config = config
        self.logger = bstack1ll11l1ll_opy_.get_logger(__name__, bstack11lll11111_opy_)
        self.bstack11l1l1l1111_opy_ = bstack11l1l1l1111_opy_
        self.bstack11l1l1l1ll1_opy_ = False
        self.bstack11l1l1l1lll_opy_ = not (
                            os.environ.get(bstackl_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒᫀࠣ")) and
                            os.environ.get(bstackl_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨ᫁")) and
                            os.environ.get(bstackl_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡔ࡚ࡁࡍࡡࡑࡓࡉࡋ࡟ࡄࡑࡘࡒ࡙ࠨ᫂"))
                        )
        if bstack1ll11l11l1_opy_.bstack11l1l11l11l_opy_(config):
            self.bstack11l1l1l111l_opy_ = bstack1ll11l11l1_opy_.bstack11l1l11l111_opy_(config, self.bstack11l1l1l1111_opy_)
            self.bstack11l1l11llll_opy_()
    def bstack11l1l111lll_opy_(self):
        return bstackl_opy_ (u"ࠧࢁࡽࡠࡽࢀ᫃ࠦ").format(self.config.get(bstackl_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦ᫄ࠩ")), os.environ.get(bstackl_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭᫅")))
    def bstack11l1l1l1l1l_opy_(self):
        try:
            if self.bstack11l1l1l1lll_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l1l111ll1_opy_, bstackl_opy_ (u"ࠣࡴࠥ᫆")) as f:
                        bstack11l1l1l11l1_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l1l1l11l1_opy_ = set()
                bstack11l1l111l1l_opy_ = bstack11l1l1l11l1_opy_ - self.bstack11l1l11ll11_opy_
                if not bstack11l1l111l1l_opy_:
                    return
                self.bstack11l1l11ll11_opy_.update(bstack11l1l111l1l_opy_)
                data = {bstackl_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࡖࡨࡷࡹࡹࠢ᫇"): list(self.bstack11l1l11ll11_opy_), bstackl_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠨ᫈"): self.config.get(bstackl_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ᫉")), bstackl_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴ᫊ࠥ"): os.environ.get(bstackl_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬ᫋")), bstackl_opy_ (u"ࠢࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠧᫌ"): self.config.get(bstackl_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᫍ"))}
            response = bstack11ll11l11ll_opy_.bstack11l1l11ll1l_opy_(self.bstack11l1l1ll111_opy_, data)
            if response.get(bstackl_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤᫎ")) == 200:
                self.logger.debug(bstackl_opy_ (u"ࠥࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡶࡩࡳࡺࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࡀࠠࡼࡿࠥ᫏").format(data))
            else:
                self.logger.debug(bstackl_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡱࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶ࠾ࠥࢁࡽࠣ᫐").format(response))
        except Exception as e:
            self.logger.debug(bstackl_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡦࡸࡶ࡮ࡴࡧࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧ᫑").format(e))
    def bstack11l1l1ll1l1_opy_(self):
        if self.bstack11l1l1l1lll_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l1l111ll1_opy_, bstackl_opy_ (u"ࠨࡲࠣ᫒")) as f:
                        bstack11l1l11l1ll_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l1l11l1ll_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstackl_opy_ (u"ࠢࡑࡱ࡯ࡰࡪࡪࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠥ᫓").format(failed_count))
                if failed_count >= self.bstack11l1l1l111l_opy_:
                    self.logger.info(bstackl_opy_ (u"ࠣࡖ࡫ࡶࡪࡹࡨࡰ࡮ࡧࠤࡨࡸ࡯ࡴࡵࡨࡨࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᫔").format(failed_count, self.bstack11l1l1l111l_opy_))
                    self.bstack11l1l1l1l11_opy_(failed_count)
                    self.bstack11l1l1l1ll1_opy_ = True
            return
        try:
            response = bstack11ll11l11ll_opy_.bstack11l1l1ll1l1_opy_(bstackl_opy_ (u"ࠤࡾࢁࡄࡨࡵࡪ࡮ࡧࡒࡦࡳࡥ࠾ࡽࢀࠪࡧࡻࡩ࡭ࡦࡕࡹࡳࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ࠿ࡾࢁࠫࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࡀࡿࢂࠨ᫕").format(self.bstack11l1l1ll111_opy_, self.config.get(bstackl_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭᫖")), os.environ.get(bstackl_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪ᫗")), self.config.get(bstackl_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᫘"))))
            if response.get(bstackl_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨ᫙")) == 200:
                failed_count = response.get(bstackl_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࡔࡦࡵࡷࡷࡈࡵࡵ࡯ࡶࠥ᫚"), 0)
                self.logger.debug(bstackl_opy_ (u"ࠣࡒࡲࡰࡱ࡫ࡤࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡤࡱࡸࡲࡹࡀࠠࡼࡿࠥ᫛").format(failed_count))
                if failed_count >= self.bstack11l1l1l111l_opy_:
                    self.logger.info(bstackl_opy_ (u"ࠤࡗ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡩࡲࡰࡵࡶࡩࡩࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᫜").format(failed_count, self.bstack11l1l1l111l_opy_))
                    self.bstack11l1l1l1l11_opy_(failed_count)
                    self.bstack11l1l1l1ll1_opy_ = True
            else:
                self.logger.error(bstackl_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡰ࡮࡯ࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢ᫝").format(response))
        except Exception as e:
            self.logger.error(bstackl_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡥࡷࡵ࡭ࡳ࡭ࠠࡱࡱ࡯ࡰ࡮ࡴࡧ࠻ࠢࡾࢁࠧ᫞").format(e))
    def bstack11l1l1l1l11_opy_(self, failed_count):
        with open(self.bstack11l1l1l11ll_opy_, bstackl_opy_ (u"ࠧࡽࠢ᫟")) as f:
            f.write(bstackl_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦࠣࡥࡹࠦࡻࡾ࡞ࡱࠦ᫠").format(datetime.now()))
            f.write(bstackl_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸ࠿ࠦࡻࡾ࡞ࡱࠦ᫡").format(failed_count))
        self.logger.debug(bstackl_opy_ (u"ࠣࡃࡥࡳࡷࡺࠠࡃࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡨࡸࡥࡢࡶࡨࡨ࠿ࠦࡻࡾࠤ᫢").format(self.bstack11l1l1l11ll_opy_))
    def bstack11l1l11llll_opy_(self):
        def bstack11l1l1ll11l_opy_():
            while not self.bstack11l1l1l1ll1_opy_:
                time.sleep(bstack11l1l11l1l1_opy_)
                self.bstack11l1l1l1l1l_opy_()
                self.bstack11l1l1ll1l1_opy_()
        bstack11l1l11lll1_opy_ = threading.Thread(target=bstack11l1l1ll11l_opy_, daemon=True)
        bstack11l1l11lll1_opy_.start()