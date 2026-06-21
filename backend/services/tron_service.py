"""
TRON 链交互服务
"""
import httpx
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from config import settings
import logging

logger = logging.getLogger(__name__)


class TronService:
    def __init__(self):
        network = settings.TRON_NETWORK
        if network == "mainnet":
            self.network_url = "https://api.trongrid.io"
        elif network == "nile":
            self.network_url = "https://api.nileex.io"
        else:  # shasta
            self.network_url = "https://api.shasta.trongrid.io"

        self.client = Tron(network=network, api_key=settings.TRON_API_KEY)
        self.wallet_address = settings.TRON_WALLET_ADDRESS

    def get_account_balance(self, address: str) -> float:
        """获取账户余额 (TRX)"""
        try:
            account = self.client.get_account(address)
            balance = account.get("balance", 0)
            return balance / 1_000_000  # SUN → TRX
        except Exception as e:
            logger.error(f"获取余额失败 {address}: {e}")
            return 0.0

    def get_account_energy(self, address: str) -> dict:
        """获取账户能量和带宽"""
        try:
            account_resource = self.client.get_account_resource(address)
            return {
                "energy_limit": account_resource.get("EnergyLimit", 0),
                "energy_used": account_resource.get("EnergyUsed", 0),
                "net_limit": account_resource.get("NetLimit", 0),
                "net_used": account_resource.get("NetUsed", 0),
            }
        except Exception as e:
            logger.error(f"获取能量失败 {address}: {e}")
            return {}

    def get_transaction_info(self, txid: str) -> dict:
        """查询交易状态"""
        try:
            tx_info = self.client.get_transaction(txid)
            return {
                "block_number": tx_info.get("blockNumber"),
                "confirm": tx_info.get("confirm", False),
                "contract_type": tx_info["raw_data"]["contract"][0]["type"],
            }
        except Exception as e:
            logger.error(f"查询交易失败 {txid}: {e}")
            return {}

    def freeze_balance(self, address: str, amount: int, days: int) -> dict:
        """
        冻结TRX获取能量
        amount: TRX数量 (不是SUN)
        days: 冻结天数 (只能填3)
        返回 txid
        """
        try:
            private_key = PrivateKey(bytes.fromhex(settings.TRON_WALLET_PRIVATE_KEY))
            # 冻结 1 TRX ≈ 1 天内约 1000 能量，动态计算
            trx_amount = amount
            burn_ratio = 1  # 每1 TRX 约对应 1 天冻结期

            txn = (
                self.client.freeze_balance(trx_amount)
                .instance("owner_address", address)
                .fee_limit(50_000_000)
                .build()
                .sign(private_key)
            )
            result = txn.broadcast()
            return {"success": True, "txid": result.get("txid")}
        except Exception as e:
            logger.error(f"冻结失败: {e}")
            return {"success": False, "error": str(e)}

    def unfreeze_balance(self, address: str) -> dict:
        """解冻TRX"""
        try:
            private_key = PrivateKey(bytes.fromhex(settings.TRON_WALLET_PRIVATE_KEY))
            txn = (
                self.client.unfreeze_balance()
                .instance("owner_address", address)
                .fee_limit(50_000_000)
                .build()
                .sign(private_key)
            )
            result = txn.broadcast()
            return {"success": True, "txid": result.get("txid")}
        except Exception as e:
            logger.error(f"解冻失败: {e}")
            return {"success": False, "error": str(e)}

    def estimate_energy_cost(self, contract_address: str) -> int:
        """估算某合约能量消耗"""
        try:
            resource = self.clientestimate_energy(contract_address)
            return resource.get("energy_required", 0)
        except Exception:
            return 10000  # 默认估算值

    def validate_address(self, address: str) -> bool:
        """验证TRX地址合法性"""
        try:
            return self.client.is_address(address)
        except Exception:
            return False


tron_service = TronService()
