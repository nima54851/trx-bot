"""
TRON 链交互服务（懒加载，避免启动时崩溃）
"""
import logging

logger = logging.getLogger(__name__)

# ── 懒加载，避免 env 没填时整个 app 启动失败 ──
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    from tronpy import Tron
    from tronpy.providers import HTTPProvider
    from config import settings

    network = settings.TRON_NETWORK or "mainnet"
    if network == "mainnet":
        network_url = "https://api.trongrid.io"
    elif network == "nile":
        network_url = "https://api.nileex.io"
    else:
        network_url = "https://api.shasta.trongrid.io"

    api_key = settings.TRON_API_KEY
    if api_key:
        provider = HTTPProvider(network_url, api_key=api_key)
    else:
        provider = HTTPProvider(network_url)

    _client = Tron(network=network, provider=provider)
    logger.info(f"TronService 初始化完成，网络: {network}")
    return _client


def _get_wallet_address():
    from config import settings
    return settings.TRON_WALLET_ADDRESS


class TronService:
    """TRON 链交互服务（代理到懒加载 client）"""

    @property
    def client(self):
        return _get_client()

    @property
    def wallet_address(self) -> str:
        return _get_wallet_address()

    @property
    def network(self) -> str:
        from config import settings
        return settings.TRON_NETWORK or "mainnet"

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
            resource = self.client.get_account_resource(address)
            return {
                "energy_limit": resource.get("EnergyLimit", 0),
                "energy_used": resource.get("EnergyUsed", 0),
                "net_limit": resource.get("NetLimit", 0),
                "net_used": resource.get("NetUsed", 0),
            }
        except Exception as e:
            logger.error(f"获取能量失败 {address}: {e}")
            return {}

    def get_transaction_info(self, txid: str) -> dict:
        """查询交易状态"""
        try:
            tx = self.client.get_transaction(txid)
            raw = tx.get("raw_data", {})
            contracts = raw.get("contract", [])
            return {
                "block_number": tx.get("blockNumber"),
                "confirmed": tx.get("confirmed", False),
                "contract_type": contracts[0]["type"] if contracts else "Unknown",
            }
        except Exception as e:
            logger.error(f"查询交易失败 {txid}: {e}")
            return {}

    def freeze_balance(self, address: str, amount: int, days: int = 3) -> dict:
        """
        冻结TRX获取能量
        amount: TRX数量（不是SUN）
        """
        try:
            from tronpy.keys import PrivateKey
            from config import settings

            private_key = PrivateKey(bytes.fromhex(settings.TRON_WALLET_PRIVATE_KEY))
            receiver = address if address != _get_wallet_address() else None

            builder = self.client.freeze_balance(amount).TRXPower(
                resource="ENERGY"
            ).fee_limit(50_000_000)

            if receiver:
                builder = builder.receiver_address(receiver)

            txn = builder.build().sign(private_key)
            result = txn.broadcast()
            return {"success": True, "txid": result.get("txid")}
        except Exception as e:
            logger.error(f"冻结失败: {e}")
            return {"success": False, "error": str(e)}

    def unfreeze_balance(self, address: str) -> dict:
        """解冻TRX"""
        try:
            from tronpy.keys import PrivateKey
            from config import settings

            private_key = PrivateKey(bytes.fromhex(settings.TRON_WALLET_PRIVATE_KEY))
            txn = (
                self.client.unfreeze_balance()
                .TRXPower(resource="ENERGY")
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
            resource = self.client.estimate_energy(contract_address)
            return resource.get("energy_required", 0)
        except Exception as e:
            logger.warning(f"能量估算失败: {e}，使用默认值 10000")
            return 10000

    def validate_address(self, address: str) -> bool:
        """验证TRX地址合法性"""
        try:
            return bool(self.client.is_address(address))
        except Exception:
            return False


tron_service = TronService()
