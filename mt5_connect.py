import MetaTrader5 as mt5

# Connect to MT5
if mt5.initialize():
    print("Connected to MT5 successfully!")
else:
    print("Failed to connect, error:", mt5.last_error())

# Print account info
account = mt5.account_info()
print("Account number:", account.login)
print("Balance:", account.balance)
print("Server:", account.server)

# Disconnect
mt5.shutdown()
print("Disconnected from MT5")