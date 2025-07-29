from typing import Union
from testnet.interfaces.logs import Logger  # Using your custom logger
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import transfer, TransferParams
from solana.rpc.commitment import Confirmed


class SolanaTransaction:
    def __init__(self, rpc_url: str = "https://devnet.helius-rpc.com/?api-key=b350b993-1ca8-4557-95aa-9e96897cce14"):
        """
        Initializes the Solana client.
        :param rpc_url: URL of the RPC server.
        """
        self._logger = Logger("solana-transactions.log").get_logger()
        self.client = Client(rpc_url)
        self.rpc_url = rpc_url

        # Reliable connection check
        try:
            self.client.get_slot(commitment=Confirmed)
            self._logger.info(f"Successfully connected to RPC node: {rpc_url}")
        except Exception as e:
            self._logger.error(f"Failed to connect to RPC node: {e}")

    def send_transaction(self, sender_private_key_hex: str, recipient_address: str, amount_sol: float) -> Union[
        str, dict]:
        """
        Creates, sends, and confirms a Solana transaction.
        :param sender_private_key_hex: The sender's private key in hex format.
        :param recipient_address: The recipient's public address.
        :param amount_sol: The amount of SOL to send.
        :return: A transaction URL on success, or an error dictionary on failure.
        """
        try:
            # --- 1. PRE-FLIGHT CHECKS ---
            self._logger.info(f"Starting transaction to {recipient_address} for {amount_sol} SOL.")

            try:
                recipient_pubkey = PublicKey(recipient_address)
            except Exception:
                error_msg = f"Invalid recipient address provided: {recipient_address}"
                self._logger.error(error_msg)
                return {"error": error_msg}

            if not isinstance(amount_sol, (int, float)) or amount_sol <= 0:
                error_msg = f"Invalid amount: {amount_sol}. Must be a positive number."
                self._logger.error(error_msg)
                return {"error": error_msg}

            # --- 2. SENDER WALLET SETUP ---
            self._logger.info("Loading sender keypair...")
            sender_secret_key_bytes = bytes.fromhex(sender_private_key_hex.strip())
            sender_keypair = Keypair.from_secret_key(sender_secret_key_bytes)
            sender_public_key = sender_keypair.public_key
            self._logger.info(f"Sender wallet loaded: {sender_public_key}")

            # Balance check
            balance = self.client.get_balance(sender_public_key, commitment=Confirmed).value
            self._logger.info(f"Sender balance: {balance / 1_000_000_000} SOL")
            if balance < (amount_sol * 1_000_000_000):
                error_msg = "Insufficient funds for the transaction."
                self._logger.error(error_msg)
                return {"error": error_msg}

            # --- 3. TRANSACTION PREPARATION ---
            self._logger.info("Preparing transaction...")
            lamports = int(amount_sol * 1_000_000_000)

            latest_blockhash_obj = self.client.get_latest_blockhash(commitment=Confirmed).value.blockhash
            self._logger.info(f"Got blockhash: {latest_blockhash_obj}")

            instruction = transfer(
                TransferParams(
                    from_pubkey=sender_public_key,
                    to_pubkey=recipient_pubkey,
                    lamports=lamports,
                )
            )

            # FIX: Convert the Blockhash object to a string, as required by the runtime.
            transaction = Transaction(recent_blockhash=str(latest_blockhash_obj)).add(instruction)
            self._logger.info("Transaction created.")

            # --- 4. SEND AND CONFIRM ---
            self._logger.info("Sending transaction...")
            response = self.client.send_transaction(transaction, sender_keypair)
            tx_signature = response.value
            self._logger.info(f"Transaction sent with signature: {tx_signature}")

            self._logger.info("Waiting for confirmation...")
            self.client.confirm_transaction(tx_signature, commitment=Confirmed)
            self._logger.info("Transaction confirmed!")

            cluster = "devnet" if "devnet" in self.rpc_url else "mainnet-beta"
            url_transaction = f"https://explorer.solana.com/tx/{tx_signature}?cluster={cluster}"

            self._logger.info(f"Success! Transaction link: {url_transaction}")
            return url_transaction

        except Exception as e:
            self._logger.error(f"A critical error occurred: {e}")
            return {"error": str(e)}

