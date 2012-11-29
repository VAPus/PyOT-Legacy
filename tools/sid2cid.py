from otbxml2xml import items

while True:
    try:
        num = raw_input("Sid: ")
    except:
        break

    num = int(num)
    print items[num].cid
