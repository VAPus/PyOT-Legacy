def payRent(house):
    player = getPlayerById(house.owner)
    if not player:
        return

    paid = player.removeMoney(house.rent)
    if paid == house.rent:
        house.paid = time.time()
        return

    print "TODO: Player couldn't pay the rent. Need to add it for sale or something!!!"

reg("chargeRent", payRent)