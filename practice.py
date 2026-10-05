def check_signal(price):
    if price > 1950:
        print("Strong buy signal!")
    elif price > 1925:
        print("Weak buy signal")
    else:
        print("No signal")

check_signal(1960)
check_signal(1930)
check_signal(1900)
